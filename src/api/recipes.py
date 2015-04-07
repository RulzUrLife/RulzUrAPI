"""API recipes entrypoints"""
import flask_restful

import peewee

import db.connector
import db.models as models

import utils.helpers
import utils.schemas as schemas


def get_recipe(recipe_id):
    """Get a specific recipe or raise 404 if it does not exists"""

    try:
        return db.models.Recipe.get(db.models.Recipe.id == recipe_id)
    except peewee.DoesNotExist:
        raise utils.helpers.APIException('Recipe not found', 404)


def select_recipes(where_clause):
    """Select recipes according to where_clause"""
    return (models.Recipe
            .select(models.Recipe,
                    models.RecipeIngredients, models.Ingredient,
                    models.RecipeUtensils, models.Utensil)
            .join(models.RecipeIngredients)
            .join(models.Ingredient)
            .switch(models.Recipe)
            .join(models.RecipeUtensils)
            .join(models.Utensil)
            .where(where_clause)
            .aggregate_rows()
            .execute())


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

    if elts_insert:
        model.insert_many(elts_insert, model.name).execute()
        elts_insert = [elt['name'] for elt in elts_insert]
    else:
        elts_insert = []

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
    db_ingrs = get_or_insert(models.Ingredient, ingrs_insert, ingrs_get)

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
        models.Utensil,
        [u for u in utensils if u.get('id') is None],
        [u['id'] for u in utensils if u.get('id') is not None]
    )

def update_recipe(recipe):
    """Update a recipe"""
    delete_old_entries = lambda model, recipe_id: (
        model.delete().where(model.recipe == recipe_id).execute()
    )

    recipe_id = recipe.pop('id')
    ingredients = recipe.pop('ingredients', None)
    utensils = recipe.pop('utensils', None)

    recipe = (models.Recipe
              .update(**recipe)
              .where(models.Recipe.id == recipe_id)
              .returning()
              .execute())
    if ingredients is not None:
        delete_old_entries(models.RecipeIngredients, recipe_id)
        ingredients = ingredients_parsing(ingredients)
        for ingredient in ingredients:
            ingredient['recipe'] = recipe

        models.RecipeIngredients.insert_many(ingredients).execute()
    else:
        ingredients = list(
            models.RecipeIngredients
            .select(models.RecipeIngredients, models.Ingredient)
            .join(models.Ingredient)
            .where(models.RecipeIngredients.recipe == recipe_id)
        )

    if utensils is not None:
        delete_old_entries(models.RecipeUtensils, recipe_id)
        utensils = utensils_parsing(utensils)

        models.RecipeUtensils.insert_many([
            {'recipe': recipe, 'utensil': utensil} for utensil in utensils
        ]).execute()
    else:
        utensils = list(models.Utensil
                        .select()
                        .join(models.RecipeUtensils)
                        .where(models.RecipeUtensils.recipe == recipe_id))

    recipe.ingredients = ingredients
    recipe.utensils = utensils
    return recipe


# pylint: disable=too-few-public-methods
class RecipeListAPI(flask_restful.Resource):
    """/recipes/ endpoint"""

    # pylint: disable=no-self-use
    def get(self):
        """List all recipes"""
        return {'recipes': list(models.Recipe.select().dicts())}

    @db.connector.database.transaction()
    def post(self):
        """Create a recipe"""
        recipe = utils.helpers.raise_or_return(
            utils.schemas.recipe_schema_post
        )
        count = (models.Recipe
                 .select()
                 .where(models.Recipe.name == recipe.get('name'))
                 .count())

        if count:
            raise utils.helpers.APIException('Recipe already exists.', 409)

        # avoid race condition by locking tables
        lock_table(models.Utensil)
        lock_table(models.Ingredient)

        ingredients = ingredients_parsing(recipe['ingredients'])
        utensils = utensils_parsing(recipe['utensils'])
        recipe = models.Recipe.create(**recipe)
        recipe.ingredients = ingredients
        recipe.utensils = utensils

        recipe_utensils = [
            {'recipe': recipe, 'utensil': utensil} for utensil in utensils
        ]

        models.RecipeUtensils.insert_many(recipe_utensils).execute()

        for ingredient in ingredients:
            ingredient['recipe'] = recipe
        models.RecipeIngredients.insert_many(ingredients).execute()
        return {
            'recipe': utils.schemas.recipe_schema.dump(recipe).data
        }, 201


    @db.connector.database.transaction()
    def put(self):
        """Update multiple recipes"""
        # avoid race condition by locking tables

        lock_table(models.Utensil)
        lock_table(models.Ingredient)

        data = utils.helpers.raise_or_return(utils.schemas.recipe_schema_list)
        recipes = [update_recipe(recipe) for recipe in data['recipes']]
        return utils.schemas.recipe_schema_list.dump({'recipes': recipes}).data


# pylint: disable=too-few-public-methods
class RecipeAPI(flask_restful.Resource):
    """/recipes/{recipe_id}/ endpoint"""

    # pylint: disable=no-self-use
    def get(self, recipe_id):
        """Provide the recipe for recipe_id"""
        try:
            recipe = next(select_recipes(models.Recipe.id == recipe_id))
        except StopIteration:
            raise utils.helpers.APIException('Recipe not found', 404)

        recipe, _ = schemas.recipe_schema.dump(recipe)
        return {'recipe': recipe}

# pylint: disable=too-few-public-methods
class RecipeIngredientListAPI(flask_restful.Resource):
    """/recipes/{recipe_id}/ingredients endpoint"""

    # pylint: disable=no-self-use
    def get(self, recipe_id):
        """List all the ingredients for recipe_id"""
        get_recipe(recipe_id)

        ingredients_query = (
            models.RecipeIngredients
            .select(
                models.RecipeIngredients.quantity,
                models.RecipeIngredients.measurement,
                models.Ingredient
            )
            .join(models.Ingredient)
            .where(models.RecipeIngredients.recipe == recipe_id)
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
            models.Utensil
            .select()
            .join(models.RecipeUtensils)
            .where(models.RecipeUtensils.recipe == recipe_id)
            .dicts())

        return {'utensils': list(utensils_query)}

