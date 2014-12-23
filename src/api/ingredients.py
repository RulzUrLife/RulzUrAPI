"""API ingredients entrypoints"""

import flask_restful
import db.models

import peewee

def get_ingredient(ingredient_id):
    """Get a specific ingredient or raise 404 if it does not exists"""
    try:
        return db.models.Ingredient.get(
            db.models.Ingredient.id == ingredient_id
        )
    except peewee.DoesNotExist:
        flask_restful.abort(404)

# pylint: disable=too-few-public-methods
class IngredientListAPI(flask_restful.Resource):
    """/ingredients/ endpoint"""

    # pylint: disable=no-self-use
    def get(self):
        """List all ingredients"""
        return {'ingredients': list(db.models.Ingredient.select().dicts())}

# pylint: disable=too-few-public-methods
class IngredientAPI(flask_restful.Resource):
    """/ingredients/{ingredient_id}/ endpoint"""

    # pylint: disable=no-self-use
    def get(self, ingredient_id):
        """Provide the ingredient for ingredient_id"""
        return {'ingredient': get_ingredient(ingredient_id).to_dict()}

# pylint: disable=too-few-public-methods
class IngredientRecipeListAPI(flask_restful.Resource):
    """/ingredients/{ingredient_id}/recipes"""

    # pylint: disable=no-self-use
    def get(self, ingredient_id):
        """List all the recipes for ingredient_id"""

        get_ingredient(ingredient_id)

        recipes_query = (
            db.models.Recipe
            .select()
            .join(db.models.RecipeIngredients)
            .where(db.models.RecipeIngredients.ingredient == ingredient_id)
            .dicts())

        return {'recipes': list(recipes_query)}

