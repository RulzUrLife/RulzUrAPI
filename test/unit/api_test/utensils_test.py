"""API utensils endpoint testing"""
import json
import peewee
import unittest.mock as mock
import db.models
import test.utils as utils

def test_utensils_list(app, monkeypatch):
    """Test /utensils/"""

    utensils = [
        {'utensil_1': 'utensil_1_content'},
        {'utensil_2': 'utensil_2_content'}
    ]

    mock_utensil_select = mock.Mock()
    mock_utensil_select.return_value.dicts.return_value = utensils
    monkeypatch.setattr('db.models.Utensil.select', mock_utensil_select)
    utensils_page = app.get('/utensils/')

    assert mock_utensil_select.call_count == 1
    assert mock_utensil_select.call_args == mock.call()
    assert utils.load(utensils_page) == {'utensils': utensils}

def test_utensils_post(app, monkeypatch):
    """Test post /utensils/"""
    utensil = {'name': 'utensil_1'}
    utensil_mock = {'id': 1, 'name': 'utensil_1'}

    mock_utensil_create = mock.Mock()
    mock_utensil_create.return_value = utils.FakeModel(utensil_mock)
    monkeypatch.setattr('db.models.Utensil.create', mock_utensil_create)
    utensils_create_page = app.post(
        '/utensils/', data=json.dumps(utensil), content_type='application/json'
    )

    assert utensils_create_page.status_code == 201
    assert utils.load(utensils_create_page) == {'utensil': utensil_mock}

    assert mock_utensil_create.call_count == 1
    assert mock_utensil_create.call_args == mock.call(**utensil)

def test_utensils_post_400(app, error_missing_name):
    """Test post /utensils/ with wrong parameters"""
    utensil = {}

    utensils_create_page = app.post(
        '/utensils/', data=json.dumps(utensil), content_type='application/json'
    )
    assert utensils_create_page.status_code == 400
    assert utils.load(utensils_create_page) == error_missing_name

def test_utensils_put(app, monkeypatch):
    """Test put /utensils/"""
    utensils_update = [
        {'id': 1, 'name': 'utensil_1', 'desc': 'description_utensil_1'},
        {'id': 2, 'name': 'utensil_2', 'desc': 'description_utensil_2'},
    ]
    utensils, update_calls = [], []

    for utensil in utensils_update:
        utensils.append({'id': utensil['id'], 'name': utensil['name']})
        update_calls.append(mock.call(name=utensil['name']))

    mock_returning_update = utils.update_mocking(iter(utensils_update))
    monkeypatch.setattr(
        'db.models.Utensil.update', mock_returning_update
    )
    utensils_update_page = app.put(
        '/utensils/', data=json.dumps({'utensils': utensils}),
        content_type='application/json'
    )
    assert mock_returning_update.call_args_list == update_calls
    assert utensils_update_page.status_code == 200
    assert utils.load(utensils_update_page) == (
        {'utensils': utensils_update}
    )

def test_utensils_put_cleanup_args(app, monkeypatch):
    """Test put /utensils/ arguments cleaner"""
    utensils = [
        {'id': 1, 'name': 'utensil_1', 'foo': 'bar'},
        {'id': 2, 'name': 'utensil_2', 'bar': 'foo'}
    ]

    mock_returning_update = utils.update_mocking(iter([{}, {}]))

    monkeypatch.setattr(
        'db.models.Utensil.update', mock_returning_update
    )
    app.put(
        '/utensils/', data=json.dumps({'utensils': utensils}),
        content_type='application/json'
    )
    # remove the extra entries
    utensil_2 = utensils.pop()
    utensil_2.pop('bar')
    utensil_2.pop('id')

    utensil_1 = utensils.pop()
    utensil_1.pop('foo')
    utensil_1.pop('id')

    assert mock_returning_update.call_count == 2
    assert mock_returning_update.call_args_list == [
        mock.call(**utensil_1), mock.call(**utensil_2)
    ]


def test_utensils_put_400(app):
    """Test put /utensils/ with wrong parameters"""
    utensils = [{'id': 1, 'name': 'utensil_1'}, {'name':'utensil_2'}]

    utensils_update_page = app.put(
        '/utensils/', data=json.dumps({}), content_type='application/json'
    )
    assert utensils_update_page.status_code == 400
    assert utils.load(utensils_update_page) == (
        {
            'message': 'Request malformed',
            'errors': {'utensils': ['Missing data for required field.']},
            'status': 400
        }
    )

    utensils_update_page = app.put(
        '/utensils/', data=json.dumps({'utensils': utensils}),
        content_type='application/json'
    )
    assert utensils_update_page.status_code == 400
    assert utils.load(utensils_update_page) == (
        {
            'message': 'Request malformed',
            'errors': {
                'utensils': {'id': ['Missing data for required field.']}
            },
            'status': 400
        }
    )

def test_utensil_get(app, monkeypatch):
    """Test /utensils/<id>"""

    utensil = {'id': 1, 'name': 'utensil_1'}

    mock_utensil_get = mock.Mock(return_value=utils.FakeModel(utensil))
    get_expr = peewee.Expression(db.models.Utensil.id, peewee.OP_EQ, 1)

    monkeypatch.setattr('db.models.Utensil.get', mock_utensil_get)
    utensil_page = app.get('/utensils/1')

    assert mock_utensil_get.call_count == 1
    assert utils.expression_assert(mock_utensil_get, get_expr)
    assert utils.load(utensil_page) == {'utensil': utensil}


def test_utensil_get_404(app, monkeypatch):
    """Test /utensils/<id> with utensil not found"""

    monkeypatch.setattr(
        'db.models.Utensil.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    utensil = app.get('/utensils/2')
    assert utensil.status_code == 404
    assert utils.load(utensil) == {
        'message': 'Utensil not found', 'status': 404
    }


def test_utensil_put(app, monkeypatch):
    """Test put /utensils/<id>"""
    utensil = {'name': 'utensil_1'}
    utensil_update = {
        'id': 1, 'name': 'utensil_1', 'desc': 'description_utensil_1'
    }
    where_expr = peewee.Expression(db.models.Utensil.id, peewee.OP_EQ,
                                   utensil_update['id'])

    mock_returning_update = mock.Mock()

    where = mock_returning_update.return_value.where
    returning = where.return_value.returning
    dicts = returning.return_value.dicts
    execute = dicts.return_value.execute
    execute.return_value = utensil_update

    monkeypatch.setattr(
        'db.models.Utensil.update', mock_returning_update
    )
    utensil_update_page = app.put(
        '/utensils/1', data=json.dumps(utensil),
        content_type='application/json'
    )

    assert mock_returning_update.call_args_list == [
        mock.call(name=utensil['name'])
    ]
    assert utils.expression_assert(where, where_expr)
    assert returning.call_args_list == [mock.call()]
    assert dicts.call_args_list == [mock.call()]

    assert execute.call_count == 1
    assert execute.call_args_list == [mock.call()]

    assert utensil_update_page.status_code == 200
    assert utils.load(utensil_update_page) == utensil_update

def test_utensil_put_cleanup_args(app, monkeypatch):
    """Test put /utensils/<id> arguments cleaner"""
    utensil = {'name': 'utensil_1', 'foo': 'bar'}

    mock_returning_update = utils.update_mocking({})

    monkeypatch.setattr(
        'db.models.Utensil.update', mock_returning_update
    )
    app.put(
        '/utensils/1', data=json.dumps(utensil),
        content_type='application/json'
    )
    # get the first element of utensil and remove the "foo" entry
    utensil.pop('foo')
    assert mock_returning_update.call_count == 1
    assert mock_returning_update.call_args == mock.call(**utensil)


def test_utensil_put_404(app, monkeypatch):
    """Test put /utensils/<id> with utensil not found"""
    utensil = {'id': 1, 'name': 'utensil_1'}

    mock_returning_update = utils.update_mocking(StopIteration)

    monkeypatch.setattr(
        'db.models.Utensil.update', mock_returning_update
    )
    utensil_update_page = app.put(
        '/utensils/1', data=json.dumps(utensil),
        content_type='application/json'
    )
    assert utensil_update_page.status_code == 404
    assert utils.load(utensil_update_page) == {
        'message': 'Utensil not found', 'status': 404
    }


def test_utensil_get_recipes(app, monkeypatch, recipe_select_mocking):
    """Test /utensils/<id>/recipes"""

    recipes = [{'recipe_1' : 'recipe_1_content'}]

    mock_utensil_get = mock.Mock()
    monkeypatch.setattr('db.models.Utensil.get', mock_utensil_get)

    mock_recipe_select = recipe_select_mocking(recipes)
    recipes_page = app.get('/utensils/1/recipes')

    get_expr = peewee.Expression(db.models.Utensil.id, '=', 1)
    where_expr = peewee.Expression(db.models.RecipeUtensils.utensil,
                                   peewee.OP_EQ, 1)

    assert mock_utensil_get.call_count == 1
    assert utils.expression_assert(mock_utensil_get, get_expr)

    assert mock_recipe_select.call_count == 1
    assert mock_recipe_select.call_args == mock.call()

    join = mock_recipe_select.return_value.join
    assert join.call_count == 1
    assert join.call_args == mock.call(db.models.RecipeUtensils)

    where = join.return_value.where
    assert where.call_count == 1
    assert utils.expression_assert(where, where_expr)

    assert utils.load(recipes_page) == {'recipes': recipes}

def test_utensil_get_recipes_404(app, monkeypatch):
    """Test /utensils/<id>/recipes with utensil not found"""

    monkeypatch.setattr(
        'db.models.Utensil.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    utensil = app.get('/utensils/2/recipes')
    assert utensil.status_code == 404
    assert utils.load(utensil) == {
        'message': 'Utensil not found', 'status': 404
    }

