"""API utensils entrypoints"""
import flask

import api.recipes
import db.models as models
import db
import utils.helpers
import utils.schemas as schemas
import utils.exceptions as exc

import peewee
blueprint = flask.Blueprint('utensils', __name__, template_folder='templates')

def get_utensil(utensil_id):
    """Get a specific utensil or raise 404 if it does not exists"""
    try:
        return models.Utensil.get(models.Utensil.id == utensil_id)
    except peewee.DoesNotExist:
        raise exc.APIException('utensil not found', 404)


def update_utensil(utensil):
    """Update an utensil and return it"""
    utensil_id = utensil.pop('id')

    try:
        return (models.Utensil
                .update(**utensil)
                .where(models.Utensil.id == utensil_id)
                .returning()
                .execute()
                .next())
    except StopIteration:
        raise exc.APIException('utensil not found', 404)


@blueprint.route('')
@utils.helpers.template({'text/html': 'utensils.html'})
def utensils_get():
    """List all utensils"""
    utensils = models.Utensil.select().dicts()
    return schemas.utensil.dump(utensils, many=True).data


@blueprint.route('', methods=['POST'])
@db.database.transaction()
def utensils_post():
    """Create an utensil"""
    utensil = utils.helpers.raise_or_return(schemas.utensil.post)
    try:
        utensil = models.Utensil.create(**utensil)
    except peewee.IntegrityError:
        raise exc.APIException('utensil already exists', 409)

    return schemas.utensil.dump(utensil).data, 201


@blueprint.route('', methods=['PUT'])
@db.database.transaction()
def utensils_put():
    """Update multiple utensils"""
    utensils = utils.helpers.raise_or_return(schemas.utensil.put, True)
    utensils = [update_utensil(utensil) for utensil in utensils]

    return schemas.utensil.dump(utensils, many=True).data


@blueprint.route('/<int:utensil_id>')
def utensil_get(utensil_id):
    """Provide the utensil for utensil_id"""
    utensil = get_utensil(utensil_id)
    return schemas.utensil.dump(utensil).data


@blueprint.route('/<int:utensil_id>', methods=['PUT'])
@db.database.transaction()
def utensil_put(utensil_id):
    """Update the utensil for utensil_id"""
    utensil = utils.helpers.raise_or_return(schemas.utensil.put)
    if not utensil:
        raise exc.APIException('no data provided for update')

    utensil['id'] = utensil_id
    return schemas.utensil.dump(update_utensil(utensil)).data


@blueprint.route('/<int:utensil_id>/recipes')
@db.database.transaction()
def recipe_get(utensil_id):
    """List all the recipes for utensil_id"""
    get_utensil(utensil_id)
    where_clause = models.RecipeUtensils.utensil == utensil_id

    recipes = list(api.recipes.select_recipes(where_clause))
    recipes, _ = schemas.recipe_schema_list.dump({'recipes': recipes})
    return recipes

