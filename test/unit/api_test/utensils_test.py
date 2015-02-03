"""API utensils endpoint testing"""
import json
import peewee
import mock
import db.models
import test.utils

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
    assert test.utils.load(utensils_page) == {'utensils': utensils}

def test_utensils_post(app, monkeypatch):
    """Test post /utensils/"""
    utensil = {'name': 'utensil_1'}
    utensil_mock = {'id': 1, 'name': 'utensil_1'}

    mock_utensil_create = mock.Mock()
    mock_utensil_create.return_value = test.utils.FakeModel(utensil_mock)
    monkeypatch.setattr('db.models.Utensil.create', mock_utensil_create)
    utensils_create_page = app.post(
        '/utensils/', data=json.dumps(utensil), content_type='application/json'
    )

    assert utensils_create_page.status_code == 201
    assert test.utils.load(utensils_create_page) == {'utensil': utensil_mock}

    assert mock_utensil_create.call_count == 1
    assert mock_utensil_create.call_args == mock.call(**utensil)

def test_utensils_post_400(app, error_missing_name):
    """Test post /utensils/ with wrong parameters"""
    utensil = {}

    utensils_create_page = app.post(
        '/utensils/', data=json.dumps(utensil), content_type='application/json'
    )
    assert utensils_create_page.status_code == 400
    assert test.utils.load(utensils_create_page) == error_missing_name

def test_utensils_put(app, returning_update_mocking, monkeypatch):
    """Test put /utensils/"""
    utensils = [{'id': 1, 'name': 'utensil_1'}, {'id': 2, 'name': 'utensil_2'}]
    utensils_update = [
        {'id': 1, 'name': 'utensil_1', 'desc': 'description_utensil_1'},
        {'id': 2, 'name': 'utensil_2', 'desc': 'description_utensil_2'},
    ]

    def update_utensil_generator():
        """Simple generator for update which returns utensils"""
        for utensil in utensils_update:
            yield utensil

    mock_returning_update = returning_update_mocking(
        update_utensil_generator()
    )

    monkeypatch.setattr(
        'db.models.Utensil.update', mock_returning_update
    )
    utensils_update_page = app.put(
        '/utensils/', data=json.dumps({'utensils': utensils}),
        content_type='application/json'
    )

    calls = [mock.call(returning=True, **utensil) for utensil in utensils]

    assert mock_returning_update.has_calls(calls)
    assert utensils_update_page.status_code == 200
    assert test.utils.load(utensils_update_page) == (
        {'utensils': utensils_update}
    )

def test_utensils_put_cleanup_args(app, monkeypatch, returning_update_mocking):
    """Test put /utensils/ arguments cleaner"""
    utensils = [{'id': 1, 'name': 'utensil_1', 'foo': 'bar'}]

    mock_returning_update = returning_update_mocking({})
    monkeypatch.setattr(
        'db.models.Utensil.update', mock_returning_update
    )
    app.put(
        '/utensils/', data=json.dumps({'utensils': utensils}),
        content_type='application/json'
    )
    # get the first element of utensils and remove the "foo" entry
    utensil = utensils.pop()
    utensil.pop('foo')
    utensil.pop('id')
    assert mock_returning_update.call_count == 1
    assert mock_returning_update.call_args == mock.call(
        returning=True, **utensil
    )


def test_utensils_put_400(app):
    """Test put /utensils/ with wrong parameters"""
    utensils = [{'id': 1, 'name': 'utensil_1'}, {'name':'utensil_2'}]

    utensils_update_page = app.put(
        '/utensils/', data=json.dumps({}), content_type='application/json'
    )
    assert utensils_update_page.status_code == 400
    assert test.utils.load(utensils_update_page) == (
        {
            'message': 'Request malformed',
            'errors': {'utensils': ['Missing data for required field.']}
        }
    )

    utensils_update_page = app.put(
        '/utensils/', data=json.dumps({'utensils': utensils}),
        content_type='application/json'
    )
    assert utensils_update_page.status_code == 400
    assert test.utils.load(utensils_update_page) == (
        {
            'message': 'Request malformed',
            'errors': {
                'utensils': {'id': ['Missing data for required field.']}
            }
        }
    )

def test_utensil_get(app, monkeypatch):
    """Test /utensils/<id>"""

    utensil = {'id': 1, 'name': 'utensil_1'}

    mock_utensil_get = mock.Mock(return_value=test.utils.FakeModel(utensil))
    monkeypatch.setattr('db.models.Utensil.get', mock_utensil_get)
    utensil_page = app.get('/utensils/1')

    assert mock_utensil_get.call_count == 1
    assert test.utils.expression_assert(
        mock_utensil_get,
        peewee.Expression(db.models.Utensil.id, '=', 1)
    )
    assert test.utils.load(utensil_page) == {'utensil': utensil}


def test_utensil_get_404(app, monkeypatch):
    """Test /utensils/<id> with utensil not found"""

    monkeypatch.setattr(
        'db.models.Utensil.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    utensil = app.get('/utensils/2')
    assert utensil.status_code == 404

def test_utensil_put(app, returning_update_mocking, monkeypatch):
    """Test put /utensils/<id>"""
    utensil = {'name': 'utensil_1'}
    utensil_update = {
        'id': 1, 'name': 'utensil_1', 'desc': 'description_utensil_1'
    }

    mock_returning_update = returning_update_mocking(utensil_update)

    monkeypatch.setattr(
        'db.models.Utensil.update', mock_returning_update
    )
    utensil_update_page = app.put(
        '/utensils/1', data=json.dumps(utensil),
        content_type='application/json'
    )

    assert mock_returning_update.call_count == 1
    assert mock_returning_update.call_args == mock.call(
        returning=True, **utensil
    )
    assert utensil_update_page.status_code == 200
    assert test.utils.load(utensil_update_page) == utensil_update

def test_utensil_put_cleanup_args(app, returning_update_mocking, monkeypatch):
    """Test put /utensils/<id> arguments cleaner"""
    utensil = {'name': 'utensil_1', 'foo': 'bar'}

    mock_returning_update = returning_update_mocking({})
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
    assert mock_returning_update.call_args == mock.call(
        returning=True, **utensil
    )


def test_utensil_put_404(app, returning_update_mocking, monkeypatch):
    """Test put /utensils/<id> with utensil not found"""
    utensil = {'id': 1, 'name': 'utensil_1'}

    mock_returning_update = returning_update_mocking(StopIteration)

    monkeypatch.setattr(
        'db.models.Utensil.update', mock_returning_update
    )
    utensil_update_page = app.put(
        '/utensils/1', data=json.dumps(utensil),
        content_type='application/json'
    )

    assert utensil_update_page.status_code == 404

def test_utensil_get_recipes(app, monkeypatch, recipe_select_mocking):
    """Test /utensils/<id>/recipes"""

    recipes = [{'recipe_1' : 'recipe_1_content'}]

    mock_utensil_get = mock.Mock()
    monkeypatch.setattr('db.models.Utensil.get', mock_utensil_get)

    mock_recipe_select = recipe_select_mocking(recipes)
    recipes_page = app.get('/utensils/1/recipes')

    assert mock_utensil_get.call_count == 1
    assert test.utils.expression_assert(
        mock_utensil_get, peewee.Expression(db.models.Utensil.id, '=', 1)
    )

    assert mock_recipe_select.call_count == 1
    assert mock_recipe_select.call_args == mock.call()

    join = mock_recipe_select.return_value.join
    assert join.call_count == 1
    assert join.call_args == mock.call(db.models.RecipeUtensils)

    where = join.return_value.where
    assert where.call_count == 1
    assert test.utils.expression_assert(
        where, peewee.Expression(db.models.RecipeUtensils.utensil, '=', 1)
    )

    assert test.utils.load(recipes_page) == {'recipes': recipes}

def test_utensil_get_recipes_404(app, monkeypatch):
    """Test /utensils/<id>/recipes with utensil not found"""

    monkeypatch.setattr(
        'db.models.Utensil.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    utensil = app.get('/utensils/2/recipes')
    assert utensil.status_code == 404

