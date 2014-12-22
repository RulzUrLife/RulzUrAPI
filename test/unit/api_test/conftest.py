"""Configuration and fixture for api testing"""
import pytest
import mock

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

