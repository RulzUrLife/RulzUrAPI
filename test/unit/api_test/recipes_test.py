"""API endpoints testing"""
import copy
import json
import peewee
import mock
import db.models
import test.utils

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

def test_recipe_get(app, monkeypatch):
    """Test /recipes/<id>"""

    recipe = {'recipe_1': 'recipe_1_content'}

    mock_recipe_get = mock.Mock(return_value=test.utils.FakeModel(recipe))
    monkeypatch.setattr('db.models.Recipe.get', mock_recipe_get)
    recipe_page = app.get('/recipes/1')

    assert mock_recipe_get.call_count == 1
    assert test.utils.expression_assert(
        mock_recipe_get, peewee.Expression(db.models.Ingredient.id, '=', 1)
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

# pylint: disable=too-many-statements, too-many-locals
def test_recipes_post(app, monkeypatch, post_recipe_fixture):
    """Test post /ingredients/"""

    ingredients, ingredients_mock = [], []
    utensils, utensils_mock = [], []
    recipe_mock = copy.deepcopy(post_recipe_fixture)
    recipe_mock['id'] = 1
    recipe_mock = test.utils.FakeModel(recipe_mock)

    for i, ingredient in enumerate(post_recipe_fixture['ingredients']):
        ingredients.append({'name': ingredient['name']})
        ingredients_mock.append(
            test.utils.FakeModel({'id': i + 1, 'name': ingredient['name']})
        )

    for i, utensil in enumerate(post_recipe_fixture['utensils']):
        utensils.append({'name': utensil['name']})
        utensils_mock.append(
            test.utils.FakeModel({'id': i + 1, 'name': utensil['name']})
        )

    mock_execute_sql = mock.Mock()

    mock_recipe_select = mock.Mock()
    mock_recipe_create = mock.Mock()

    mock_ingredient_insert = mock.Mock()
    mock_ingredient_select = mock.Mock()

    mock_utensil_insert = mock.Mock()
    mock_utensil_select = mock.Mock()

    mock_recipe_utensils_insert = mock.Mock()
    mock_recipe_ingredients_insert = mock.Mock()

    monkeypatch.setattr('db.connector.database.execute_sql', mock_execute_sql)
    monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)
    monkeypatch.setattr('db.models.Recipe.create', mock_recipe_create)
    monkeypatch.setattr('db.models.Ingredient.select', mock_ingredient_select)
    monkeypatch.setattr(
        'db.models.Ingredient.insert_many_unique', mock_ingredient_insert
    )
    monkeypatch.setattr('db.models.Utensil.select', mock_utensil_select)
    monkeypatch.setattr(
        'db.models.Utensil.insert_many_unique', mock_utensil_insert
    )
    monkeypatch.setattr(
        'db.models.RecipeUtensils.insert_many', mock_recipe_utensils_insert
    )
    monkeypatch.setattr(
        'db.models.RecipeIngredients.insert_many',
        mock_recipe_ingredients_insert
    )

    mock_recipe_select.return_value.where.return_value.count.return_value = 0
    mock_recipe_create.return_value = recipe_mock
    mock_ingredient_select.return_value.where.return_value = ingredients_mock
    mock_utensil_select.return_value.where.return_value = utensils_mock

    recipes_create_page = app.post(
        '/recipes/', data=json.dumps(post_recipe_fixture),
        content_type='application/json'
    )

    execute = mock_ingredient_insert.return_value.execute
    assert mock_ingredient_insert.call_count == 1
    assert mock_ingredient_insert.call_args == mock.call(
        db.models.Ingredient.name, ingredients
    )
    assert execute.call_count == 1
    assert execute.call_args == mock.call()

    execute = mock_utensil_insert.return_value.execute
    assert mock_utensil_insert.call_count == 1
    assert mock_utensil_insert.call_args == mock.call(
        db.models.Utensil.name, utensils
    )
    assert execute.call_count == 1
    assert execute.call_args == mock.call

    post_recipe_fixture['id'] = 1

    ingredients = zip(ingredients_mock, post_recipe_fixture['ingredients'])
    ingredients_mock = []
    for fake_model, ingredient in ingredients:
        ingredient.pop('name')
        ingredient['ingredient'] = fake_model.to_dict()
        ingredients_mock.append(ingredient)

    post_recipe_fixture['ingredients'] = ingredients_mock
    post_recipe_fixture['utensils'] = [
        utensil.to_dict() for utensil in utensils_mock
    ]

    assert recipes_create_page.status_code == 201
    assert json.loads(recipes_create_page.data) == {
        'recipe': post_recipe_fixture
    }

def test_recipes_post_409(app, monkeypatch, post_recipe_fixture):
    """Test post conflict /recipes/"""

    mock_select = mock.Mock()

    monkeypatch.setattr('db.models.Recipe.select', mock_select)

    mock_select.return_value.where.return_value.count.return_value = 1
    ingredients_create_page = app.post(
        '/recipes/', data=json.dumps(post_recipe_fixture),
        content_type='application/json'
    )

    assert test.utils.expression_assert(
        mock_select.return_value.where,
        peewee.Expression(
            db.models.Recipe.name, '=', post_recipe_fixture.get('name')
        )
    )
    assert ingredients_create_page.status_code == 409
    assert json.loads(ingredients_create_page.data) == (
        {'message': 'Recipe already exists.'}
    )


def test_recipes_post_400(app, post_recipe_fixture):
    """Test http error 400 possibilities"""

    def post(data):
        """Simply post dumped data on /recipes/"""
        return app.post(
            '/recipes/', data=json.dumps(data), content_type='application/json'
        )

    error_message = {
        'errors': {'name': ['Missing data for required field.']},
        'message': 'Request malformed'
    }
    post_recipe_fixture.pop('name')
    ingredients_create_page = post(post_recipe_fixture)

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message

    post_recipe_fixture['difficulty'] = 0
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['difficulty'] = [
        'Difficulty level must be between 1 and 5.'
    ]

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message

    post_recipe_fixture['difficulty'] = 6
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['difficulty'] = [
        'Difficulty level must be between 1 and 5.'
    ]

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message


    post_recipe_fixture.pop('difficulty')
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['difficulty'] = [
        'Missing data for required field.'
    ]

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message


    post_recipe_fixture['people'] = 0
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['people'] = [
        'People number must be between 1 and 12.'
    ]

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message

    post_recipe_fixture['people'] = 13
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['people'] = [
        'People number must be between 1 and 12.'
    ]

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message


    post_recipe_fixture.pop('people')
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['people'] = ['Missing data for required field.']

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message

    post_recipe_fixture['duration'] = 'error'
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['duration'] = [
        'Duration value is not a valid one.'
    ]

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message


    post_recipe_fixture.pop('duration')
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['duration'] = ['Missing data for required field.']

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message

    post_recipe_fixture['category'] = 'test'
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['category'] = [
        'Recipe category is not a valid one '
        '(allowed values: starter, main, dessert).'
    ]

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message


    post_recipe_fixture.pop('category')
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['category'] = ['Missing data for required field.']

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message


    post_recipe_fixture.pop('directions')
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['directions'] = [
        'Missing data for required field.'
    ]

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message

    post_recipe_fixture.pop('utensils')
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['utensils'] = [
        'Missing data for required field.'
    ]

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message

    post_recipe_fixture.pop('ingredients')
    ingredients_create_page = post(post_recipe_fixture)
    error_message['errors']['ingredients'] = [
        'Missing data for required field.'
    ]

    assert ingredients_create_page.status_code == 400
    assert json.loads(ingredients_create_page.data) == error_message


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


    assert mock_recipe_get.call_count == 1
    assert test.utils.expression_assert(
        mock_recipe_get, peewee.Expression(db.models.Recipe.id, '=', 1)
    )

    assert mock_recipe_ingredients_select.call_count == 1
    assert mock_recipe_ingredients_select.call_args == mock.call(
        db.models.RecipeIngredients.quantity,
        db.models.RecipeIngredients.measurement,
        db.models.Ingredient
    )

    join = mock_recipe_ingredients_select.return_value.join
    assert join.call_count == 1
    assert join.call_args == mock.call(db.models.Ingredient)

    where = join.return_value.where
    assert where.call_count == 1
    assert test.utils.expression_assert(
        where, peewee.Expression(db.models.RecipeIngredients.recipe, '=', 1)
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

    monkeypatch.setattr('db.models.Utensil.select', mock_utensil_select)

    utensils_page = app.get('/recipes/1/utensils')

    assert mock_recipe_get.call_count == 1
    assert test.utils.expression_assert(
        mock_recipe_get, peewee.Expression(db.models.Recipe.id, '=', 1)
    )

    assert mock_utensil_select.call_count == 1
    assert mock_utensil_select.call_args == mock.call()

    join = mock_utensil_select.return_value.join
    assert join.call_count == 1
    assert join.call_args == mock.call(db.models.RecipeUtensils)

    where = join.return_value.where
    assert where.call_count == 1
    assert test.utils.expression_assert(
        where, peewee.Expression(db.models.RecipeUtensils.recipe, '=', 1)
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

