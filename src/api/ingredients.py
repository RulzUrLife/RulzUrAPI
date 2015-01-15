"""API ingredients entrypoints"""
import flask
import flask_restful
import db.models
import utils.helpers
import utils.schemas

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

    def post(self):
        """Create an ingredient"""
        ingredient = utils.helpers.parse_args(
            utils.schemas.post_ingredients_parser, flask.request.json
        )

        try:
            ingredient = db.models.Ingredient.create(**ingredient)
        except peewee.IntegrityError:
            flask_restful.abort(409, message='Ingredient already exists')

        ingredient = utils.schemas.ingredient_parser.dump(ingredient).data
        return (
            {'ingredient': ingredient}, 201
        )

    @db.connector.database.transaction()
    def put(self):
        """Update multiple ingredients"""
        ingredients = []
        data = utils.helpers.parse_args(
            utils.schemas.put_ingredients_parser, flask.request.json
        )

        for ingredient in data['ingredients']:
            ingredient_id = ingredient.pop('id')
            try:
                ingredients.append(
                    db.models.Ingredient
                    .update(returning=True, **ingredient)
                    .where(db.models.Ingredient.id == ingredient_id)
                    .dicts()
                    .execute()
                    .next()
                )
            except StopIteration:
                pass

        return {'ingredients': ingredients}

# pylint: disable=too-few-public-methods
class IngredientAPI(flask_restful.Resource):
    """/ingredients/{ingredient_id}/ endpoint"""

    # pylint: disable=no-self-use
    def get(self, ingredient_id):
        """Provide the ingredient for ingredient_id"""
        return {
            'ingredient': utils.schemas.ingredient_parser.dump(
                get_ingredient(ingredient_id)
            ).data
        }

    @db.connector.database.transaction()
    def put(self, ingredient_id):
        """Update the ingredient for ingredient_id"""
        ingredient = utils.helpers.parse_args(
            utils.schemas.ingredient_parser, flask.request.json
        )

        try:
            return (
                db.models.Ingredient
                .update(returning=True, **ingredient)
                .where(db.models.Ingredient.id == ingredient_id)
                .dicts()
                .execute()
                .next()
            )

        except StopIteration:
            flask_restful.abort(404)


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

