"""API recipes entrypoints"""

import flask

import db.connector
import db.models

import peewee

# disable warning here due to Flask initialisation
# pylint: disable=invalid-name
recipes_blueprint = flask.Blueprint('recipes', __name__)

def get_recipe(recipe_id):
    """Get a specific recipe or raise 404 if it does not exists"""
    try:
        return db.models.Recipe.get(db.models.Recipe.id == recipe_id)
    except peewee.DoesNotExist:
        flask.abort(404)


@recipes_blueprint.route('/', defaults={'recipe_id': None})
@recipes_blueprint.route('/<int:recipe_id>')
def recipes(recipe_id):
    """List all recipes or a specific one

    If optional argument recipe_id is given, this function return the specific
    recipe, otherwise it returns the list of all recipes
    """
    if recipe_id is None:
        result = {
            'recipes': list(db.models.Recipe.select().dicts())
        }
    else:
        result = {
            'recipe': get_recipe(recipe_id).to_dict()
        }

    return flask.jsonify(result)

@recipes_blueprint.route('/<int:recipe_id>/ingredients')
def ingredients(recipe_id):
    """List all the ingredients of a specific recipe"""

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

    return flask.jsonify({'ingredients': list(ingredients_query)})

@recipes_blueprint.route('/<int:recipe_id>/utensils')
def utensils(recipe_id):
    """List all the utensils of a specific recipe"""

    get_recipe(recipe_id)

    utensils_query = (
        db.models.Utensil
        .select()
        .join(db.models.RecipeUtensils)
        .where(db.models.RecipeUtensils.recipe == recipe_id)
        .dicts())

    return flask.jsonify({'utensils': list(utensils_query)})

