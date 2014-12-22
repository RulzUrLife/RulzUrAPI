"""API ingredients endpoint testing"""
import json
import peewee
import mock
import db.models

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
    mock_ingredient_select.assert_called_once_with()
    assert json.loads(ingredients_page.data) == {'ingredients': ingredients}

def test_ingredient_get(app, monkeypatch, fake_model_factory):
    """Test /ingredients/<id>"""

    ingredient = {'ingredient_1': 'ingredient_1_content'}

    mock_ingredient_get = mock.Mock(return_value=fake_model_factory(ingredient))
    monkeypatch.setattr('db.models.Ingredient.get', mock_ingredient_get)
    ingredient_page = app.get('/ingredients/1')
    mock_ingredient_get.assert_called_once_with(
        peewee.Expression(db.models.Ingredient.id, '=', 1)
    )
    assert json.loads(ingredient_page.data) == {'ingredient': ingredient}

def test_ingredient_get_404(app, monkeypatch):
    """Test /ingredients/<id> with ingredient not found"""

    monkeypatch.setattr(
        'db.models.Ingredient.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    ingredient = app.get('/ingredients/2')
    assert ingredient.status_code == 404

def test_ingredient_get_recipes(app, monkeypatch):
    """Test /ingredients/<id>/recipes"""

    recipes = [{'recipe_1' : 'recipe_1_content'}]

    mock_ingredient_get = mock.Mock()
    monkeypatch.setattr('db.models.Ingredient.get', mock_ingredient_get)

    mock_recipe_select = mock.Mock()
    (mock_recipe_select.return_value
     .join.return_value
     .where.return_value
     .dicts.return_value) = recipes

    monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)

    ingredients_page = app.get('/ingredients/1/recipes')

    mock_ingredient_get.assert_called_once_with(
        peewee.Expression(db.models.Ingredient.id, '=', 1)
    )

    mock_recipe_select.assert_called_once_with()

    mock_recipe_select.return_value.join.assert_called_once_with(
        db.models.RecipeIngredients
    )
    (mock_recipe_select.return_value
     .join.return_value
     .where.assert_called_once_with(
         peewee.Expression(db.models.RecipeIngredients.ingredient, '=', 1)
     )
    )

    assert json.loads(ingredients_page.data) == {'recipes': recipes}

def test_ingredient_get_recipes_404(app, monkeypatch):
    """Test /ingredients/<id>/recipes with ingredient not found"""

    monkeypatch.setattr(
        'db.models.Ingredient.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    ingredient = app.get('/ingredients/2/recipes')
    assert ingredient.status_code == 404

