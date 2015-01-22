"""Configuration and fixture for unit testing"""
import pytest
import ipdb

import api
import db.connector

def mock_transaction():
    """Replace the transaction decorator from peewee to a noop one"""
    def noop_decorator():
        """noop decorator (do nothing)"""
        return lambda x: x

    db.connector.database.transaction = noop_decorator
    reload(api.utensils)
    reload(api.ingredients)
    reload(api.recipes)

mock_transaction()

@pytest.fixture(autouse=True)
def app():
    """Load flask in testing mode"""
    app_test = api.init_app()
    app_test.config['TESTING'] = True
    return app_test.test_client()

@pytest.fixture
def debug():
    """Debugging fixture, helpers for mock.side_effect"""

    # pylint: disable=unused-argument
    def debug_fn(*args, **kwargs):
        """debugging function, accept inspection of args"""
        ipdb.set_trace()

    return debug_fn


