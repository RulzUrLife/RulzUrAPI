"""API utensils endpoint testing"""
import copy
import json
import unittest.mock as mock

import peewee
import pytest

import api.utensils
import db.models
import utils.schemas as schemas
import utils.helpers as helpers

import test.utils as utils


def test_get_utensil(monkeypatch):
    mock_utensil_get = mock.Mock(return_value=mock.sentinel.utensil)
    get_clause = peewee.Expression(db.models.Utensil.id, peewee.OP_EQ,
                                   mock.sentinel.utensil_id)

    monkeypatch.setattr('db.models.Utensil.get', mock_utensil_get)
    returned_utensil = api.utensils.get_utensil(mock.sentinel.utensil_id)

    assert returned_utensil is mock.sentinel.utensil
    assert mock_utensil_get.call_args_list == [mock.call(get_clause)]


def test_get_utensil_404(monkeypatch):
    mock_utensil_get = mock.Mock(side_effect=peewee.DoesNotExist)

    monkeypatch.setattr('db.models.Utensil.get', mock_utensil_get)
    with pytest.raises(helpers.APIException) as excinfo:
        api.utensils.get_utensil(None)

    assert excinfo.value.args == ('Utensil not found', 404, None)


def test_update_utensil(monkeypatch, utensil):
    utensil['id'] = mock.sentinel.utensil_id
    where_exp = peewee.Expression(db.models.Utensil.id, peewee.OP_EQ,
                                  mock.sentinel.utensil_id)

    mock_utensil_update = mock.Mock()
    where = mock_utensil_update.return_value.where
    returning = where.return_value.returning
    dicts = returning.return_value.dicts
    execute = dicts.return_value.execute
    execute.return_value = mock.sentinel.utensil

    monkeypatch.setattr('db.models.Utensil.update', mock_utensil_update)
    returned_utensil = api.utensils.update_utensil(utensil)

    assert returned_utensil is mock.sentinel.utensil
    assert mock_utensil_update.call_args_list == [mock.call(**utensil)]
    assert where.call_args_list == [mock.call(where_exp)]
    assert returning.call_args_list == [mock.call()]
    assert dicts.call_args_list == [mock.call()]
    assert execute.call_args_list == [mock.call()]


def test_update_utensil_404(monkeypatch, utensil):
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
    utensils_page = utils.send(app.get, '/utensils/')

    assert utensils_page.status_code == 200
    assert mock_utensil_select.call_args_list == [mock.call()]
    assert dicts.call_args_list == [mock.call()]
    assert utils.load(utensils_page) == utensils


def test_utensils_post(app, monkeypatch, utensil, utensil_no_id):
    """Test post /utensils/"""

    mock_raise_or_return = mock.Mock(return_value=utensil_no_id)
    mock_utensil_create = mock.Mock(return_value=utils.FakeModel(utensil))

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr('db.models.Utensil.create', mock_utensil_create)

    schema = schemas.utensil_schema_post
    utensils_create_page = utils.send(app.post,'/utensils/', utensil_no_id)

    assert utensils_create_page.status_code == 201
    assert utils.load(utensils_create_page) == {'utensil': utensil}
    assert mock_utensil_create.call_args_list == [mock.call(**utensil_no_id)]
    assert mock_raise_or_return.call_args_list == [mock.call(schema)]


def test_utensils_post_409(app, monkeypatch, utensil_no_id):
    mock_raise_or_return = mock.Mock(return_value=utensil_no_id)
    mock_utensil_create = mock.Mock(side_effect=peewee.IntegrityError)

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr('db.models.Utensil.create', mock_utensil_create)

    utensils_create_page = utils.send(app.post,'/utensils/', utensil_no_id)
    error_msg = {'message': 'Utensil already exists'}

    assert utensils_create_page.status_code == 409
    assert utils.load(utensils_create_page) == error_msg


def test_utensils_put(app, monkeypatch, utensils):
    """Test put /utensils/"""

    mock_raise_or_return = mock.Mock(return_value=utensils)
    mock_update_utensil = mock.Mock(side_effect=iter(utensils['utensils']))

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr('api.utensils.update_utensil', mock_update_utensil)

    schema = schemas.utensil_schema_list
    utensils_update_page = utils.send(app.put,'/utensils/', utensils)

    update_calls = [mock.call(utensil) for utensil in utensils['utensils']]
    assert utensils_update_page.status_code == 200
    assert utils.load(utensils_update_page) == utensils
    assert mock_update_utensil.call_args_list == update_calls
    assert mock_raise_or_return.call_args_list == [mock.call(schema)]


def test_utensils_put_with_exception(app, monkeypatch, utensils):
    update_utensil_returns = iter([
        helpers.APIException('Error') for _ in range(len(utensils['utensils']))
    ])
    mock_raise_or_return = mock.Mock(return_value=utensils)
    mock_update_utensil = mock.Mock(side_effect=update_utensil_returns)

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr('api.utensils.update_utensil', mock_update_utensil)

    utensils_update_page = utils.send(app.put,'/utensils/', utensils)

    update_calls = [mock.call(utensil) for utensil in utensils['utensils']]
    assert utensils_update_page.status_code == 200
    assert utils.load(utensils_update_page) == {'utensils': []}
    assert mock_update_utensil.call_args_list == update_calls


def test_utensil_get(app, monkeypatch, utensil):
    """Test /utensils/<id>"""
    sentinel_utensil = mock.sentinel.utensil
    mock_get_utensil = mock.Mock(return_value=sentinel_utensil)
    mock_utensil_dump = mock.Mock(return_value=(utensil, None))

    monkeypatch.setattr('api.utensils.get_utensil', mock_get_utensil)
    monkeypatch.setattr('utils.schemas.utensil_schema.dump', mock_utensil_dump)

    utensil_page = utils.send(app.get, '/utensils/1')

    assert utensil_page.status_code == 200
    assert utils.load(utensil_page) == {'utensil': utensil}
    assert mock_get_utensil.call_args_list == [mock.call(1)]
    assert mock_utensil_dump.call_args_list == [mock.call(sentinel_utensil)]


def test_utensil_put(app, monkeypatch, utensil):
    """Test put /utensils/<id>"""
    utensil_copy = copy.deepcopy(utensil)
    utensil_copy['id'] = 2

    mock_raise_or_return = mock.Mock(return_value=utensil)
    mock_update_utensil = mock.Mock(return_value=utensil)

    monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
    monkeypatch.setattr('api.utensils.update_utensil', mock_update_utensil)

    schema = schemas.utensil_schema_put
    utensil_put_page = utils.send(app.put, '/utensils/2', utensil)

    assert utensil_put_page.status_code == 200
    assert utils.load(utensil_put_page) == {'utensil': utensil}
    assert mock_raise_or_return.call_args_list == [mock.call(schema)]
    assert mock_update_utensil.call_args_list == [mock.call(utensil_copy)]


def test_utensil_get_recipes(app, monkeypatch, recipes):
    """Test /utensils/<id>/recipes"""

    mock_get_utensil = mock.Mock()
    mock_select_recipes = mock.Mock(return_value=recipes)
    mock_recipe_dump = mock.Mock(return_value=(recipes, None))

    monkeypatch.setattr('api.utensils.get_utensil', mock_get_utensil)
    monkeypatch.setattr('api.recipes.select_recipes', mock_select_recipes)
    monkeypatch.setattr('utils.schemas.recipe_schema.dump', mock_recipe_dump)

    utensil_recipes_page = utils.send(app.get, '/utensils/1/recipes')

