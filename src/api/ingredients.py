"""API ingredients entrypoints"""

import flask

import db.connector
import db.models

import peewee

# disable warning here due to Flask initialisation
# pylint: disable=invalid-name
ingredients_blueprint = flask.Blueprint('ingredients', __name__)

def get_ingredient(ingredient_id):
    """Get a specific ingredient or raise 404 if it does not exists"""
    try:
        return db.models.Ingredient.get(
            db.models.Ingredient.id == ingredient_id
        )
    except peewee.DoesNotExist:
        flask.abort(404)


@ingredients_blueprint.route('/', defaults={'ingredient_id': None})
@ingredients_blueprint.route('/<int:ingredient_id>')
def ingredients(ingredient_id):
    """List all ingredients or a specific one

    If optional argument ingredient_id is given, this function return the specific
    ingredient, otherwise it returns the list of all ingredients
    """

    if ingredient_id is None:
        result = {
            'ingredients': list(db.models.Ingredient.select().dicts())
        }
    else:
        result = {
            'ingredient': get_ingredient(ingredient_id).to_dict()
        }

    return flask.jsonify(result)

@ingredients_blueprint.route('/<int:ingredient_id>/recipes')
def recipes(ingredient_id):
    """List all the recipes of a specific ingredient"""

    get_ingredient(ingredient_id)

    recipes_query = (
        db.models.Recipe
        .select()
        .join(db.models.RecipeIngredients)
        .where(db.models.RecipeIngredients.ingredient == ingredient_id)
        .dicts())

    return flask.jsonify({'recipes': list(recipes_query)})

