"""API ingredients entrypoints"""

import flask
import flask_restful

import peewee

import db.models
import db.connector

import utils.helpers
import utils.schemas


def get_ingredient(ingredient_id):
    """Get a specific ingredient or raise 404 if it does not exists"""
    try:
        return db.models.Ingredient.get(
            db.models.Ingredient.id == ingredient_id
        )
    except peewee.DoesNotExist:
        raise utils.helpers.APIException('Ingredient not found', 404)

class IngredientListAPI(flask_restful.Resource):
    """/ingredients/ endpoint"""

    # pylint: disable=no-self-use
    def get(self):
        """List all ingredients"""
        return {'ingredients': list(db.models.Ingredient.select().dicts())}

    @db.connector.database.transaction()
    def post(self):
        """Create an ingredient"""
        ingredient = utils.helpers.raise_or_return(
            utils.schemas.ingredient_schema_post, flask.request.json
        )

        try:
            ingredient = db.models.Ingredient.create(**ingredient)
        except peewee.IntegrityError:
            raise utils.helpers.APIException('Ingredient already exists', 409)

        ingredient, _ = utils.schemas.ingredient_schema.dump(ingredient)
        return {'ingredient': ingredient}, 201

    @db.connector.database.transaction()
    def put(self):
        """Update multiple ingredients"""
        ingredients = []

        data = utils.helpers.raise_or_return(
            utils.schemas.ingredient_schema_list, flask.request.json
        )

        for ingredient in data['ingredients']:
            ingredient_id = ingredient.pop('id')
            try:
                ingredients.append(
                    db.models.Ingredient
                    .update(**ingredient)
                    .where(db.models.Ingredient.id == ingredient_id)
                    .returning()
                    .dicts()
                    .execute())
            except StopIteration:
                pass

        return {'ingredients': ingredients}

# pylint: disable=too-few-public-methods
class IngredientAPI(flask_restful.Resource):
    """/ingredients/{ingredient_id}/ endpoint"""

    # pylint: disable=no-self-use
    def get(self, ingredient_id):
        """Provide the ingredient for ingredient_id"""
        ingredient, _ = utils.schemas.ingredient_schema.dump(
            get_ingredient(ingredient_id)
        )
        return {'ingredient': ingredient}

    @db.connector.database.transaction()
    def put(self, ingredient_id):
        """Update the ingredient for ingredient_id"""
        ingredient = utils.helpers.raise_or_return(
            utils.schemas.ingredient_schema_put, flask.request.json
        )

        try:
            return (db.models.Ingredient
                    .update(**ingredient)
                    .where(db.models.Ingredient.id == ingredient_id)
                    .returning()
                    .dicts()
                    .execute())

        except StopIteration:
            raise utils.helpers.APIException('Utensil not found', 404)


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

