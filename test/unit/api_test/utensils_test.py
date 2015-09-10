"""API utensils endpoint testing"""
# pylint: disable=no-self-use, too-many-locals, too-many-statements
import unittest.mock as mock

import peewee
import pytest

import api.utensils
import db.models as models
import utils.schemas as schemas
import utils.helpers as helpers

import test.utils as utils


def test_get_utensil(monkeypatch):
    """Test the api.utensils.get_utensil function"""
    mock_utensil_get = mock.Mock(return_value=mock.sentinel.utensil)
    get_clause = peewee.Expression(models.Utensil.id, peewee.OP.EQ,
                                   mock.sentinel.utensil_id)

    monkeypatch.setattr('db.models.Utensil.get', mock_utensil_get)
    returned_utensil = api.utensils.get_utensil(mock.sentinel.utensil_id)

    assert returned_utensil is mock.sentinel.utensil
    assert mock_utensil_get.call_args_list == [mock.call(get_clause)]


def test_get_utensil_404(monkeypatch):
    """Test the api.utensils.get_utensil function with inexistent element"""
    mock_utensil_get = mock.Mock(side_effect=peewee.DoesNotExist)

    monkeypatch.setattr('db.models.Utensil.get', mock_utensil_get)
    with pytest.raises(helpers.APIException) as excinfo:
        api.utensils.get_utensil(None)

    assert excinfo.value.args == ('Utensil not found', 404, None)


def test_update_utensil(monkeypatch, utensil):
    """Test api.utensils.update_utensil function"""
    utensil['id'] = mock.sentinel.utensil_id
    where_exp = peewee.Expression(models.Utensil.id, peewee.OP.EQ,
                                  mock.sentinel.utensil_id)

    mock_utensil_update = mock.Mock()
    where = mock_utensil_update.return_value.where
    returning = where.return_value.returning
    dicts = returning.return_value.dicts
    dicts.return_value = mock.sentinel.utensil

    monkeypatch.setattr('db.models.Utensil.update', mock_utensil_update)
    returned_utensil = api.utensils.update_utensil(utensil)

    assert returned_utensil is mock.sentinel.utensil
    assert mock_utensil_update.call_args_list == [mock.call(**utensil)]
    assert where.call_args_list == [mock.call(where_exp)]
    assert returning.call_args_list == [mock.call()]
    assert dicts.call_args_list == [mock.call()]


def test_update_utensil_404(monkeypatch, utensil):
    """Test the api.utensils.update_utensil function with inexistent element"""
    mock_utensil_update = mock.Mock(side_effect=peewee.DoesNotExist)

    monkeypatch.setattr('db.models.Utensil.update', mock_utensil_update)
    with pytest.raises(helpers.APIException) as excinfo:
        api.utensils.update_utensil(utensil)

    assert excinfo.value.args == ('Utensil not found', 404, None)


def test_utensils_list(app, monkeypatch, utensils):
    """Test /utensils/"""

    mock_utensil_select = mock.Mock()
    dicts = mock_utensil_select.return_value.dicts
    dicts.return_value = utensils['utensils']

    monkeypatch.setattr('db.models.Utensil.select', mock_utensil_select)
    utensils_page = app.get('/utensils/')

    assert utensils_page.status_code == 200
    assert mock_utensil_select.call_args_list == [mock.call()]
    assert dicts.call_args_list == [mock.call()]
    assert utils.load(utensils_page) == utensils


def test_utensils_post(app, monkeypatch):
    """Test post /utensils/"""
    utensil = {
        str(mock.sentinel.utensil_key): str(mock.sentinel.utensil)
    }
    mock_utensil = mock.MagicMock(wraps=utensil)
    mock_raise_or_return = mock.Mock(return_value=mock_utensil)
    mock_utensil_create = mock.Mock(return_value=mock.sentinel.utensil)
    mock_utensil_schema_dump = mock.Mock(return_value=(mock_utensil, None))

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr('db.models.Utensil.create', mock_utensil_create)
    monkeypatch.setattr('utils.schemas.utensil_schema.dump',
                        mock_utensil_schema_dump)

    schema = schemas.utensil_schema_post
    utensils_create_page = app.post('/utensils/', data=mock_utensil)

    assert utensils_create_page.status_code == 201
    assert utils.load(utensils_create_page) == {'utensil': utensil}
    assert mock_utensil_create.call_args_list == [mock.call(**utensil)]
    assert mock_raise_or_return.call_args_list == [mock.call(schema)]


def test_utensils_post_409(app, monkeypatch):
    """Test post /utensils/ with conflict"""
    mock_raise_or_return = mock.Mock(return_value=mock.MagicMock(spec=dict))
    mock_utensil_create = mock.Mock(side_effect=peewee.IntegrityError)

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr('db.models.Utensil.create', mock_utensil_create)

    utensils_create_page = app.post('/utensils/', data={})
    error_msg = {'message': 'Utensil already exists', 'status_code': 409}

    assert utensils_create_page.status_code == 409
    assert utils.load(utensils_create_page) == error_msg


def test_utensils_put(app, monkeypatch):
    """Test put /utensils/"""
    utensil = str(mock.sentinel.utensil)
    utensils = {'utensils': [utensil]}

    mock_raise_or_return = mock.Mock(return_value=utensils)
    mock_update_utensil = mock.Mock(return_value=utensil)

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr('api.utensils.update_utensil', mock_update_utensil)

    schema = schemas.utensil_schema_list
    utensils_update_page = app.put('/utensils/', data=utensils)

    assert utensils_update_page.status_code == 200
    assert utils.load(utensils_update_page) == utensils
    assert mock_update_utensil.call_args_list == [mock.call(utensil)]
    assert mock_raise_or_return.call_args_list == [mock.call(schema)]


def test_utensils_put_with_exception(app, monkeypatch):
    """Test put /utensils/ with possible conflict"""
    utensil = str(mock.sentinel.utensil)
    utensils = {'utensils': [utensil]}
    mock_raise_or_return = mock.Mock(return_value=utensils)
    mock_update_utensil = mock.Mock(side_effect=helpers.APIException('Error'))

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr('api.utensils.update_utensil', mock_update_utensil)

    utensils_update_page = app.put('/utensils/', data=utensils)

    update_calls = [mock.call(utensil)]
    assert utensils_update_page.status_code == 200
    assert utils.load(utensils_update_page) == {'utensils': []}
    assert mock_update_utensil.call_args_list == update_calls


def test_utensil_get(app, monkeypatch):
    """Test /utensils/<id>"""
    sentinel_utensil = mock.sentinel.utensil
    mock_get_utensil = mock.Mock(return_value=sentinel_utensil)
    mock_utensil_dump = mock.Mock(return_value=(str(sentinel_utensil), None))

    monkeypatch.setattr('api.utensils.get_utensil', mock_get_utensil)
    monkeypatch.setattr('utils.schemas.utensil_schema.dump', mock_utensil_dump)

    utensil_page = app.get('/utensils/1/')

    assert utensil_page.status_code == 200
    assert utils.load(utensil_page) == {'utensil': str(sentinel_utensil)}
    assert mock_get_utensil.call_args_list == [mock.call(1)]
    assert mock_utensil_dump.call_args_list == [mock.call(sentinel_utensil)]


def test_utensil_put(app, monkeypatch):
    """Test put /utensils/<id>"""
    utensil = str(mock.sentinel.utensil)
    mock_utensil = mock.MagicMock(spec=dict)
    mock_raise_or_return = mock.Mock(return_value=mock_utensil)
    mock_update_utensil = mock.Mock(return_value=utensil)

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr('api.utensils.update_utensil', mock_update_utensil)

    schema = schemas.utensil_schema_put
    utensil_put_page = app.put('/utensils/2/', data=utensil)

    assert utensil_put_page.status_code == 200
    assert utils.load(utensil_put_page) == {'utensil': utensil}
    assert mock_raise_or_return.call_args_list == [mock.call(schema)]
    assert mock_update_utensil.call_args_list == [mock.call(mock_utensil)]


def test_utensil_get_recipes(app, monkeypatch):
    """Test /utensils/<id>/recipes"""

    recipe = {str(mock.sentinel.recipe_key): str(mock.sentinel.recipe)}
    recipes = {'recipes': [recipe]}
    mock_recipes = mock.MagicMock(wraps=recipes, spec=dict)

    mock_get_utensil = mock.Mock()
    mock_select_recipes = mock.Mock(return_value=[mock.sentinel.recipe])
    mock_recipe_dump = mock.Mock(return_value=(mock_recipes, None))

    monkeypatch.setattr('api.utensils.get_utensil', mock_get_utensil)
    monkeypatch.setattr('api.recipes.select_recipes', mock_select_recipes)
    monkeypatch.setattr('utils.schemas.recipe_schema_list.dump',
                        mock_recipe_dump)

    utensil_recipes_page = app.get('/utensils/1/recipes/')

    select_recipes_calls = [mock.call(
        peewee.Expression(models.RecipeUtensils.utensil, peewee.OP.EQ, 1)
    )]

    assert utensil_recipes_page.status_code == 200
    assert utils.load(utensil_recipes_page) == recipes

    assert mock_get_utensil.call_args_list == [mock.call(1)]
    assert mock_select_recipes.call_args_list == select_recipes_calls
    assert mock_recipe_dump.call_args_list == [mock.call({
        'recipes': [mock.sentinel.recipe]
    })]

