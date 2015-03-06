"""API ingredients entrypoints"""

import flask
import flask_restful
import api.recipes
import db.models as models
import db.connector
import utils.helpers
import utils.schemas as schemas

import peewee


def get_ingredient(ingredient_id):
    """Get a specific ingredient or raise 404 if it does not exists"""
    try:
        return models.Ingredient.get(models.Ingredient.id == ingredient_id)
    except peewee.DoesNotExist:
        raise utils.helpers.APIException('Ingredient not found', 404)


def update_ingredient(ingredient):
    ingredient_id = ingredient.pop('id')

    try:
        return (models.Ingredient
                .update(**ingredient)
                .where(models.Ingredient.id == ingredient_id)
                .returning()
                .dicts()
                .execute())
    except peewee.DoesNotExist:
        raise utils.helpers.APIException('Ingredient not found', 404)


class IngredientListAPI(flask_restful.Resource):
    """/ingredients/ endpoint"""

    # pylint: disable=no-self-use
    def get(self):
        """List all ingredients"""
        return {'ingredients': list(models.Ingredient.select().dicts())}

    @db.connector.database.transaction()
    def post(self):
        """Create an ingredient"""
        schema = schemas.ingredient_schema_post
        ingredient = utils.helpers.raise_or_return(schema)

        try:
            ingredient = models.Ingredient.create(**ingredient)
        except peewee.IntegrityError:
            flask_restful.abort(409, message='Ingredient already exists')

        ingredient, _ = schemas.ingredient_schema.dump(ingredient)
        return {'ingredient': ingredient}, 201

    @db.connector.database.transaction()
    def put(self):
        """Update multiple ingredients"""

        data = utils.helpers.raise_or_return(schemas.ingredient_schema_list)

        ingredients = []
        for ingredient in data['ingredients']:
            try:
                ingredients.append(update_ingredient(ingredient))
            except utils.helpers.APIException:
                pass

        return {'ingredients': ingredients}


class IngredientAPI(flask_restful.Resource):
    """/ingredients/{ingredient_id}/ endpoint"""

    # pylint: disable=no-self-use
    def get(self, ingredient_id):
        """Provide the ingredient for ingredient_id"""
        ingredient = get_ingredient(ingredient_id)
        ingredient, _ = schemas.ingredient_schema.dump(ingredient)
        return {'ingredient': ingredient}

    @db.connector.database.transaction()
    def put(self, ingredient_id):
        """Update the ingredient for ingredient_id"""
        schema = schemas.ingredient_schema_put
        ingredient = utils.helpers.raise_or_return(schema)
        ingredient['id'] = ingredient_id
        return {'ingredient': update_ingredient(ingredient)}


# pylint: disable=too-few-public-methods
class IngredientRecipeListAPI(flask_restful.Resource):
    """/ingredients/{ingredient_id}/recipes endpoint"""

    # pylint: disable=no-self-use
    def get(self, ingredient_id):
        """List all the recipes for ingredient_id"""
        get_ingredient(ingredient_id)
        where_clause = models.RecipeIngredients.ingredient == ingredient_id

        recipes = list(api.recipes.select_recipes(where_clause))
        recipes, _ = schemas.recipe_schema_list.dump({'recipes': recipes})
        return recipes


