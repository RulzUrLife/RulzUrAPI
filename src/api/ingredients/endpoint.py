"""API ingredients entrypoints"""
import flask

import api.recipes
import db.models as models
import db
import utils.exceptions as exc
import utils.helpers
import utils.schemas as schemas

import peewee

blueprint = flask.Blueprint('ingredients', __name__)

def get_ingredient(ingredient_id):
    """Get a specific ingredient or raise 404 if it does not exists"""
    try:
        return models.Ingredient.get(models.Ingredient.id == ingredient_id)
    except peewee.DoesNotExist:
        raise exc.APIException('ingredient not found', 404)


def update_ingredient(ingredient):
    """Update an ingredient and return it"""
    ingredient_id = ingredient.pop('id')

    try:
        return (models.Ingredient
                .update(**ingredient)
                .where(models.Ingredient.id == ingredient_id)
                .returning()
                .execute()
                .next())
    except StopIteration:
        raise exc.APIException('ingredient not found', 404)


@blueprint.route('')
def ingredients_get():
    """List all ingredients"""
    ingredients = models.Ingredient.select().dicts()
    return schemas.ingredient.dump(ingredients, many=True).data


@blueprint.route('', methods=['POST'])
@db.database.transaction()
def ingredients_post():
    """Create an ingredient"""
    ingredient = utils.helpers.raise_or_return(schemas.ingredient.post)
    try:
        ingredient = models.Ingredient.create(**ingredient)
    except peewee.IntegrityError:
        raise exc.APIException('ingredient already exists', 409)

    return schemas.ingredient.dump(ingredient).data, 201


@blueprint.route('', methods=['PUT'])
@db.database.transaction()
def ingredients_put():
    """Update multiple ingredients"""
    ingredients = utils.helpers.raise_or_return(schemas.ingredient.put, True)
    ingredients = [update_ingredient(ingredient) for ingredient in ingredients]
    return schemas.ingredient.dump(ingredients, many=True).data


@blueprint.route('/<int:ingredient_id>')
def ingredient_get(ingredient_id):
    """Provide the ingredient for ingredient_id"""
    ingredient = get_ingredient(ingredient_id)
    return schemas.ingredient.dump(ingredient).data


@blueprint.route('/<int:ingredient_id>', methods=['PUT'])
@db.database.transaction()
def ingredient_put(ingredient_id):
    """Update the ingredient for ingredient_id"""
    ingredient = utils.helpers.raise_or_return(schemas.ingredient.put)
    if not ingredient:
        raise exc.APIException('no data provided for update')

    ingredient['id'] = ingredient_id
    return schemas.ingredient.dump(update_ingredient(ingredient)).data


@blueprint.route('/<int:ingredient_id>/recipes')
def recipes_get(ingredient_id):
    """List all the recipes for ingredient_id"""
    get_ingredient(ingredient_id)
    where_clause = models.RecipeIngredients.ingredient == ingredient_id

    recipes = list(api.recipes.select_recipes(where_clause))
    recipes, _ = schemas.recipe_schema_list.dump({'recipes': recipes})
    return recipes
