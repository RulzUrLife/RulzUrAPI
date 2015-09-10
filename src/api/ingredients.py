"""API ingredients entrypoints"""
import flask

import api.recipes
import db.models as models
import db.connector
import utils.helpers
import utils.schemas as schemas

import peewee

blueprint = flask.Blueprint('ingredients', __name__)

def get_ingredient(ingredient_id):
    """Get a specific ingredient or raise 404 if it does not exists"""
    try:
        return models.Ingredient.get(models.Ingredient.id == ingredient_id)
    except peewee.DoesNotExist:
        raise utils.helpers.APIException('Ingredient not found', 404)


def update_ingredient(ingredient):
    """Update an ingredient and return it"""
    ingredient_id = ingredient.pop('id')

    try:
        return (models.Ingredient
                .update(**ingredient)
                .where(models.Ingredient.id == ingredient_id)
                .returning()
                .dicts())
    except peewee.DoesNotExist:
        raise utils.helpers.APIException('Ingredient not found', 404)


@blueprint.route('/')
def ingredients_get():
    """List all ingredients"""
    return {'ingredients': list(models.Ingredient.select().dicts())}


@blueprint.route('/', methods=['POST'])
@db.connector.database.transaction()
def ingredients_post():
    """Create an ingredient"""
    schema = schemas.ingredient_schema_post
    ingredient = utils.helpers.raise_or_return(schema)
    try:
        ingredient = models.Ingredient.create(**ingredient)
    except peewee.IntegrityError:
        raise utils.helpers.APIException('Ingredient already exists', 409)

    ingredient, _ = schemas.ingredient_schema.dump(ingredient)
    return {'ingredient': ingredient}, 201


@blueprint.route('/', methods=['PUT'])
@db.connector.database.transaction()
def ingredients_put():
    """Update multiple ingredients"""

    data = utils.helpers.raise_or_return(schemas.ingredient_schema_list)

    ingredients = []
    for ingredient in data['ingredients']:
        try:
            ingredients.append(update_ingredient(ingredient))
        except utils.helpers.APIException:
            pass

    return {'ingredients': ingredients}


@blueprint.route('/<int:ingredient_id>/')
def ingredient_get(ingredient_id):
    """Provide the ingredient for ingredient_id"""
    ingredient = get_ingredient(ingredient_id)
    ingredient, _ = schemas.ingredient_schema.dump(ingredient)
    return {'ingredient': ingredient}


@blueprint.route('/<int:ingredient_id>/', methods=['PUT'])
@db.connector.database.transaction()
def ingredient_put(ingredient_id):
    """Update the ingredient for ingredient_id"""

    schema = schemas.ingredient_schema_put
    ingredient = utils.helpers.raise_or_return(schema)
    ingredient['id'] = ingredient_id
    return {'ingredient': update_ingredient(ingredient)}


@blueprint.route('/<int:ingredient_id>/recipes/')
def get(ingredient_id):
    """List all the recipes for ingredient_id"""
    get_ingredient(ingredient_id)
    where_clause = models.RecipeIngredients.ingredient == ingredient_id

    recipes = list(api.recipes.select_recipes(where_clause))
    recipes, _ = schemas.recipe_schema_list.dump({'recipes': recipes})
    return recipes


