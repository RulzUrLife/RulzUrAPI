"""Configuration and fixture for api testing"""
import pytest
import mock
import types

@pytest.fixture
def error_missing_name():
    """Simple fixture for missing name error"""
    return (
        {
            'message': 'Request malformed',
            'errors': {'name': ['Missing data for required field.']}
        }
    )

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

@pytest.fixture
def returning_update_mocking():
    """Simple factory for creating a mock_returning_update"""

    def returning_update(returns):
        """Create a mock object for an update query and return it"""
        mock_returning_update = mock.Mock()

        mocking = (
            mock_returning_update.return_value
            .where.return_value
            .dicts.return_value
            .execute
        )
        if not isinstance(returns, types.GeneratorType):
            mocking = mocking.return_value.next

        if hasattr(returns, '__call__'):
            mocking.side_effect = returns
        else:
            mocking.return_value = returns

        return mock_returning_update

    return returning_update
