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

def test_ingredients_post(app, monkeypatch):
    """Test post /ingredients/"""
    ingredient = {'name': 'ingredient_1'}

    mock_ingredient_create = mock.Mock()
    mock_ingredient_create.return_value.to_dict.return_value = ingredient
    monkeypatch.setattr('db.models.Ingredient.create', mock_ingredient_create)
    ingredients_create_page = app.post(
        '/ingredients/', data=json.dumps(ingredient),
        content_type='application/json'
    )

    assert ingredients_create_page.status_code == 201
    assert json.loads(ingredients_create_page.data) == {
        'ingredient': ingredient
    }
    mock_ingredient_create.assert_called_once_with(**ingredient)

def test_ingredients_post_400(app):
    """Test post /ingredients/ with wrong parameters"""
    ingredient = {}

    ingredients_create_page = app.post(
        '/ingredients/', data=json.dumps(ingredient)
    )
    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == (
        {'message': 'No ingredient name provided'}
    )

def test_ingredients_put(app, monkeypatch):
    """Test put /ingredients/"""
    ingredients = [
        {'id': 1, 'name': 'ingredient_1'}, {'id': 2, 'name': 'ingredient_2'}
    ]
    ingredients_update = [
        {'id': 1, 'name': 'ingredient_1', 'desc': 'description_ingredient_1'},
        {'id': 2, 'name': 'ingredient_2', 'desc': 'description_ingredient_2'},
    ]

    def optimized_update_ingredient_generator():
        """Simple generator for optimized_update which returns ingredients"""
        for ingredient in ingredients_update:
            yield ingredient

    mock_optimized_update = mock.Mock()
    mock_optimized_update.return_value.execute.return_value = (
        optimized_update_ingredient_generator()
    )
    monkeypatch.setattr(
        'utils.helpers.optimized_update', mock_optimized_update
    )
    ingredients_update_page = app.put(
        '/ingredients/', data=json.dumps({'ingredients': ingredients}),
        content_type='application/json'
    )

    assert ingredients_update_page.status_code == 200
    assert json.loads(ingredients_update_page.data) == (
        {'ingredients': ingredients_update}
    )

def test_ingredients_put_cleanup_args(app, monkeypatch):
    """Test put /ingredients/ arguments cleaner"""
    ingredients = [{'id': 1, 'name': 'ingredient_1', 'foo': 'bar'}]

    mock_optimized_update_ingredient = mock.Mock()
    mock_optimized_update_ingredient.return_value.execute.return_value = []
    monkeypatch.setattr(
        'utils.helpers.optimized_update', mock_optimized_update_ingredient
    )
    app.put(
        '/ingredients/', data=json.dumps({'ingredients': ingredients}),
        content_type='application/json'
    )
    # get the first element of ingredients and remove the "foo" entry
    ingredient = ingredients.pop()
    ingredient.pop('foo')
    assert mock_optimized_update_ingredient.call_args[0][1] == ingredient

def test_ingredients_put_400(app, monkeypatch):
    """Test put /ingredients/ with wrong parameters"""
    ingredients = [{'id': 1, 'name': 'ingredient_1'}, {'name':'ingredient_2'}]

    mock_optimized_update_ingredient = mock.Mock()
    mock_optimized_update_ingredient.return_value.execute.return_value = []
    monkeypatch.setattr(
        'utils.helpers.optimized_update', mock_optimized_update_ingredient
    )

    ingredients_update_page = app.put(
        '/ingredients/', data=json.dumps({}), content_type='application/json'
    )
    assert ingredients_update_page.status_code == 400
    assert json.loads(ingredients_update_page.data) == (
        {'message': 'Missing required parameter ingredients in the JSON body'}
    )

    ingredients_update_page = app.put(
        '/ingredients/', data=json.dumps({'ingredients': ingredients}),
        content_type='application/json'
    )
    assert ingredients_update_page.status_code == 400
    assert json.loads(ingredients_update_page.data) == (
        {'message': 'id field not provided for all values'}
    )

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

def test_ingredient_put(app, monkeypatch):
    """Test put /ingredients/<id>"""
    ingredient = {'id': 1, 'name': 'ingredient_1'}
    ingredient_update = {
        'id': 1, 'name': 'ingredient_1', 'desc': 'description_ingredient_1'
    }

    mock_optimized_update = mock.Mock()
    (mock_optimized_update.return_value
     .execute.return_value
     .next.return_value) = ingredient_update

    monkeypatch.setattr(
        'utils.helpers.optimized_update', mock_optimized_update
    )
    ingredient_update_page = app.put(
        '/ingredients/1', data=json.dumps(ingredient),
        content_type='application/json'
    )

    assert ingredient_update_page.status_code == 200
    assert json.loads(ingredient_update_page.data) == (
        {'ingredient': ingredient_update}
    )

def test_ingredient_put_404(app, monkeypatch):
    """Test put /ingredients/<id> with ingredient not found"""
    ingredient = {'id': 1, 'name': 'ingredient_1'}

    mock_optimized_update_ingredient = mock.Mock()
    (mock_optimized_update_ingredient.return_value
     .execute.return_value
     .next.side_effect) = StopIteration()

    monkeypatch.setattr(
        'utils.helpers.optimized_update', mock_optimized_update_ingredient
    )
    ingredient_update_page = app.put(
        '/ingredients/1', data=json.dumps(ingredient),
        content_type='application/json'
    )

    assert ingredient_update_page.status_code == 404

def test_ingredient_put_cleanup_args(app, monkeypatch):
    """Test put /ingredients/<id> arguments cleaner"""
    ingredient = {'name': 'ingredient_1', 'foo': 'bar'}

    mock_optimized_update_ingredient = mock.Mock()
    (mock_optimized_update_ingredient.return_value
     .execute.return_value
     .next.return_value) = []
    monkeypatch.setattr(
        'utils.helpers.optimized_update', mock_optimized_update_ingredient
    )
    app.put(
        '/ingredients/1', data=json.dumps(ingredient),
        content_type='application/json'
    )
    # get the first element of ingredient and remove the "foo" entry
    ingredient.pop('foo')
    assert mock_optimized_update_ingredient.call_args[0][1] == ingredient


def test_ingredient_get_recipes(app, monkeypatch, recipe_select_mocking):
    """Test /ingredients/<id>/recipes"""

    recipes = [{'recipe_1' : 'recipe_1_content'}]

    mock_ingredient_get = mock.Mock()
    monkeypatch.setattr('db.models.Ingredient.get', mock_ingredient_get)

    mock_recipe_select = recipe_select_mocking(recipes)
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
