"""API recipes entrypoints"""

import flask_restful

import db.connector
import db.models

import utils.helpers

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

    def __init__(self):
        def init_reqparse(element):
            """Init request parser for put and post methods"""

            put_reqparse = flask_restful.reqparse.RequestParser()
            post_reqparse = flask_restful.reqparse.RequestParser()

            for name, kwargs in element.items():
                post_reqparse.add_argument(
                    name, required=True, location='json', **kwargs
                )
                put_reqparse.add_argument(
                    name, location='json', **kwargs
                )
            return post_reqparse, put_reqparse

        reqparse = self.reqparse = {
            'post': None, 'put': None, 'put_recipe': None,
            'post_ingredient': None, 'put_ingredient': None,
            'post_utensil': None, 'put_utensil': None
        }

        reqparse['post'], reqparse['put_recipe'] = (
            init_reqparse(utils.helpers.reqparse['recipe'])
        )
        reqparse['post_ingredient'], reqparse['put_ingredient'] = (
            init_reqparse(utils.helpers.reqparse['ingredient'])
        )
        reqparse['post_utensil'], reqparse['put_utensil'] = (
            init_reqparse(utils.helpers.reqparse['utensil'])
        )

        reqparse['put_recipe'].add_argument(
            'id', type=int, required=True, location='json',
            help='id field not provided for all recipes'
        )
        reqparse['put'] = flask_restful.reqparse.RequestParser()
        reqparse['put'].add_argument(
            'recipes', type=list, required=True, location='json'
        )
        self.query_compiler = peewee.QueryCompiler()
        super(RecipeListAPI, self).__init__()


    # pylint: disable=no-self-use
    def get(self):
        """List all recipes"""
        return {'recipes': list(db.models.Recipe.select().dicts())}

    @db.connector.database.transaction()
    def post(self):
        """Create a recipe"""

        # pylint: disable=protected-access
        def parse_list(model, json_list, reqparse_fn, insert_fn):
            """Parse a model list and insert it in the dedicated table"""

            nested_request = utils.helpers.NestedRequest()
            elements = []
            model_entity, _ = self.query_compiler._parse_entity(
                model._as_entity(), None, None
            )
            lock_request = (
                'LOCK TABLE %s IN SHARE ROW EXCLUSIVE MODE' % model_entity
            )

            for element in json_list:
                nested_request.nested_json = element
                elements.append(reqparse_fn.parse_args(nested_request))

            if not len(elements):
                return []

            #protect the database table against race condition
            db.connector.database.execute_sql(lock_request)
            return insert_fn(elements)

        def insert_ingredients(ingredients_list):
            """Insert ingredient list into the Ingredient table and return
            the entries
            """
            ingredients_dataset = []
            ingredients_dict = {}

            for ingredient in ingredients_list:
                # the name is the key in ingredients_dict
                name = ingredient.pop('name')
                ingredients_dict[name] = ingredient
                ingredients_dataset.append({'name': name})

            if len(ingredients_dict.keys()) != len(ingredients_list):
                raise ValueError(
                    'There is multiple entries for the same ingredient'
                )

            query = db.models.Ingredient.insert_many_unique(
                db.models.Ingredient.name, ingredients_dataset
            )
            query.execute()

            query = (db.models.Ingredient
                     .select()
                     .where(
                         db.models.Ingredient.name << ingredients_dict.keys()
                     ))
            for ingredient in query:
                ingredients_dict[ingredient.name]['ingredient'] = ingredient

            return ingredients_dict.values()

        def insert_utensils(utensils):
            """Insert utensils into the Utensil table and return the entries"""

            # this remove duplicate keys
            names = {utensil['name'] for utensil in utensils}

            query = db.models.Utensil.insert_many_unique(
                db.models.Utensil.name, utensils
            )
            query.execute()

            query = (db.models.Utensil
                     .select()
                     .where(db.models.Utensil.name << list(names)))
            return [{'utensil': utensil} for utensil in query]

        recipe = self.reqparse['post'].parse_args()
        count = db.models.Recipe.select().where(
            db.models.Recipe.name == recipe.get('name')
        ).count()

        if count:
            flask_restful.abort(409, message='recipe already exists')

        ingredients = parse_list(
            db.models.Ingredient, recipe.pop('ingredients'),
            self.reqparse['post_ingredient'], insert_ingredients
        )

        utensils = parse_list(
            db.models.Utensil, recipe.pop('utensils'),
            self.reqparse['post_utensil'], insert_utensils
        )

        recipe = db.models.Recipe.create(**recipe)
        recipe.ingredients = ingredients
        recipe.utensils = utensils

        for ingredient in ingredients:
            ingredient['recipe'] = recipe

        for utensil in utensils:
            utensil['recipe'] = recipe

        db.models.RecipeUtensils.insert_many(utensils).execute()
        db.models.RecipeIngredients.insert_many(ingredients).execute()

        return flask_restful.marshal(
            recipe.to_dict(), utils.helpers.recipe_marshal, envelope='recipe'
        ), 201


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

