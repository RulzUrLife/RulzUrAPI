"""API recipes entrypoints"""

import flask_restful

import db.connector
import db.models

import peewee

def get_recipe(recipe_id):
    """Get a specific recipe or raise 404 if it does not exists"""
    try:
        return db.models.Recipe.get(db.models.Recipe.id == recipe_id)
    except peewee.DoesNotExist:
        flask_restful.abort(404)

# pylint: disable=too-few-public-methods
class RecipeListAPI(flask_restful.Resource):
    """/recipes/ endpoint"""

    # pylint: disable=no-self-use
    def get(self):
        """List all recipes"""
        return {'recipes': list(db.models.Recipe.select().dicts())}

# pylint: disable=too-few-public-methods
class RecipeAPI(flask_restful.Resource):
    """/recipes/{recipe_id}/ endpoint"""

    # pylint: disable=no-self-use
    def get(self, recipe_id):
        """Provide the recipe for recipe_id"""
        return {'recipe': get_recipe(recipe_id).to_dict()}

# pylint: disable=too-few-public-methods
class RecipeIngredientListAPI(flask_restful.Resource):
    """/recipes/{recipe_id}/ingredients endpoint"""

    # pylint: disable=no-self-use
    def get(self, recipe_id):
        """List all the ingredients for recipe_id"""
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

        return {'ingredients': list(ingredients_query)}

# pylint: disable=too-few-public-methods
class RecipeUtensilListAPI(flask_restful.Resource):
    """/recipes/{recipe_id}/utensils endpoint"""

    # pylint: disable=no-self-use
    def get(self, recipe_id):
        """List all the utensils for recipe_id"""
        get_recipe(recipe_id)

        utensils_query = (
            db.models.Utensil
            .select()
            .join(db.models.RecipeUtensils)
            .where(db.models.RecipeUtensils.recipe == recipe_id)
            .dicts())

        return {'utensils': list(utensils_query)}

