"""API utensils entrypoints"""
import flask

import api.recipes
import db.models
import db.connector
import utils.helpers
import utils.schemas as schemas

import peewee

blueprint = flask.Blueprint('utensils', __name__)

def get_utensil(utensil_id):
    """Get a specific utensil or raise 404 if it does not exists"""
    try:
        return db.models.Utensil.get(db.models.Utensil.id == utensil_id)
    except peewee.DoesNotExist:
        raise utils.helpers.APIException('Utensil not found', 404)


def update_utensil(utensil):
    """Update an utensil and return it"""
    utensil_id = utensil.pop('id')

    try:
        return (db.models.Utensil
                .update(**utensil)
                .where(db.models.Utensil.id == utensil_id)
                .returning()
                .dicts()
                .execute())
    except peewee.DoesNotExist:
        raise utils.helpers.APIException('Utensil not found', 404)


@blueprint.route('/')
@utils.helpers.template({'text/html': 'utensils.html'})
def utensils_get():
    """List all utensils"""
    return {'utensils': list(db.models.Utensil.select().dicts())}


@blueprint.route('/', methods=['POST'])
@db.connector.database.transaction()
def utensils_post():
    """Create an utensil"""
    utensil = utils.helpers.raise_or_return(schemas.utensil_schema_post)

    try:
        utensil = db.models.Utensil.create(**utensil)
    except peewee.IntegrityError:
        raise utils.helpers.APIException('Utensil already exists', 409)

    utensil, _ = schemas.utensil_schema.dump(utensil)
    return {'utensil': utensil}, 201


@blueprint.route('/', methods=['PUT'])
@db.connector.database.transaction()
def utensils_put():
    """Update multiple utensils"""

    data = utils.helpers.raise_or_return(schemas.utensil_schema_list)

    utensils = []
    for utensil in data['utensils']:
        try:
            utensils.append(update_utensil(utensil))
        except utils.helpers.APIException:
            pass

    return {'utensils': utensils}


@blueprint.route('/<int:utensil_id>/')
def utensil_get(utensil_id):
    """Provide the utensil for utensil_id"""
    utensil, _ = schemas.utensil_schema.dump(get_utensil(utensil_id))
    return {'utensil': utensil}


@blueprint.route('/<int:utensil_id>/', methods=['PUT'])
@db.connector.database.transaction()
def utensil_put(utensil_id):
    """Update the utensil for utensil_id"""

    utensil = utils.helpers.raise_or_return(schemas.utensil_schema_put)
    utensil['id'] = utensil_id
    return {'utensil': update_utensil(utensil)}


@blueprint.route('/<int:utensil_id>/recipes/')
@db.connector.database.transaction()
def recipe_get(utensil_id):
    """List all the recipes for utensil_id"""
    get_utensil(utensil_id)
    where_clause = db.models.RecipeUtensils.utensil == utensil_id

    recipes = list(api.recipes.select_recipes(where_clause))
    recipes, _ = schemas.recipe_schema_list.dump({'recipes': recipes})
    return recipes

