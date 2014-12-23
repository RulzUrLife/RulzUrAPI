"""API utensils entrypoints"""

import flask_restful
import db.models

import peewee

def get_utensil(utensil_id):
    """Get a specific utensil or raise 404 if it does not exists"""
    try:
        return db.models.Utensil.get(db.models.Utensil.id == utensil_id)
    except peewee.DoesNotExist:
        flask_restful.abort(404)

# pylint: disable=too-few-public-methods
class UtensilListAPI(flask_restful.Resource):
    """/utensils/ endpoint"""

    # pylint: disable=no-self-use
    def get(self):
        """List all utensils"""
        return {'utensils': list(db.models.Utensil.select().dicts())}

# pylint: disable=too-few-public-methods
class UtensilAPI(flask_restful.Resource):
    """/utensils/{utensil_id}/ endpoint"""

    # pylint: disable=no-self-use
    def get(self, utensil_id):
        """Provide the utensil for utensil_id"""
        return {'utensil': get_utensil(utensil_id).to_dict()}

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

