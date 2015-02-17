"""Configuration and fixture for api testing"""
import pytest
import unittest.mock as mock

@pytest.fixture
def error_missing_name():
    """Simple fixture for missing name error"""
    return {
        'message': 'Request malformed',
        'errors': {'name': ['Missing data for required field.']},
        'status': 400
    }


@pytest.fixture
def post_recipe_fixture():
    """Simple fixture to post a recipe"""
    return {
        'name': 'recipe_1',
        'difficulty': 1,
        'people': 2,
        'duration': '0/5',
        'category': 'starter',
        'directions': {},
        'utensils': [
            {'name': 'utensil_1'},
            {'name': 'utensil_2'},
            {'id': 3},
            {'id': 4},
        ],
        'ingredients': [
            {'name': 'ingredient_1', 'measurement': 'L', 'quantity': 1},
            {'name': 'ingredient_2', 'measurement': 'g', 'quantity': 2},
            {'id': 3, 'measurement': 'oz', 'quantity': 3},
            {'id': 4, 'measurement': 'spoon', 'quantity': 4},
        ]
    }


@pytest.fixture
def post_recipe_fixture_no_id():
    """Remove the id entries from the previous fixture"""
    post_fixture = post_recipe_fixture()
    ingredients = post_fixture.pop('ingredients')
    utensils = post_fixture.pop('utensils')

    post_fixture['ingredients'] = ingredients[0:-2]
    post_fixture['utensils'] = utensils[0:-2]
    return post_fixture


@pytest.fixture
def put_recipes_fixture():
    """Fixture for updating multiple recipes"""
    put_fixture_1 = post_recipe_fixture()
    put_fixture_1['id'] = 1
    put_fixture_2 = {'id': 2, 'name': 'recipe_2'}
    return [put_fixture_1, put_fixture_2]


@pytest.fixture
def recipe_select_mocking(monkeypatch):
    """Simple factory for creating a mock_recipe_select"""

    def recipe_select(recipes):
        """Mock db.models.Recipe.select and return specified recipies"""

        mock_recipe_select = mock.Mock()
        (mock_recipe_select.return_value
         .join.return_value
         .where.return_value
         .dicts.return_value) = recipes

        monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)
        return mock_recipe_select

    return recipe_select

