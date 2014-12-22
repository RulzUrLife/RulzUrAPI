"""API utensils entrypoints"""

import flask

import db.connector
import db.models

import peewee

# disable warning here due to Flask initialisation
# pylint: disable=invalid-name
utensils_blueprint = flask.Blueprint('utensils', __name__)

def get_utensil(utensil_id):
    """Get a specific utensil or raise 404 if it does not exists"""
    try:
        return db.models.Utensil.get(
            db.models.Utensil.id == utensil_id
        )
    except peewee.DoesNotExist:
        flask.abort(404)


@utensils_blueprint.route('/', defaults={'utensil_id': None})
@utensils_blueprint.route('/<int:utensil_id>')
def utensils(utensil_id):
    """List all utensils or a specific one

    If optional argument utensil_id is given, this function return the specific
    utensil, otherwise it returns the list of all utensils
    """

    if utensil_id is None:
        result = {
            'utensils': list(db.models.Utensil.select().dicts())
        }
    else:
        result = {
            'utensil': get_utensil(utensil_id).to_dict()
        }

    return flask.jsonify(result)

@utensils_blueprint.route('/<int:utensil_id>/recipes')
def recipes(utensil_id):
    """List all the recipes of a specific utensil"""

    get_utensil(utensil_id)

    recipes_query = (
        db.models.Recipe
        .select()
        .join(db.models.RecipeUtensils)
        .where(db.models.RecipeUtensils.utensil == utensil_id)
        .dicts())

    return flask.jsonify({'recipes': list(recipes_query)})

