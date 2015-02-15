"""API ingredients endpoint testing"""
import json
import peewee
import unittest.mock as mock
import db.models
import test.utils as utils

def test_ingredients_list(app, monkeypatch):
    """Test /ingredients/"""

    ingredients = [
        {'ingredient_1': 'ingredient_1_content'},
        {'ingredient_2': 'ingredient_2_content'}
    ]

    mock_ingredient_select = mock.Mock()
    mock_ingredient_select.return_value.dicts.return_value = ingredients
    monkeypatch.setattr('db.models.Ingredient.select', mock_ingredient_select)
    ingredients_page = app.get('/ingredients/')

    assert mock_ingredient_select.call_count == 1
    assert mock_ingredient_select.call_args == mock.call()
    assert utils.load(ingredients_page) == {'ingredients': ingredients}

def test_ingredients_post(app, monkeypatch):
    """Test post /ingredients/"""
    ingredient = {'name': 'ingredient_1'}
    ingredient_mock = {'id': 1, 'name': 'ingredient_1'}

    mock_ingredient_create = mock.Mock()
    mock_ingredient_create.return_value = utils.FakeModel(ingredient_mock)
    monkeypatch.setattr('db.models.Ingredient.create', mock_ingredient_create)
    ingredients_create_page = app.post(
        '/ingredients/', data=json.dumps(ingredient),
        content_type='application/json'
    )

    assert ingredients_create_page.status_code == 201
    assert utils.load(ingredients_create_page) == {
        'ingredient': ingredient_mock
    }
    assert mock_ingredient_create.call_count == 1
    assert mock_ingredient_create.call_args == mock.call(**ingredient)

def test_ingredients_post_400(app, error_missing_name):
    """Test post /ingredients/ with wrong parameters"""
    ingredient = {}

    ingredients_create_page = app.post(
        '/ingredients/', data=json.dumps(ingredient),
        content_type='application/json'
    )
    assert ingredients_create_page.status_code == 400
    assert utils.load(ingredients_create_page) == error_missing_name

def test_ingredients_put(app, monkeypatch):
    """Test put /ingredients/"""
    ingredients_update = [
        {'id': 1, 'name': 'ingredient_1', 'desc': 'description_ingredient_1'},
        {'id': 2, 'name': 'ingredient_2', 'desc': 'description_ingredient_2'},
    ]

    ingredients, update_calls = [], []

    for ingredient in ingredients_update:
        ingredients.append(
            {'id': ingredient['id'], 'name': ingredient['name']}
        )
        update_calls.append(mock.call(name=ingredient['name']))

    mock_returning_update = utils.update_mocking(iter(ingredients_update))
    monkeypatch.setattr(
        'db.models.Ingredient.update', mock_returning_update
    )
    ingredients_update_page = app.put(
        '/ingredients/', data=json.dumps({'ingredients': ingredients}),
        content_type='application/json'
    )

    assert mock_returning_update.call_args_list == update_calls
    assert ingredients_update_page.status_code == 200
    assert utils.load(ingredients_update_page) == (
        {'ingredients': ingredients_update}
    )

def test_ingredients_put_cleanup_args(app, monkeypatch):
    """Test put /ingredients/ arguments cleaner"""
    ingredients = [
        {'id': 1, 'name': 'ingredient_1', 'foo': 'bar'},
        {'id': 2, 'name': 'ingredient_2', 'bar': 'foo'}
    ]

    mock_returning_update = utils.update_mocking(iter([{}, {}]))

    monkeypatch.setattr(
        'db.models.Ingredient.update', mock_returning_update
    )
    app.put(
        '/ingredients/', data=json.dumps({'ingredients': ingredients}),
        content_type='application/json'
    )
    # remove the extra entries
    ingredient_2 = ingredients.pop()
    ingredient_2.pop('bar')
    ingredient_2.pop('id')

    ingredient_1 = ingredients.pop()
    ingredient_1.pop('foo')
    ingredient_1.pop('id')

    assert mock_returning_update.call_count == 2
    assert mock_returning_update.call_args_list == [
        mock.call(**ingredient_1), mock.call(**ingredient_2)
    ]


def test_ingredients_put_400(app):
    """Test put /ingredients/ with wrong parameters"""
    ingredients = [{'id': 1, 'name': 'ingredient_1'}, {'name':'ingredient_2'}]

    ingredients_update_page = app.put(
        '/ingredients/', data=json.dumps({}), content_type='application/json'
    )
    assert ingredients_update_page.status_code == 400
    assert utils.load(ingredients_update_page) == (
        {
            'message': 'Request malformed',
            'errors': {'ingredients': ['Missing data for required field.']},
            'status': 400
        }
    )

    ingredients_update_page = app.put(
        '/ingredients/', data=json.dumps({'ingredients': ingredients}),
        content_type='application/json'
    )
    assert ingredients_update_page.status_code == 400
    assert utils.load(ingredients_update_page) == (
        {
            'message': 'Request malformed',
            'errors': {
                'ingredients': {'id': ['Missing data for required field.']}
            },
            'status': 400
        }
    )

def test_ingredient_get(app, monkeypatch):
    """Test /ingredients/<id>"""

    ingredient = {'id': 1, 'name': 'ingredient_1'}

    mock_ingredient_get = mock.Mock(return_value=utils.FakeModel(ingredient))
    get_expr = peewee.Expression(db.models.Ingredient.id, peewee.OP_EQ, 1)

    monkeypatch.setattr('db.models.Ingredient.get', mock_ingredient_get)
    ingredient_page = app.get('/ingredients/1')

    assert mock_ingredient_get.call_count == 1
    assert utils.expression_assert(mock_ingredient_get, get_expr)
    assert utils.load(ingredient_page) == {'ingredient': ingredient}

def test_ingredient_get_404(app, monkeypatch):
    """Test /ingredients/<id> with ingredient not found"""

    monkeypatch.setattr(
        'db.models.Ingredient.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    ingredient = app.get('/ingredients/2')
    assert ingredient.status_code == 404
    assert utils.load(ingredient) == {
        'message': 'Ingredient not found', 'status': 404
    }


def test_ingredient_put(app, monkeypatch):
    """Test put /ingredients/<id>"""
    ingredient = {'name': 'ingredient_1'}
    ingredient_update = {
        'id': 1, 'name': 'ingredient_1', 'desc': 'description_ingredient_1'
    }
    where_expr = peewee.Expression(db.models.Ingredient.id, peewee.OP_EQ,
                                   ingredient_update['id'])

    mock_returning_update = mock.Mock()

    where = mock_returning_update.return_value.where
    returning = where.return_value.returning
    dicts = returning.return_value.dicts
    execute = dicts.return_value.execute
    execute.return_value = ingredient_update

    monkeypatch.setattr(
        'db.models.Ingredient.update', mock_returning_update
    )
    ingredient_update_page = app.put(
        '/ingredients/1', data=json.dumps(ingredient),
        content_type='application/json'
    )

    assert mock_returning_update.call_args_list == [
        mock.call(name=ingredient['name'])
    ]
    assert utils.expression_assert(where, where_expr)
    assert returning.call_args_list == [mock.call()]
    assert dicts.call_args_list == [mock.call()]

    assert execute.call_count == 1
    assert execute.call_args_list == [mock.call()]

    assert ingredient_update_page.status_code == 200
    assert utils.load(ingredient_update_page) == ingredient_update


def test_ingredient_put_cleanup_args(app, monkeypatch):
    """Test put /ingredients/<id> arguments cleaner"""
    ingredient = {'name': 'ingredient_1', 'foo': 'bar'}

    mock_returning_update = utils.update_mocking({})

    monkeypatch.setattr(
        'db.models.Ingredient.update', mock_returning_update
    )
    app.put(
        '/ingredients/1', data=json.dumps(ingredient),
        content_type='application/json'
    )
    # get the first element of ingredient and remove the "foo" entry
    ingredient.pop('foo')

    assert mock_returning_update.call_count == 1
    assert mock_returning_update.call_args == mock.call(**ingredient)

def test_ingredient_put_404(app, monkeypatch):
    """Test put /ingredients/<id> with ingredient not found"""
    ingredient = {'id': 1, 'name': 'ingredient_1'}

    mock_returning_update = utils.update_mocking(StopIteration)

    monkeypatch.setattr(
        'db.models.Ingredient.update', mock_returning_update
    )
    ingredient_update_page = app.put(
        '/ingredients/1', data=json.dumps(ingredient),
        content_type='application/json'
    )

    assert ingredient_update_page.status_code == 404
    assert utils.load(ingredient_update_page) == {
        'message': 'Ingredient not found', 'status': 404
    }


def test_ingredient_get_recipes(app, monkeypatch, recipe_select_mocking):
    """Test /ingredients/<id>/recipes"""

    recipes = [{'recipe_1' : 'recipe_1_content'}]

    mock_ingredient_get = mock.Mock()
    monkeypatch.setattr('db.models.Ingredient.get', mock_ingredient_get)

    mock_recipe_select = recipe_select_mocking(recipes)
    ingredients_page = app.get('/ingredients/1/recipes')

    get_expr = peewee.Expression(db.models.Ingredient.id, peewee.OP_EQ, 1)
    where_expr = peewee.Expression(
        db.models.RecipeIngredients.ingredient, peewee.OP_EQ, 1
    )

    assert mock_ingredient_get.call_count == 1
    assert utils.expression_assert(mock_ingredient_get, get_expr)

    assert mock_recipe_select.call_count == 1
    assert mock_recipe_select.call_args == mock.call()

    join = mock_recipe_select.return_value.join
    assert join.call_count == 1
    assert join.call_args == mock.call(db.models.RecipeIngredients)

    where = join.return_value.where
    assert where.call_count == 1
    assert utils.expression_assert(where, where_expr)

    assert utils.load(ingredients_page) == {'recipes': recipes}

def test_ingredient_get_recipes_404(app, monkeypatch):
    """Test /ingredients/<id>/recipes with ingredient not found"""

    monkeypatch.setattr(
        'db.models.Ingredient.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    ingredient = app.get('/ingredients/2/recipes')
    assert ingredient.status_code == 404
    assert utils.load(ingredient) == {
        'message': 'Ingredient not found', 'status': 404
    }
