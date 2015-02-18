"""API recipes entrypoints"""
import flask_restful
import flask

import peewee

import db.connector
import db.models

import utils.helpers


def get_recipe(recipe_id):
    """Get a specific recipe or raise 404 if it does not exists"""
    try:
        return db.models.Recipe.get(db.models.Recipe.id == recipe_id)
    except peewee.DoesNotExist:
        raise utils.helpers.APIException('Recipe not found', 404)


def lock_table(model):
    """Lock table to avoid race conditions"""
    model_entity = utils.helpers.model_entity(model)
    lock_request = (
        'LOCK TABLE %s IN SHARE ROW EXCLUSIVE MODE' % model_entity
    )

    #protect the database table against race condition
    db.connector.database.execute_sql(lock_request)


def get_or_insert(model, elts_insert, elts_get):
    """Get the elements from a model or create them if they not exist"""

    model.insert_many(elts_insert, model.name).execute()

    elts_insert = [elt['name'] for elt in elts_insert]

    list_elts = lambda x: list(model.select().where(x))
    if elts_get and elts_insert:
        return list_elts((model.id << elts_get) | (model.name << elts_insert))
    elif elts_insert:
        return list_elts(model.name << elts_insert)
    elif elts_get:
        return list_elts(model.id << elts_get)
    else:
        return []


def ingredients_parsing(ingrs):
    """Parse the ingredients before calling get_or_insert"""

    ingrs_insert, ingrs_get = [], []
    ingrs_id, ingrs_name = {}, {}

    for ingr in ingrs:
        ingr_id = ingr.pop('id', None)
        ingr_name = ingr.pop('name', None)

        if ingr_id:
            ingrs_get.append(ingr_id)
            ingrs_id[ingr_id] = ingr
        if ingr_name:
            ingrs_insert.append({'name': ingr_name})
            ingrs_name[ingr_name] = ingr

    db_ingrs = get_or_insert(db.models.Ingredient, ingrs_insert, ingrs_get)

    # wraps again the ingredients into recipe_ingredients dict
    for ingr in db_ingrs:
        ingr_id = ingr.id
        ingr_name = ingr.name

        ingr_tmp = ingrs_id.get(ingr_id) or ingrs_name.get(ingr_name)
        ingr_tmp['ingredient'] = ingr

    return ingrs

def utensils_parsing(utensils):
    """Parse the utensils before calling get_or_insert"""
    return get_or_insert(
        db.models.Utensil,
        [u for u in utensils if u.get('id') is None],
        [u['id'] for u in utensils if u.get('id') is not None]
    )

def update_recipe(recipe):
    """Update a recipe"""
    recipe_id = recipe.pop('id')
    ingredients = recipe.pop('ingredients', None)
    utensils = recipe.pop('utensils', None)
    recipe = (db.models.Recipe
              .update(**recipe)
              .where(db.models.Recipe.id == recipe_id)
              .returning()
              .execute())
    if ingredients is not None:
        (db.models.RecipeIngredients
         .delete()
         .where(db.models.RecipeIngredients.recipe == recipe_id)
         .execute())
        ingredients = ingredients_parsing(ingredients)
        for ingredient in ingredients:
            ingredient['recipe'] = recipe

        db.models.RecipeIngredients.insert_many(ingredients).execute()
    else:
        ingredients = list(
            db.models.RecipeIngredients
            .select(db.models.RecipeIngredients, db.models.Ingredient)
            .join(db.models.Ingredient)
            .where(db.models.RecipeIngredients.recipe == recipe_id)
        )

    if utensils is not None:
        (db.models.RecipeUtensils
         .delete()
         .where(db.models.RecipeUtensils.recipe == recipe_id)
         .execute())

        utensils = utensils_parsing(utensils)

        db.models.RecipeUtensils.insert_many([
            {'recipe': recipe, 'utensil': utensil} for utensil in utensils
        ]).execute()
    else:
        utensils = list(db.models.Utensil
                        .select()
                        .join(db.models.RecipeUtensils)
                        .where(db.models.RecipeUtensils.recipe == recipe_id))

    recipe.ingredients = ingredients
    recipe.utensils = utensils
    return recipe


# pylint: disable=too-few-public-methods
class RecipeListAPI(flask_restful.Resource):
    """/recipes/ endpoint"""

    # pylint: disable=no-self-use
    def get(self):
        """List all recipes"""
        return {'recipes': list(db.models.Recipe.select().dicts())}

    @db.connector.database.transaction()
    def post(self):
        """Create a recipe"""
        # avoid race condition by locking tables
        lock_table(db.models.Utensil)
        lock_table(db.models.Ingredient)

        recipe = utils.helpers.raise_or_return(
            utils.schemas.recipe_schema_post, flask.request.json
        )
        count = (db.models.Recipe
                 .select()
                 .where(db.models.Recipe.name == recipe.get('name'))
                 .count())

        if count:
            raise utils.helpers.APIException('Recipe already exists.', 409)

        ingredients = ingredients_parsing(recipe['ingredients'])
        utensils = utensils_parsing(recipe['utensils'])

        recipe = db.models.Recipe.create(**recipe)
        recipe.ingredients = ingredients
        recipe.utensils = utensils

        recipe_utensils = [
            {'recipe': recipe, 'utensil': utensil} for utensil in utensils
        ]

        db.models.RecipeUtensils.insert_many(recipe_utensils).execute()

        for ingredient in ingredients:
            ingredient['recipe'] = recipe
        db.models.RecipeIngredients.insert_many(ingredients).execute()
        return {
            'recipe': utils.schemas.RecipeSchema().dump(recipe).data
        }, 201


    @db.connector.database.transaction()
    def put(self):
        """Update multiple recipes"""
        # avoid race condition by locking tables

        lock_table(db.models.Utensil)
        lock_table(db.models.Ingredient)

        data = utils.helpers.raise_or_return(
            utils.schemas.recipe_schema_list, flask.request.json
        )
        recipes = [update_recipe(recipe) for recipe in data['recipes']]

        return utils.schemas.recipe_schema_list.dump({'recipes': recipes}).data


# pylint: disable=too-few-public-methods
class RecipeAPI(flask_restful.Resource):
    """/recipes/{recipe_id}/ endpoint"""

    # pylint: disable=no-self-use
    def get(self, recipe_id):
        """Provide the recipe for recipe_id"""
        return {'recipe': get_recipe(recipe_id).to_dict()}

# pylint: disable=too-few-public-methods
class RecipeIngredientListAPI(flask_restful.Resource):
    """/recipes/{recipe_id}/ingredients endpoint"""

    # pylint: disable=no-self-use
    def get(self, recipe_id):
        """List all the ingredients for recipe_id"""
        get_recipe(recipe_id)

        ingredients_query = (
            db.models.RecipeIngredients
            .select(
                db.models.RecipeIngredients.quantity,
                db.models.RecipeIngredients.measurement,
                db.models.Ingredient
            )
            .join(db.models.Ingredient)
            .where(db.models.RecipeIngredients.recipe == recipe_id)
            .dicts())

        return {'ingredients': list(ingredients_query)}

# pylint: disable=too-few-public-methods
class RecipeUtensilListAPI(flask_restful.Resource):
    """/recipes/{recipe_id}/utensils endpoint"""

    # pylint: disable=no-self-use
    def get(self, recipe_id):
        """List all the utensils for recipe_id"""
        get_recipe(recipe_id)

        utensils_query = (
            db.models.Utensil
            .select()
            .join(db.models.RecipeUtensils)
            .where(db.models.RecipeUtensils.recipe == recipe_id)
            .dicts())

        return {'utensils': list(utensils_query)}

