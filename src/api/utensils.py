"""API utensils entrypoints"""

import flask_restful
import flask_restful.reqparse
import flask
import db.models
import db.connector
import utils.helpers
import utils.schemas

import peewee

def get_utensil(utensil_id):
    """Get a specific utensil or raise 404 if it does not exists"""
    try:
        return db.models.Utensil.get(db.models.Utensil.id == utensil_id)
    except peewee.DoesNotExist:
        flask_restful.abort(404)

class UtensilListAPI(flask_restful.Resource):
    """/utensils/ endpoint"""

    # pylint: disable=no-self-use
    def get(self):
        """List all utensils"""
        return {'utensils': list(db.models.Utensil.select().dicts())}

    @db.connector.database.transaction()
    def post(self):
        """Create an utensil"""
        utensil = utils.helpers.parse_args(
            utils.schemas.UtensilPostSchema(), flask.request.json
        )

        try:
            utensil = db.models.Utensil.create(**utensil)
        except peewee.IntegrityError:
            flask_restful.abort(409, message='Utensil already exists')
        return (
            {'utensil': utils.schemas.UtensilSchema().dump(utensil).data}, 201
        )

    @db.connector.database.transaction()
    def put(self):
        """Update multiple utensils"""
        utensils = []
        data = utils.helpers.parse_args(
            utils.schemas.UtensilListSchema(), flask.request.json
        )

        for utensil in data['utensils']:
            utensil_id = utensil.pop('id')
            try:
                utensils.append(
                    next(db.models.Utensil
                         .update(returning=True, **utensil)
                         .where(db.models.Utensil.id == utensil_id)
                         .dicts()
                         .execute())
                )

            except StopIteration:
                pass

        return {'utensils': utensils}

class UtensilAPI(flask_restful.Resource):
    """/utensils/{utensil_id}/ endpoint"""

    # pylint: disable=no-self-use
    def get(self, utensil_id):
        """Provide the utensil for utensil_id"""
        return {
            'utensil': utils.schemas.UtensilSchema().dump(
                get_utensil(utensil_id)
            ).data
        }

    @db.connector.database.transaction()
    def put(self, utensil_id):
        """Update the utensil for utensil_id"""

        utensil = utils.helpers.parse_args(
            utils.schemas.UtensilSchema(exclude=('id',)), flask.request.json
        )

        try:
            return next(db.models.Utensil
                        .update(returning=True, **utensil)
                        .where(db.models.Utensil.id == utensil_id)
                        .dicts()
                        .execute())

        except StopIteration:
            flask_restful.abort(404)


# pylint: disable=too-few-public-methods
class UtensilRecipeListAPI(flask_restful.Resource):
    """/utensils/{utensil_id}/recipes endpoint"""

    # pylint: disable=no-self-use
    def get(self, utensil_id):
        """List all the recipes for utensil_id"""
        get_utensil(utensil_id)

        recipes_query = (
            db.models.Recipe
            .select()
            .join(db.models.RecipeUtensils)
            .where(db.models.RecipeUtensils.utensil == utensil_id)
            .dicts())

        return {'recipes': list(recipes_query)}

