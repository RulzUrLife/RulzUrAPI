"""API ingredients entrypoints"""
import flask_restful
import db.models
import utils.helpers

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

    def __init__(self):
        self.post_reqparse = flask_restful.reqparse.RequestParser()
        self.post_reqparse.add_argument(
            'name', type=str, required=True,
            help='No ingredient name provided', location='json'
        )

        self.put_reqparse = flask_restful.reqparse.RequestParser()
        self.put_reqparse.add_argument(
            'ingredients', type=list, required=True, location='json'
        )

        self.put_reqparse_ingredient = flask_restful.reqparse.RequestParser()
        self.put_reqparse_ingredient.add_argument(
            'id', type=int, required=True, location='json',
            help='id field not provided for all values'
        )
        self.put_reqparse_ingredient.add_argument(
            'name', type=str, location='json'
        )

        super(IngredientListAPI, self).__init__()


    # pylint: disable=no-self-use
    def get(self):
        """List all ingredients"""
        return {'ingredients': list(db.models.Ingredient.select().dicts())}

    def post(self):
        """Create an ingredient"""
        args = self.post_reqparse.parse_args()
        ingredient = db.models.Ingredient.create(name=args.get('name'))
        return {'ingredient': ingredient.to_dict()}, 201

    @db.connector.database.transaction()
    def put(self):
        """Update multiple ingredients"""
        args = self.put_reqparse.parse_args()
        ingredients = []
        nested_request = utils.helpers.NestedRequest()
        for ingredient in args.get('ingredients'):
            nested_request.nested_json = ingredient
            ingredient = (
                self.put_reqparse_ingredient.parse_args(nested_request)
            )
            ingredients += (
                utils.helpers.optimized_update(
                    db.models.Ingredient, ingredient
                ).execute()
            )

        return {'ingredients': ingredients}

# pylint: disable=too-few-public-methods
class IngredientAPI(flask_restful.Resource):
    """/ingredients/{ingredient_id}/ endpoint"""

    def __init__(self):
        self.put_reqparse = flask_restful.reqparse.RequestParser()
        self.put_reqparse.add_argument('name', type=str, location='json')
        super(IngredientAPI, self).__init__()

    # pylint: disable=no-self-use
    def get(self, ingredient_id):
        """Provide the ingredient for ingredient_id"""
        return {'ingredient': get_ingredient(ingredient_id).to_dict()}

    @db.connector.database.transaction()
    def put(self, ingredient_id):
        """Update the ingredient for ingredient_id"""
        args = (
            db.models.Ingredient, self.put_reqparse.parse_args(), ingredient_id
        )
        try:
            return {
                'ingredient': (
                    utils.helpers.optimized_update(*args).execute().next()
                )
            }
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

