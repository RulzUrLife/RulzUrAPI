"""API utensils entrypoints"""

import flask_restful
import flask_restful.reqparse
import db.models
import db.connector
import utils.helpers

import peewee

def get_utensil(utensil_id):
    """Get a specific utensil or raise 404 if it does not exists"""
    try:
        return db.models.Utensil.get(db.models.Utensil.id == utensil_id)
    except peewee.DoesNotExist:
        flask_restful.abort(404)

class UtensilListAPI(flask_restful.Resource):
    """/utensils/ endpoint"""

    def __init__(self):
        self.post_reqparse = flask_restful.reqparse.RequestParser()
        self.post_reqparse.add_argument(
            'name', type=str, required=True,
            help='No utensil name provided', location='json'
        )

        self.put_reqparse = flask_restful.reqparse.RequestParser()
        self.put_reqparse.add_argument(
            'utensils', type=list, required=True, location='json'
        )

        self.put_reqparse_utensil = flask_restful.reqparse.RequestParser()
        self.put_reqparse_utensil.add_argument(
            'id', type=int, required=True, location='json',
            help='id field not provided for all values'
        )
        self.put_reqparse_utensil.add_argument(
            'name', type=str, location='json'
        )


        super(UtensilListAPI, self).__init__()

    # pylint: disable=no-self-use
    def get(self):
        """List all utensils"""
        return {'utensils': list(db.models.Utensil.select().dicts())}

    def post(self):
        """Create an utensil"""
        args = self.post_reqparse.parse_args()
        utensil = db.models.Utensil.create(name=args.get('name'))
        return {'utensil': utensil.to_dict()}, 201

    @db.connector.database.transaction()
    def put(self):
        """Update multiple utensils"""
        args = self.put_reqparse.parse_args()
        utensils = []
        nested_request = utils.helpers.NestedRequest()
        for utensil in args.get('utensils'):
            nested_request.nested_json = utensil
            utensil = self.put_reqparse_utensil.parse_args(nested_request)
            utensils += (
                utils.helpers.optimized_update(db.models.Utensil, utensil)
                .execute()
            )

        return {'utensils': utensils}

class UtensilAPI(flask_restful.Resource):
    """/utensils/{utensil_id}/ endpoint"""

    def __init__(self):
        self.put_reqparse = flask_restful.reqparse.RequestParser()
        self.put_reqparse.add_argument('name', type=str, location='json')
        super(UtensilAPI, self).__init__()

    # pylint: disable=no-self-use
    def get(self, utensil_id):
        """Provide the utensil for utensil_id"""
        return {'utensil': get_utensil(utensil_id).to_dict()}

    @db.connector.database.transaction()
    def put(self, utensil_id):
        """Update the utensil for utensil_id"""
        args = (db.models.Utensil, self.put_reqparse.parse_args(), utensil_id)
        try:
            return {
                'utensil': (utils.helpers.optimized_update(*args)
                            .execute().next())
            }
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

