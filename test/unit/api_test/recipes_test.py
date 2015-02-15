"""API endpoints testing"""

import copy
import json
import peewee
import unittest.mock as mock
import db.models
import test.utils as utils
import utils.helpers as helpers

def test_recipes_list(app, monkeypatch):
    """Test /recipes/"""

    recipes = [
        {'recipe_1': 'recipe_1_content'},
        {'recipe_2': 'recipe_2_content'}
    ]

    mock_recipe_select = mock.Mock()
    mock_recipe_select.return_value.dicts.return_value = recipes
    monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)
    recipes_page = app.get('/recipes/')
    mock_recipe_select.assert_called_once_with()
    assert utils.load(recipes_page) == {'recipes': recipes}


def test_recipe_get(app, monkeypatch):
    """Test /recipes/<id>"""

    recipe = {'recipe_1': 'recipe_1_content'}

    mock_recipe_get = mock.Mock(return_value=utils.FakeModel(recipe))
    monkeypatch.setattr('db.models.Recipe.get', mock_recipe_get)
    recipe_page = app.get('/recipes/1')

    assert mock_recipe_get.call_count == 1
    assert utils.expression_assert(
        mock_recipe_get, peewee.Expression(db.models.Ingredient.id, '=', 1)
    )
    assert utils.load(recipe_page) == {'recipe': recipe}



def test_recipe_get_404(app, monkeypatch):
    """Test /recipes/<id> with recipe not found"""

    monkeypatch.setattr(
        'db.models.Recipe.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    recipe = app.get('/recipes/2')
    assert recipe.status_code == 404


# pylint: disable=too-many-statements, too-many-locals
def test_recipes_post(app, monkeypatch, post_recipe_fixture):
    """Test post /ingredients/"""


    # prepare the returned object to check against the test
    recipe_mock = copy.deepcopy(post_recipe_fixture)
    recipe_mock['id'] = 1

    recipe_mock = utils.FakeModel(recipe_mock)

    # prepare the nested tests, the first element will be used for checking
    # the insertion, the second one will be the result (it adds the id field)
    ingredients, ingredients_mock = [], []
    utensils, utensils_mock = [], []

    for i, ingredient in enumerate(post_recipe_fixture['ingredients']):
        ingredients.append({'name': ingredient['name']})
        ingredients_mock.append(
            utils.FakeModel({'id': i + 1, 'name': ingredient['name']})
        )

    for i, utensil in enumerate(post_recipe_fixture['utensils']):
        utensils.append({'name': utensil['name']})
        utensils_mock.append(
            utils.FakeModel({'id': i + 1, 'name': utensil['name']})
        )


    # add existing ingredients and utensils, to test validation
    post_recipe_fixture['ingredients'].append(
        {'id': 3, 'measurement': 'L', 'quantity': 1}
    )
    post_recipe_fixture['utensils'].append({'id': 3})

    utensils_select = [{'name': 'utensil_3'}]
    ingredients_select = [{'name': 'ingredient_3'}]

    ingredients_mock.append(
        utils.FakeModel({'id': 3, 'name': 'ingredient_3'})
    )
    utensils_mock.append(
        utils.FakeModel({'id': 3, 'name': 'utensil_3'})
    )


    # prepare some mock for recipe workflow
    mock_execute_sql = mock.Mock()
    mock_recipe_create = mock.Mock()
    mock_recipe_select = mock.Mock()


    # the nested fields will use two requests, the first one for validation,
    # the second one to populate the created recipe

    ingredient_validate, ingredient_select = mock.Mock(), mock.Mock()
    utensil_validate, utensil_select = mock.Mock(), mock.Mock()

    (ingredient_validate.return_value
     .where.return_value
     .dicts.return_value) = ingredients_select
    (ingredient_select.return_value
     .where.return_value) = ingredients_mock

    (utensil_validate.return_value
     .where.return_value
     .dicts.return_value) = utensils_select
    (utensil_select.return_value
     .where.return_value) = utensils_mock


    mock_ingredient_select = mock.Mock(
        side_effect=iter([ingredient_validate(), ingredient_select()])
    )

    mock_utensil_select = mock.Mock(
        side_effect=iter([utensil_validate(), utensil_select()])
    )

    # mock the other methods
    mock_ingredient_insert = mock.Mock()
    mock_utensil_insert = mock.Mock()

    mock_recipe_utensils_insert = mock.Mock()
    mock_recipe_ingredients_insert = mock.Mock()

    # monkeypatch all the things! o/
    monkeypatch.setattr('db.connector.database.execute_sql', mock_execute_sql)
    monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)
    monkeypatch.setattr('db.models.Recipe.create', mock_recipe_create)
    monkeypatch.setattr('db.models.Ingredient.select', mock_ingredient_select)
    monkeypatch.setattr(
        'db.models.Ingredient.insert_many_unique', mock_ingredient_insert
    )
    monkeypatch.setattr('db.models.Utensil.select', mock_utensil_select)
    monkeypatch.setattr(
        'db.models.Utensil.insert_many_unique', mock_utensil_insert
    )
    monkeypatch.setattr(
        'db.models.RecipeUtensils.insert_many', mock_recipe_utensils_insert
    )
    monkeypatch.setattr(
        'db.models.RecipeIngredients.insert_many',
        mock_recipe_ingredients_insert
    )

    # mock the recipes methods
    mock_recipe_select.return_value.where.return_value.count.return_value = 0
    mock_recipe_create.return_value = recipe_mock


    # go, go, go
    recipes_create_page = app.post(
        '/recipes/', data=json.dumps(post_recipe_fixture),
        content_type='application/json'
    )

    # check if the tables are correctly locked
    lock_string = 'LOCK TABLE %s IN SHARE ROW EXCLUSIVE MODE'
    lock_utensil = lock_string % helpers.model_entity(db.models.Utensil)
    lock_ingredient = lock_string % helpers.model_entity(db.models.Ingredient)

    utensil_lock = mock.call(lock_utensil)
    ingredient_lock = mock.call(lock_ingredient)

    assert mock_execute_sql.call_args_list == [utensil_lock, ingredient_lock]

    # check if the recipes are checked to avoid conflict
    assert mock_recipe_select.call_count == 1
    assert utils.expression_assert(
        mock_recipe_select.return_value.where,
        peewee.Expression(
            db.models.Recipe.name, '=', post_recipe_fixture.get('name')
        )
    )

    # check if the utensils or ingredients to update exists and if they are not
    # redundant in the same request

    # it has been called two times, one for the validation, one for the return
    assert mock_ingredient_select.call_count == 2
    assert utils.expression_assert(
        mock_ingredient_select, db.models.Ingredient.name
    )
    assert mock_ingredient_select.call_args_list[1] == mock.call()
    assert utils.expression_assert(
        ingredient_validate.return_value.where,
        peewee.Expression(
            db.models.Ingredient.id, peewee.OP_IN, [3]
        )
    )

    assert mock_utensil_select.call_count == 2
    assert utils.expression_assert(
        mock_utensil_select, db.models.Utensil.name
    )
    assert mock_utensil_select.call_args_list[1] == mock.call()
    assert utils.expression_assert(
        utensil_validate.return_value.where,
        peewee.Expression(
            db.models.Utensil.id, peewee.OP_IN, [3]
        )
    )

    # insertion into the tables of the nested fields
    execute = mock_ingredient_insert.return_value.execute
    assert mock_ingredient_insert.call_count == 1
    assert mock_ingredient_insert.call_args == mock.call(
        db.models.Ingredient.name, ingredients
    )
    assert execute.call_count == 1
    assert execute.call_args == mock.call()

    execute = mock_utensil_insert.return_value.execute
    assert mock_utensil_insert.call_count == 1
    assert mock_utensil_insert.call_args == mock.call(
        db.models.Utensil.name, utensils
    )
    assert execute.call_count == 1
    assert execute.call_args == mock.call

    post_recipe_fixture['id'] = 1

    # merge the fake model with the post fixture
    for index, ingredient in enumerate(ingredients_mock):
        post_recipe_fixture['ingredients'][index].update(ingredient.to_dict())

    post_recipe_fixture['utensils'] = [
        utensil.to_dict() for utensil in utensils_mock
    ]

    assert recipes_create_page.status_code == 201
    assert utils.load(recipes_create_page) == {
        'recipe': post_recipe_fixture
    }


def test_recipes_post_409(app, monkeypatch, post_recipe_fixture):
    """Test post conflict /recipes/"""

    mock_select = mock.Mock()
    mock_execute_sql = mock.Mock()

    monkeypatch.setattr('db.connector.database.execute_sql', mock_execute_sql)
    monkeypatch.setattr('db.models.Recipe.select', mock_select)

    mock_select.return_value.where.return_value.count.return_value = 1
    recipes_create_page = app.post(
        '/recipes/', data=json.dumps(post_recipe_fixture),
        content_type='application/json'
    )

    assert utils.expression_assert(
        mock_select.return_value.where,
        peewee.Expression(
            db.models.Recipe.name, '=', post_recipe_fixture.get('name')
        )
    )
    assert recipes_create_page.status_code == 409
    assert utils.load(recipes_create_page) == (
        {'message': 'Recipe already exists.', 'status': 409}
    )


def test_recipes_post_400(app, monkeypatch, post_recipe_fixture):
    """Test http error 400 possibilities"""

    def post(data):
        """Simply post dumped data on /recipes/"""
        return app.post(
            '/recipes/', data=json.dumps(data), content_type='application/json'
        )

    mock_execute_sql = mock.Mock()
    monkeypatch.setattr('db.connector.database.execute_sql', mock_execute_sql)

    error_message = {
        'errors': {'name': ['Missing data for required field.']},
        'message': 'Request malformed',
        'status': 400
    }
    post_recipe_fixture.pop('name')
    recipes_create_page = post(post_recipe_fixture)
    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['difficulty'] = 0
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['difficulty'] = ['Must be between 1 and 5.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['difficulty'] = 6
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['difficulty'] = ['Must be between 1 and 5.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture.pop('difficulty')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['difficulty'] = [
        'Missing data for required field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture['people'] = 0
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['people'] = ['Must be between 1 and 12.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['people'] = 13
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['people'] = ['Must be between 1 and 12.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture.pop('people')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['people'] = ['Missing data for required field.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['duration'] = 'error'
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['duration'] = [
        '\'error\' is not a valid choice for this field.'
    ]
    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture.pop('duration')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['duration'] = ['Missing data for required field.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['ingredients'].append(
        {'id': 1, 'measurement': 'oz', 'quantity': 1}
    )
    post_recipe_fixture['ingredients'].append(
        {'id': 2, 'measurement': 'oz', 'quantity': 1}
    )

    mock_select_update_elts = mock.Mock()
    (mock_select_update_elts.return_value
     .where.return_value
     .dicts.return_value) = [{'name': 'ingredient_3'}]

    monkeypatch.setattr('db.models.Ingredient.select', mock_select_update_elts)

    error_message['errors']['ingredients'] = [
        'There is some entries to update which does not exist.'
    ]

    recipes_create_page = post(post_recipe_fixture)

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    dicts_return_value = [{'name': 'ingredient_1'}, {'name': 'ingredient_3'}]

    (mock_select_update_elts.return_value
     .where.return_value
     .dicts.return_value) = dicts_return_value

    error_message['errors']['ingredients'] = [
        'There is multiple entries for the same entity.'
    ]

    recipes_create_page = post(post_recipe_fixture)

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['ingredients'][0]['measurement'] = 'error'
    recipes_create_page = post(post_recipe_fixture)

    error_message['errors']['ingredients'] = {}
    error_message['errors']['ingredients']['measurement'] = [
        '\'error\' is not a valid choice for this field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['ingredients'][0].pop('measurement')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['ingredients']['measurement'] = [
        'Missing data for required field.'
    ]
    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['ingredients'][0]['quantity'] = -1

    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['ingredients']['quantity'] = [
        'Must be at least 0.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['ingredients'][0].pop('quantity')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['ingredients']['quantity'] = [
        'Missing data for required field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture['ingredients'][0].pop('name')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['ingredients']['name'] = [
        'Missing data for required field if \'id\' field is not provided.'
    ]
    error_message['errors']['ingredients']['id'] = [
        'Missing data for required field if \'name\' field is not provided.'
    ]
    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['utensils'].append({'id': 1})
    post_recipe_fixture['utensils'].append({'id': 2})

    mock_select_update_elts = mock.Mock()
    (mock_select_update_elts.return_value
     .where.return_value
     .dicts.return_value) = [{'name': 'utensil_3'}]

    monkeypatch.setattr('db.models.Utensil.select', mock_select_update_elts)

    error_message['errors']['utensils'] = [
        'There is some entries to update which does not exist.'
    ]

    recipes_create_page = post(post_recipe_fixture)

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    (mock_select_update_elts.return_value
     .where.return_value
     .dicts.return_value) = [{'name': 'utensil_1'}, {'name': 'utensil_3'}]

    error_message['errors']['utensils'] = [
        'There is multiple entries for the same entity.'
    ]

    recipes_create_page = post(post_recipe_fixture)

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['utensils'][0].pop('name')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['utensils'] = {}
    error_message['errors']['utensils']['name'] = [
        'Missing data for required field if \'id\' field is not provided.'
    ]
    error_message['errors']['utensils']['id'] = [
        'Missing data for required field if \'name\' field is not provided.'
    ]
    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture['category'] = 'error'
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['category'] = [
        '\'error\' is not a valid choice for this field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture.pop('category')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['category'] = ['Missing data for required field.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture.pop('directions')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['directions'] = [
        'Missing data for required field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture.pop('utensils')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['utensils'] = [
        'Missing data for required field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture.pop('ingredients')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['ingredients'] = [
        'Missing data for required field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


def test_recipe_get_ingredients(app, monkeypatch):
    """Test /recipes/<id>/ingredients"""

    ingredients = [{'ingredient_1' : 'ingredient_1_content'}]

    mock_recipe_get = mock.Mock()
    monkeypatch.setattr('db.models.Recipe.get', mock_recipe_get)

    mock_recipe_ingredients_select = mock.Mock()
    (mock_recipe_ingredients_select.return_value
     .join.return_value
     .where.return_value
     .dicts.return_value) = ingredients

    monkeypatch.setattr(
        'db.models.RecipeIngredients.select',
        mock_recipe_ingredients_select
    )

    ingredients_page = app.get('/recipes/1/ingredients')


    assert mock_recipe_get.call_count == 1
    assert utils.expression_assert(
        mock_recipe_get, peewee.Expression(db.models.Recipe.id, '=', 1)
    )

    assert mock_recipe_ingredients_select.call_count == 1
    assert mock_recipe_ingredients_select.call_args == mock.call(
        db.models.RecipeIngredients.quantity,
        db.models.RecipeIngredients.measurement,
        db.models.Ingredient
    )

    join = mock_recipe_ingredients_select.return_value.join
    assert join.call_count == 1
    assert join.call_args == mock.call(db.models.Ingredient)

    where = join.return_value.where
    assert where.call_count == 1
    assert utils.expression_assert(
        where, peewee.Expression(db.models.RecipeIngredients.recipe, '=', 1)
    )

    assert utils.load(ingredients_page) == {'ingredients': ingredients}


def test_recipe_get_ingredients_404(app, monkeypatch):
    """Test /recipes/<id>/ingredients with recipe not found"""

    monkeypatch.setattr(
        'db.models.Recipe.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    recipe = app.get('/recipes/2/ingredients')
    assert recipe.status_code == 404


def test_recipe_get_utensils(app, monkeypatch):
    """Test /recipes/<id>/utensils"""

    utensils = [{'utensil_1' : 'utensil_1_content'}]

    mock_recipe_get = mock.Mock()
    monkeypatch.setattr('db.models.Recipe.get', mock_recipe_get)

    mock_utensil_select = mock.Mock()
    (mock_utensil_select.return_value
     .join.return_value
     .where.return_value
     .dicts.return_value) = utensils

    monkeypatch.setattr('db.models.Utensil.select', mock_utensil_select)

    utensils_page = app.get('/recipes/1/utensils')

    assert mock_recipe_get.call_count == 1
    assert utils.expression_assert(
        mock_recipe_get, peewee.Expression(db.models.Recipe.id, '=', 1)
    )

    assert mock_utensil_select.call_count == 1
    assert mock_utensil_select.call_args == mock.call()

    join = mock_utensil_select.return_value.join
    assert join.call_count == 1
    assert join.call_args == mock.call(db.models.RecipeUtensils)

    where = join.return_value.where
    assert where.call_count == 1
    assert utils.expression_assert(
        where, peewee.Expression(db.models.RecipeUtensils.recipe, '=', 1)
    )

    assert utils.load(utensils_page) == {'utensils': utensils}


def test_recipe_get_utensils_404(app, monkeypatch):
    """Test /recipes/<id>/utensils with recipe not found"""

    monkeypatch.setattr(
        'db.models.Recipe.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    recipe = app.get('/recipes/2/utensils')
    assert recipe.status_code == 404

