"""API ingredients endpoint testing"""
import json
import peewee
import unittest.mock as mock
import db.models
import test.utils

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
    assert test.utils.load(ingredients_page) == {'ingredients': ingredients}

def test_ingredients_post(app, monkeypatch):
    """Test post /ingredients/"""
    ingredient = {'name': 'ingredient_1'}
    ingredient_mock = {'id': 1, 'name': 'ingredient_1'}

    mock_ingredient_create = mock.Mock()
    mock_ingredient_create.return_value = test.utils.FakeModel(ingredient_mock)
    monkeypatch.setattr('db.models.Ingredient.create', mock_ingredient_create)
    ingredients_create_page = app.post(
        '/ingredients/', data=json.dumps(ingredient),
        content_type='application/json'
    )

    assert ingredients_create_page.status_code == 201
    assert test.utils.load(ingredients_create_page) == {
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
    assert test.utils.load(ingredients_create_page) == error_missing_name

def test_ingredients_put(app, returning_update_mocking, monkeypatch):
    """Test put /ingredients/"""
    ingredients = [
        {'id': 1, 'name': 'ingredient_1'}, {'id': 2, 'name': 'ingredient_2'}
    ]
    ingredients_update = [
        {'id': 1, 'name': 'ingredient_1', 'desc': 'description_ingredient_1'},
        {'id': 2, 'name': 'ingredient_2', 'desc': 'description_ingredient_2'},
    ]

    def update_ingredient_generator():
        """Simple generator for update which returns ingredients"""
        for ingredient in ingredients_update:
            yield ingredient

    mock_returning_update = returning_update_mocking(
        update_ingredient_generator()
    )

    monkeypatch.setattr(
        'db.models.Ingredient.update', mock_returning_update
    )
    ingredients_update_page = app.put(
        '/ingredients/', data=json.dumps({'ingredients': ingredients}),
        content_type='application/json'
    )

    calls = [
        mock.call(returning=True, **ingredient) for ingredient in ingredients
    ]

    assert mock_returning_update.has_calls(calls)
    assert ingredients_update_page.status_code == 200
    assert test.utils.load(ingredients_update_page) == (
        {'ingredients': ingredients_update}
    )

def test_ingredients_put_cleanup_args(
        app, returning_update_mocking, monkeypatch):
    """Test put /ingredients/ arguments cleaner"""
    ingredients = [{'id': 1, 'name': 'ingredient_1', 'foo': 'bar'}]

    mock_returning_update = returning_update_mocking({})

    monkeypatch.setattr(
        'db.models.Ingredient.update', mock_returning_update
    )
    app.put(
        '/ingredients/', data=json.dumps({'ingredients': ingredients}),
        content_type='application/json'
    )
    # get the first element of ingredients and remove the "foo" entry
    ingredient = ingredients.pop()
    ingredient.pop('foo')
    ingredient.pop('id')
    assert mock_returning_update.call_count == 1
    assert mock_returning_update.call_args == mock.call(
        returning=True, **ingredient
    )


def test_ingredients_put_400(app):
    """Test put /ingredients/ with wrong parameters"""
    ingredients = [{'id': 1, 'name': 'ingredient_1'}, {'name':'ingredient_2'}]

    ingredients_update_page = app.put(
        '/ingredients/', data=json.dumps({}), content_type='application/json'
    )
    assert ingredients_update_page.status_code == 400
    assert test.utils.load(ingredients_update_page) == (
        {
            'message': 'Request malformed',
            'errors': {'ingredients': ['Missing data for required field.']}
        }
    )

    ingredients_update_page = app.put(
        '/ingredients/', data=json.dumps({'ingredients': ingredients}),
        content_type='application/json'
    )
    assert ingredients_update_page.status_code == 400
    assert test.utils.load(ingredients_update_page) == (
        {
            'message': 'Request malformed',
            'errors': {
                'ingredients': {'id': ['Missing data for required field.']}
            }
        }
    )

def test_ingredient_get(app, monkeypatch):
    """Test /ingredients/<id>"""

    ingredient = {'id': 1, 'name': 'ingredient_1'}

    mock_ingredient_get = mock.Mock(
        return_value=test.utils.FakeModel(ingredient)
    )
    monkeypatch.setattr('db.models.Ingredient.get', mock_ingredient_get)
    ingredient_page = app.get('/ingredients/1')

    assert mock_ingredient_get.call_count == 1
    assert test.utils.expression_assert(
        mock_ingredient_get, peewee.Expression(db.models.Ingredient.id, '=', 1)
    )
    assert test.utils.load(ingredient_page) == {'ingredient': ingredient}

def test_ingredient_get_404(app, monkeypatch):
    """Test /ingredients/<id> with ingredient not found"""

    monkeypatch.setattr(
        'db.models.Ingredient.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    ingredient = app.get('/ingredients/2')
    assert ingredient.status_code == 404

def test_ingredient_put(app, returning_update_mocking, monkeypatch):
    """Test put /ingredients/<id>"""
    ingredient = {'name': 'ingredient_1'}
    ingredient_update = {
        'id': 1, 'name': 'ingredient_1', 'desc': 'description_ingredient_1'
    }

    mock_returning_update = returning_update_mocking(ingredient_update)

    monkeypatch.setattr(
        'db.models.Ingredient.update', mock_returning_update
    )
    ingredient_update_page = app.put(
        '/ingredients/1', data=json.dumps(ingredient),
        content_type='application/json'
    )


    assert mock_returning_update.call_count == 1
    assert mock_returning_update.call_args == mock.call(
        returning=True, **ingredient
    )
    assert ingredient_update_page.status_code == 200
    assert test.utils.load(ingredient_update_page) == ingredient_update


def test_ingredient_put_404(app, returning_update_mocking, monkeypatch):
    """Test put /ingredients/<id> with ingredient not found"""
    ingredient = {'id': 1, 'name': 'ingredient_1'}

    mock_returning_update = returning_update_mocking(StopIteration)

    monkeypatch.setattr(
        'db.models.Ingredient.update', mock_returning_update
    )
    ingredient_update_page = app.put(
        '/ingredients/1', data=json.dumps(ingredient),
        content_type='application/json'
    )

    assert ingredient_update_page.status_code == 404

def test_ingredient_put_cleanup_args(
        app, monkeypatch, returning_update_mocking):
    """Test put /ingredients/<id> arguments cleaner"""
    ingredient = {'name': 'ingredient_1', 'foo': 'bar'}

    mock_returning_update = returning_update_mocking({})

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
    assert mock_returning_update.call_args == mock.call(
        returning=True, **ingredient
    )


def test_ingredient_get_recipes(app, monkeypatch, recipe_select_mocking):
    """Test /ingredients/<id>/recipes"""

    recipes = [{'recipe_1' : 'recipe_1_content'}]

    mock_ingredient_get = mock.Mock()
    monkeypatch.setattr('db.models.Ingredient.get', mock_ingredient_get)

    mock_recipe_select = recipe_select_mocking(recipes)
    ingredients_page = app.get('/ingredients/1/recipes')

    assert mock_ingredient_get.call_count == 1
    assert test.utils.expression_assert(
        mock_ingredient_get, peewee.Expression(db.models.Ingredient.id, '=', 1)
    )

    assert mock_recipe_select.call_count == 1
    assert mock_recipe_select.call_args == mock.call()

    join = mock_recipe_select.return_value.join
    assert join.call_count == 1
    assert join.call_args == mock.call(db.models.RecipeIngredients)

    where = join.return_value.where
    assert where.call_count == 1
    assert test.utils.expression_assert(
        where,
        peewee.Expression(db.models.RecipeIngredients.ingredient, '=', 1)
    )

    assert test.utils.load(ingredients_page) == {'recipes': recipes}

def test_ingredient_get_recipes_404(app, monkeypatch):
    """Test /ingredients/<id>/recipes with ingredient not found"""

    monkeypatch.setattr(
        'db.models.Ingredient.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    ingredient = app.get('/ingredients/2/recipes')
    assert ingredient.status_code == 404

