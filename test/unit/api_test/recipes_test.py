"""API endpoints testing"""
import json
import peewee
import mock
import db.models

def test_recipes_list(app, monkeypatch):
    """Test /recipes/"""

    recipes = [
        {'recipe_1': 'recipe_1_content'},
        {'recipe_2': 'recipe_2_content'}
    ]

    mock_recipe_select = mock.Mock()
    mock_recipe_select.return_value.dicts.return_value = recipes
    monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)
    recipes_page = app.get('/recipes/')
    mock_recipe_select.assert_called_once_with()
    assert json.loads(recipes_page.data) == {'recipes': recipes}

def test_recipe_get(app, monkeypatch, fake_model_factory):
    """Test /recipes/<id>"""

    recipe = {'recipe_1': 'recipe_1_content'}

    mock_recipe_get = mock.Mock(return_value=fake_model_factory(recipe))
    monkeypatch.setattr('db.models.Recipe.get', mock_recipe_get)
    recipe_page = app.get('/recipes/1')
    mock_recipe_get.assert_called_once_with(
        peewee.Expression(db.models.Ingredient.id, '=', 1)
    )
    assert json.loads(recipe_page.data) == {'recipe': recipe}


def test_recipe_get_404(app, monkeypatch):
    """Test /recipes/<id> with recipe not found"""

    monkeypatch.setattr(
        'db.models.Recipe.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    recipe = app.get('/recipes/2')
    assert recipe.status_code == 404

def test_recipe_get_ingredients(app, monkeypatch):
    """Test /recipes/<id>/ingredients"""

    ingredients = [{'ingredient_1' : 'ingredient_1_content'}]

    mock_recipe_get = mock.Mock()
    monkeypatch.setattr('db.models.Recipe.get', mock_recipe_get)

    mock_recipe_ingredients_select = mock.Mock()
    (mock_recipe_ingredients_select.return_value
     .join.return_value
     .where.return_value
     .dicts.return_value) = ingredients

    monkeypatch.setattr(
        'db.models.RecipeIngredients.select',
        mock_recipe_ingredients_select
    )

    ingredients_page = app.get('/recipes/1/ingredients')

    mock_recipe_get.assert_called_once_with(
        peewee.Expression(db.models.Recipe.id, '=', 1)
    )
    mock_recipe_ingredients_select.assert_called_once_with(
        db.models.RecipeIngredients.quantity,
        db.models.RecipeIngredients.measurement,
        db.models.Ingredient
    )

    mock_recipe_ingredients_select.return_value.join.assert_called_once_with(
        db.models.Ingredient
    )

    (mock_recipe_ingredients_select.return_value
     .join.return_value
     .where.assert_called_once_with(
         peewee.Expression(db.models.RecipeIngredients.recipe, '=', 1)
     )
    )

    assert json.loads(ingredients_page.data) == {'ingredients': ingredients}


def test_recipe_get_ingredients_404(app, monkeypatch):
    """Test /recipes/<id>/ingredients with recipe not found"""

    monkeypatch.setattr(
        'db.models.Recipe.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    recipe = app.get('/recipes/2/ingredients')
    assert recipe.status_code == 404

def test_recipe_get_utensils(app, monkeypatch):
    """Test /recipes/<id>/utensils"""

    utensils = [{'utensil_1' : 'utensil_1_content'}]

    mock_recipe_get = mock.Mock()
    monkeypatch.setattr('db.models.Recipe.get', mock_recipe_get)

    mock_utensil_select = mock.Mock()
    (mock_utensil_select.return_value
     .join.return_value
     .where.return_value
     .dicts.return_value) = utensils

    monkeypatch.setattr(
        'db.models.Utensil.select',
        mock_utensil_select
    )

    utensils_page = app.get('/recipes/1/utensils')

    mock_recipe_get.assert_called_once_with(
        peewee.Expression(db.models.Recipe.id, '=', 1)
    )

    mock_utensil_select.assert_called_once_with()

    mock_utensil_select.return_value.join.assert_called_once_with(
        db.models.RecipeUtensils
    )

    (mock_utensil_select.return_value
     .join.return_value
     .where.assert_called_once_with(
         peewee.Expression(db.models.RecipeUtensils.recipe, '=', 1)
     )
    )

    assert json.loads(utensils_page.data) == {'utensils': utensils}


def test_recipe_get_utensils_404(app, monkeypatch):
    """Test /recipes/<id>/utensils with recipe not found"""

    monkeypatch.setattr(
        'db.models.Recipe.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    recipe = app.get('/recipes/2/utensils')
    assert recipe.status_code == 404

