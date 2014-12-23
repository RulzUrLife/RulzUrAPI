"""Flask API Entrypoint

Creates the Flask object

Loads API entrypoints into flask
Initialise the database with the config in db.connector, this avoid multiple
initialization accross the codebase

"""
import flask
import db.connector
import logging
import os
import api.recipes
import api.utensils
import api.ingredients
import flask_restful


def init_app():
    """Init the Flask app"""
    db.connector.database.init(**db.connector.config)

    if int(os.environ.get('DEBUG', 0)) != 0:
        logger = logging.getLogger('peewee')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    app = flask.Flask(__name__)
    public_api = flask_restful.Api(app)

    # Utensils endpoints
    public_api.add_resource(
        api.utensils.UtensilListAPI,
        '/utensils/',
        endpoint='utensils'
    )
    public_api.add_resource(
        api.utensils.UtensilAPI,
        '/utensils/<int:utensil_id>',
        endpoint='utensil'
    )
    public_api.add_resource(
        api.utensils.UtensilRecipeListAPI,
        '/utensils/<int:utensil_id>/recipes',
        endpoint='utensil_recipes'
    )

    # Ingredients endpoints
    public_api.add_resource(
        api.ingredients.IngredientListAPI,
        '/ingredients/',
        endpoint='ingredients'
    )
    public_api.add_resource(
        api.ingredients.IngredientAPI,
        '/ingredients/<int:ingredient_id>',
        endpoint='ingredient'
    )
    public_api.add_resource(
        api.ingredients.IngredientRecipeListAPI,
        '/ingredients/<int:ingredient_id>/recipes',
        endpoint='ingredient_recipes'
    )

    # Recipes endpoints
    public_api.add_resource(
        api.recipes.RecipeListAPI,
        '/recipes/',
        endpoint='recipes'
    )
    public_api.add_resource(
        api.recipes.RecipeAPI,
        '/recipes/<int:recipe_id>',
        endpoint='recipe'
    )
    public_api.add_resource(
        api.recipes.RecipeUtensilListAPI,
        '/recipes/<int:recipe_id>/utensils',
        endpoint='recipe_utensils'
    )

    public_api.add_resource(
        api.recipes.RecipeIngredientListAPI,
        '/recipes/<int:recipe_id>/ingredients',
        endpoint='recipe_ingredients'
    )

    return app

