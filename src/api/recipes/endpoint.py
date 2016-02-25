"""API recipes entrypoints"""
import flask
import peewee

import db
import db.models as models
import db.utils

import utils.helpers as helpers
import utils.schemas as schemas
import utils.exceptions as exc

blueprint = flask.Blueprint('recipes', __name__, template_folder='templates')

def select_recipes(where_clause=None):
    """Select recipes according to where_clause if provided"""

    recipes = (
        models.Recipe
        .select(models.Recipe, models.RecipeIngredients, models.Ingredient,
                models.RecipeUtensils, models.Utensil)
        .join(models.RecipeIngredients, peewee.JOIN.LEFT_OUTER)
        .join(models.Ingredient, peewee.JOIN.LEFT_OUTER)
        .switch(models.Recipe)
        .join(models.RecipeUtensils, peewee.JOIN.LEFT_OUTER)
        .join(models.Utensil, peewee.JOIN.LEFT_OUTER)
        .switch(models.Recipe)
    )
    if where_clause:
        recipes = recipes.where(where_clause)

    return recipes.aggregate_rows().execute()


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
              .returning())

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


@blueprint.route('')
@helpers.template({'text/html': 'recipes.html'})
def recipes_get():
    """List all recipes"""
    recipes = select_recipes()

    return schemas.recipe.dump(recipes, many=True).data


@blueprint.route('', methods=['POST'])
@db.utils.lock(models.Utensil, models.Ingredient)
def recipes_post():
    """Create a recipe"""
    recipe = helpers.raise_or_return(schemas.recipe.post)
    ret_id = lambda obj, key: {'recipe': recipe.id, key: obj['id']}
    ret_recipe_ingr = lambda ingr: helpers.dict_merge(
        ret_id(ingr, 'ingredient'),
        {'quantity': ingr['quantity'], 'measurement': ingr['measurement']}
    )

    ingredients = recipe.pop('ingredients')
    utensils = recipe.pop('utensils')
    try:
        recipe = models.Recipe.create(**recipe)
    except peewee.IntegrityError:
        raise exc.APIException('recipe already exists', 409)

    recipe.ingredients = ingredients
    recipe.utensils = utensils

    if utensils:
        recipe_utensils = [ret_id(utensil, 'utensil') for utensil in utensils]
        models.RecipeUtensils.insert_many(recipe_utensils).execute()

    if ingredients:
        recipe_ingrs = [ret_recipe_ingr(ingr) for ingr in ingredients]
        models.RecipeIngredients.insert_many(recipe_ingrs).execute()

    return schemas.recipe.dump(recipe).data, 201


@blueprint.route('', methods=['PUT'])
@db.utils.lock(models.Utensil, models.Ingredient)
def recipes_put():
    """Update multiple recipes"""

    data = helpers.raise_or_return(schemas.recipe.put, True)
    recipes = [update_recipe(recipe) for recipe in data['recipes']]
    return schemas.recipe_schema_list.dump({'recipes': recipes}).data


@blueprint.route('/<int:recipe_id>')
@helpers.template({'text/html': 'recipe.html'})
def recipe_get(recipe_id):
    """Provide the recipe for recipe_id"""
    try:
        recipe = next(select_recipes(models.Recipe.id == recipe_id))
    except StopIteration:
        raise exc.APIException('recipe not found', 404)

    return schemas.recipe.dump(recipe).data


@blueprint.route('/<int:recipe_id>', methods=['PUT'])
@db.database.atomic()
def recipe_put(recipe_id):
    recipe = helpers.raise_or_return(schemas.recipe.put)
    if not recipe:
        raise exc.APIException('no data provided for update')


@blueprint.route('/<int:recipe_id>/ingredients/')
def recipe_ingredients_get(recipe_id):
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

@blueprint.route('/<int:recipe_id>/utensils/')
def recipe_utensils_get(recipe_id):
    """List all the utensils for recipe_id"""
    get_recipe(recipe_id)

    utensils_query = (
        models.Utensil
        .select()
        .join(models.RecipeUtensils)
        .where(models.RecipeUtensils.recipe == recipe_id)
        .dicts())

    return {'utensils': list(utensils_query)}

