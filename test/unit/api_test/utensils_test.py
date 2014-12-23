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

