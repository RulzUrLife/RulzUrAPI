"""API utensils endpoint testing"""
import json
import peewee
import mock
import db.models

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
    mock_utensil_select.assert_called_once_with()
    assert json.loads(utensils_page.data) == {'utensils': utensils}

def test_utensils_post(app, monkeypatch):
    """Test post /utensils/"""
    utensil = {'name': 'utensil_1'}

    mock_utensil_create = mock.Mock()
    mock_utensil_create.return_value.to_dict.return_value = utensil
    monkeypatch.setattr('db.models.Utensil.create', mock_utensil_create)
    utensils_create_page = app.post(
        '/utensils/', data=json.dumps(utensil), content_type='application/json'
    )

    assert utensils_create_page.status_code == 201
    assert json.loads(utensils_create_page.data) == {'utensil': utensil}
    mock_utensil_create.assert_called_once_with(**utensil)

def test_utensils_post_400(app):
    """Test post /utensils/ with wrong parameters"""
    utensil = {}

    utensils_create_page = app.post('/utensils/', data=json.dumps(utensil))
    assert utensils_create_page.status_code == 400
    assert json.loads(utensils_create_page.data) == (
        {'message': 'No utensil name provided'}
    )

def test_utensils_put(app, monkeypatch):
    """Test put /utensils/"""
    utensils = [{'id': 1, 'name': 'utensil_1'}, {'id': 2, 'name': 'utensil_2'}]
    utensils_update = [
        {'id': 1, 'name': 'utensil_1', 'desc': 'description_utensil_1'},
        {'id': 2, 'name': 'utensil_2', 'desc': 'description_utensil_2'},
    ]

    def optimized_update_generator():
        """Simple generator for optimized_update which returns utensils"""
        for utensil in utensils_update:
            yield utensil

    mock_optimized_update = mock.Mock()
    mock_optimized_update.return_value.execute.return_value = (
        optimized_update_generator()
    )
    monkeypatch.setattr(
        'utils.helpers.optimized_update', mock_optimized_update
    )
    utensils_update_page = app.put(
        '/utensils/', data=json.dumps({'utensils': utensils}),
        content_type='application/json'
    )

    assert utensils_update_page.status_code == 200
    assert json.loads(utensils_update_page.data) == (
        {'utensils': utensils_update}
    )

def test_utensils_put_cleanup_args(app, monkeypatch):
    """Test put /utensils/ arguments cleaner"""
    utensils = [{'id': 1, 'name': 'utensil_1', 'foo': 'bar'}]

    mock_optimized_update = mock.Mock()
    mock_optimized_update.return_value.execute.return_value = []
    monkeypatch.setattr(
        'utils.helpers.optimized_update', mock_optimized_update
    )
    app.put(
        '/utensils/', data=json.dumps({'utensils': utensils}),
        content_type='application/json'
    )
    # get the first element of utensils and remove the "foo" entry
    utensil = utensils.pop()
    utensil.pop('foo')
    assert mock_optimized_update.call_args[0][1] == utensil


def test_utensils_put_400(app, monkeypatch):
    """Test put /utensils/ with wrong parameters"""
    utensils = [{'id': 1, 'name': 'utensil_1'}, {'name':'utensil_2'}]

    mock_optimized_update = mock.Mock()
    mock_optimized_update.return_value.execute.return_value = []
    monkeypatch.setattr(
        'utils.helpers.optimized_update', mock_optimized_update
    )

    utensils_update_page = app.put(
        '/utensils/', data=json.dumps({}), content_type='application/json'
    )
    assert utensils_update_page.status_code == 400
    assert json.loads(utensils_update_page.data) == (
        {'message': 'Missing required parameter utensils in the JSON body'}
    )

    utensils_update_page = app.put(
        '/utensils/', data=json.dumps({'utensils': utensils}),
        content_type='application/json'
    )
    assert utensils_update_page.status_code == 400
    assert json.loads(utensils_update_page.data) == (
        {'message': 'id field not provided for all values'}
    )

def test_utensil_get(app, monkeypatch, fake_model_factory):
    """Test /utensils/<id>"""

    utensil = {'utensil_1': 'utensil_1_content'}

    mock_utensil_get = mock.Mock(return_value=fake_model_factory(utensil))
    monkeypatch.setattr('db.models.Utensil.get', mock_utensil_get)
    utensil_page = app.get('/utensils/1')
    mock_utensil_get.assert_called_once_with(
        peewee.Expression(db.models.Utensil.id, '=', 1)
    )
    assert json.loads(utensil_page.data) == {'utensil': utensil}


def test_utensil_get_404(app, monkeypatch):
    """Test /utensils/<id> with utensil not found"""

    monkeypatch.setattr(
        'db.models.Utensil.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    utensil = app.get('/utensils/2')
    assert utensil.status_code == 404

def test_utensil_put(app, monkeypatch):
    """Test put /utensils/<id>"""
    utensil = {'id': 1, 'name': 'utensil_1'}
    utensil_update = {
        'id': 1, 'name': 'utensil_1', 'desc': 'description_utensil_1'
    }

    mock_optimized_update = mock.Mock()
    (mock_optimized_update.return_value
     .execute.return_value
     .next.return_value) = utensil_update

    monkeypatch.setattr(
        'utils.helpers.optimized_update', mock_optimized_update
    )
    utensil_update_page = app.put(
        '/utensils/1', data=json.dumps(utensil),
        content_type='application/json'
    )

    assert utensil_update_page.status_code == 200
    assert json.loads(utensil_update_page.data) == (
        {'utensil': utensil_update}
    )

def test_utensil_put_cleanup_args(app, monkeypatch):
    """Test put /utensils/<id> arguments cleaner"""
    utensil = {'name': 'utensil_1', 'foo': 'bar'}

    mock_optimized_update = mock.Mock()
    (mock_optimized_update.return_value
     .execute.return_value
     .next.return_value) = []
    monkeypatch.setattr(
        'utils.helpers.optimized_update', mock_optimized_update
    )
    app.put(
        '/utensils/1', data=json.dumps(utensil),
        content_type='application/json'
    )
    # get the first element of utensil and remove the "foo" entry
    utensil.pop('foo')
    assert mock_optimized_update.call_args[0][1] == utensil


def test_utensil_put_404(app, monkeypatch):
    """Test put /utensils/<id> with utensil not found"""
    utensil = {'id': 1, 'name': 'utensil_1'}

    mock_optimized_update = mock.Mock()
    (mock_optimized_update.return_value
     .execute.return_value
     .next.side_effect) = StopIteration()

    monkeypatch.setattr(
        'utils.helpers.optimized_update', mock_optimized_update
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

    mock_utensil_get.assert_called_once_with(
        peewee.Expression(db.models.Utensil.id, '=', 1)
    )

    mock_recipe_select.assert_called_once_with()
    mock_recipe_select.return_value.join.assert_called_once_with(
        db.models.RecipeUtensils
    )
    (mock_recipe_select.return_value
     .join.return_value
     .where.assert_called_once_with(
         peewee.Expression(db.models.RecipeUtensils.utensil, '=', 1)
     )
    )

    assert json.loads(recipes_page.data) == {'recipes': recipes}

def test_utensil_get_recipes_404(app, monkeypatch):
    """Test /utensils/<id>/recipes with utensil not found"""

    monkeypatch.setattr(
        'db.models.Utensil.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    utensil = app.get('/utensils/2/recipes')
    assert utensil.status_code == 404

