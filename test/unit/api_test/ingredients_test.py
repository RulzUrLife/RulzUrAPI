"""API ingredients endpoint testing"""
import copy
import unittest.mock as mock

import peewee
import pytest

import api.ingredients.endpoint as api_ingredients
import db.models as models
import utils.schemas as schemas
import utils.helpers as helpers

import test.utils as utils


def test_get_ingredient(monkeypatch):
    """Test the get ingredient method against API"""
    mock_ingredient_get = mock.Mock(return_value=mock.sentinel.ingredient)
    get_clause = peewee.Expression(models.Ingredient.id, peewee.OP.EQ,
                                   mock.sentinel.ingredient_id)

    monkeypatch.setattr('db.models.Ingredient.get', mock_ingredient_get)
    returned_ingredient = api_ingredients.get_ingredient(
        mock.sentinel.ingredient_id
    )

    assert returned_ingredient is mock.sentinel.ingredient
    assert mock_ingredient_get.call_args_list == [mock.call(get_clause)]


def test_get_ingredient_404(monkeypatch):
    """Test the get ingredient method with ingredient not found"""
    mock_ingredient_get = mock.Mock(side_effect=peewee.DoesNotExist)

    monkeypatch.setattr('db.models.Ingredient.get', mock_ingredient_get)
    with pytest.raises(helpers.APIException) as excinfo:
        api_ingredients.get_ingredient(None)

    assert excinfo.value.args == ('Ingredient not found', 404, None)


def test_update_ingredient(monkeypatch, ingredient):
    """Test the update ingredient method against API"""
    ingredient['id'] = mock.sentinel.ingredient_id
    where_exp = peewee.Expression(models.Ingredient.id, peewee.OP.EQ,
                                  mock.sentinel.ingredient_id)

    mock_ingredient_update = mock.Mock()
    where = mock_ingredient_update.return_value.where
    returning = where.return_value.returning
    dicts = returning.return_value.dicts
    dicts.return_value = mock.sentinel.ingredient

    monkeypatch.setattr('db.models.Ingredient.update', mock_ingredient_update)
    returned_ingredient = api_ingredients.update_ingredient(ingredient)

    assert returned_ingredient is mock.sentinel.ingredient
    assert mock_ingredient_update.call_args_list == [mock.call(**ingredient)]
    assert where.call_args_list == [mock.call(where_exp)]
    assert returning.call_args_list == [mock.call()]
    assert dicts.call_args_list == [mock.call()]


def test_update_ingredient_404(monkeypatch, ingredient):
    """Test the update ingredient method with ingredient not found"""
    mock_ingredient_update = mock.Mock(side_effect=peewee.DoesNotExist)

    monkeypatch.setattr('db.models.Ingredient.update', mock_ingredient_update)
    with pytest.raises(helpers.APIException) as excinfo:
        api_ingredients.update_ingredient(ingredient)

    assert excinfo.value.args == ('Ingredient not found', 404, None)


def test_ingredients_list(app, monkeypatch, ingredients):
    """Test /ingredients/"""

    mock_ingredient_select = mock.Mock()
    dicts = mock_ingredient_select.return_value.dicts
    dicts.return_value = ingredients['ingredients']

    monkeypatch.setattr('db.models.Ingredient.select', mock_ingredient_select)
    ingredients_page = app.get('/ingredients/')

    assert ingredients_page.status_code == 200
    assert mock_ingredient_select.call_args_list == [mock.call()]
    assert dicts.call_args_list == [mock.call()]
    assert utils.load(ingredients_page) == ingredients


def test_ingredients_post(app, monkeypatch, ingredient, ingredient_no_id):
    """Test post /ingredients/"""

    mock_raise_or_return = mock.Mock(return_value=ingredient_no_id)
    mock_ingredient_create = mock.Mock(
        return_value=utils.FakeModel(ingredient)
    )

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr('db.models.Ingredient.create', mock_ingredient_create)

    schema = schemas.ingredient_schema_post
    ingredient_create_calls = [mock.call(**ingredient_no_id)]

    ingredients_create_page = app.post('/ingredients/', data=ingredient_no_id)

    assert ingredients_create_page.status_code == 201
    assert utils.load(ingredients_create_page) == {'ingredient': ingredient}
    assert mock_ingredient_create.call_args_list == ingredient_create_calls
    assert mock_raise_or_return.call_args_list == [mock.call(schema)]


def test_ingredients_post_409(app, monkeypatch, ingredient_no_id):
    """Test post /ingredients/ with conflict"""
    mock_raise_or_return = mock.Mock(return_value=ingredient_no_id)
    mock_ingredient_create = mock.Mock(side_effect=peewee.IntegrityError)

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr('db.models.Ingredient.create', mock_ingredient_create)

    ingredients_create_page = app.post('/ingredients/', data=ingredient_no_id)
    error_msg = {'message': 'Ingredient already exists', 'status_code': 409}
    assert ingredients_create_page.status_code == 409
    assert utils.load(ingredients_create_page) == error_msg


def test_ingredients_put(app, monkeypatch, ingredients):
    """Test put /ingredients/"""

    mock_raise_or_return = mock.Mock(return_value=ingredients)
    mock_update_ingredient = mock.Mock(
        side_effect=iter(ingredients['ingredients'])
    )

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr(api_ingredients, 'update_ingredient',
                        mock_update_ingredient)

    schema = schemas.ingredient_schema_list
    ingredients_update_page = app.put('/ingredients/', data=ingredients)

    update_calls = [
        mock.call(ingredient) for ingredient in ingredients['ingredients']
    ]
    assert ingredients_update_page.status_code == 200
    assert utils.load(ingredients_update_page) == ingredients
    assert mock_update_ingredient.call_args_list == update_calls
    assert mock_raise_or_return.call_args_list == [mock.call(schema)]


def test_ingredients_put_with_exception(app, monkeypatch, ingredients):
    """Test put /ingredients/ with an exception raise"""
    update_ingredient_returns = iter([
        helpers.APIException('Error')
        for _ in range(len(ingredients['ingredients']))
    ])
    mock_raise_or_return = mock.Mock(return_value=ingredients)
    mock_update_ingredient = mock.Mock(side_effect=update_ingredient_returns)

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr(api_ingredients, 'update_ingredient',
                        mock_update_ingredient)
    ingredients_update_page = app.put('/ingredients/', data=ingredients)

    update_calls = [
        mock.call(ingredient) for ingredient in ingredients['ingredients']
    ]
    assert ingredients_update_page.status_code == 200
    assert utils.load(ingredients_update_page) == {'ingredients': []}
    assert mock_update_ingredient.call_args_list == update_calls


def test_ingredient_get(app, monkeypatch, ingredient):
    """Test /ingredients/<id>"""
    sentinel_ingredient = mock.sentinel.ingredient
    mock_get_ingredient = mock.Mock(return_value=sentinel_ingredient)
    mock_ingredient_dump = mock.Mock(return_value=(ingredient, None))

    monkeypatch.setattr(api_ingredients, 'get_ingredient', mock_get_ingredient)
    monkeypatch.setattr('utils.schemas.ingredient_schema.dump',
                        mock_ingredient_dump)

    ingredient_page = app.get('/ingredients/1/')
    ingredient_dump_calls = [mock.call(sentinel_ingredient)]
    assert ingredient_page.status_code == 200
    assert utils.load(ingredient_page) == {'ingredient': ingredient}
    assert mock_get_ingredient.call_args_list == [mock.call(1)]
    assert mock_ingredient_dump.call_args_list == ingredient_dump_calls


def test_ingredient_put(app, monkeypatch, ingredient):
    """Test put /ingredients/<id>"""
    ingredient_copy = copy.deepcopy(ingredient)
    ingredient_copy['id'] = 2

    mock_raise_or_return = mock.Mock(return_value=ingredient)
    mock_update_ingredient = mock.Mock(return_value=ingredient)

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr(api_ingredients, 'update_ingredient',
                        mock_update_ingredient)

    schema = schemas.ingredient_schema_put
    ingredient_put_page = app.put('/ingredients/2/', data=ingredient)
    update_ingredient_calls = [mock.call(ingredient_copy)]

    assert ingredient_put_page.status_code == 200
    assert utils.load(ingredient_put_page) == {'ingredient': ingredient}
    assert mock_raise_or_return.call_args_list == [mock.call(schema)]
    assert mock_update_ingredient.call_args_list == update_ingredient_calls


def test_ingredient_get_recipes(app, monkeypatch):
    """Test /ingredients/<id>/recipes"""

    recipe = {str(mock.sentinel.recipe_key): str(mock.sentinel.recipe)}
    recipes = {'recipes': [recipe]}
    mock_recipes = mock.MagicMock(wraps=recipes, spec=dict)

    mock_get_ingredient = mock.Mock()
    mock_select_recipes = mock.Mock(return_value=[mock.sentinel.recipe])
    mock_recipe_dump = mock.Mock(return_value=(mock_recipes, None))

    monkeypatch.setattr(api_ingredients, 'get_ingredient', mock_get_ingredient)
    monkeypatch.setattr('api.recipes.select_recipes', mock_select_recipes)
    monkeypatch.setattr('utils.schemas.recipe_schema_list.dump',
                        mock_recipe_dump)

    ingredient_recipes_page = app.get('/ingredients/1/recipes/')
    select_recipes_calls = [mock.call(
        peewee.Expression(models.RecipeIngredients.ingredient, peewee.OP.EQ, 1)
    )]

    assert ingredient_recipes_page.status_code == 200
    assert utils.load(ingredient_recipes_page) == recipes

    assert mock_get_ingredient.call_args_list == [mock.call(1)]
    assert mock_select_recipes.call_args_list == select_recipes_calls
    assert mock_recipe_dump.call_args_list == [mock.call({
        'recipes': [mock.sentinel.recipe]
    })]


