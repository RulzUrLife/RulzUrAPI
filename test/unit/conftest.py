"""Configuration and fixture for unit testing"""
import contextlib
import imp
import json
import unittest.mock

import ipdb
import peewee
import pytest

import api
import db.connector
import test.utils

@pytest.fixture(autouse=True, scope='session')
def mock_transaction():
    """Replace the transaction decorator from peewee to a noop one"""

    noop_decorator = contextlib.contextmanager(lambda: (yield))

    db.connector.database.transaction = noop_decorator
    imp.reload(api.utensils)
    imp.reload(api.ingredients)
    imp.reload(api.recipes)
    imp.reload(api)


@pytest.fixture(autouse=True, scope='module')
def mock_connect(request):
    """Avoid connection by replacing the function with a noop one"""
    connect = db.connector.database.connect
    db.connector.database.connect = lambda: None

    def finalize():
        """Restore connect function for e2e tests"""
        db.connector.database.connect = connect

    request.addfinalizer(finalize)


# Override mock.call to be compliant with peewee __eq__ override
unittest.mock._Call = test.utils._Call # pylint: disable=protected-access
unittest.mock.MagicMock = test.utils.MagicMock

@pytest.fixture(autouse=True)
def app():
    """Load flask in testing mode"""

    def client_method_decorator(func):
        """Helper to send data from test to the application"""
        def wrapper(*args, **kwargs):
            """Dump the data dict into json and set content_type"""
            if not kwargs.get('content_type'):
                kwargs['content_type'] = 'application/json'
            data = kwargs.get('data')
            if data:
                kwargs['data'] = json.dumps(data, cls=test.utils.MockEncoder)

            return func(*args, **kwargs)

        return wrapper
    app_test = api.app
    app_test.config['TESTING'] = True
    app_test.json_encoder = test.utils.MockEncoder

    client = app_test.test_client()
    client.get = client_method_decorator(client.get)
    client.put = client_method_decorator(client.put)
    client.post = client_method_decorator(client.post)

    return client

def remove_id(elt):
    """Remove the "id" field of a dict like object"""
    elt.pop('id', None)
    return elt

@pytest.fixture
def debug():
    """Debugging fixture, helpers for mock.side_effect"""

    # pylint: disable=unused-argument
    def debug_fn(*args, **kwargs):
        """debugging function, accept inspection of args"""
        ipdb.set_trace()

    return debug_fn


@pytest.yield_fixture
# pylint: disable=redefined-outer-name
def request_context(app):
    """Provide a Flask request context for testing purpose"""

    with app.application.test_request_context() as req_context:
        yield req_context


@pytest.fixture
def utensil():
    """utensil fixture"""
    return {'id': 1, 'name': 'utensil_1'}

@pytest.fixture
def utensil_no_id():
    """utensil with no id fixture"""
    return remove_id(utensil())

@pytest.fixture
def utensils():
    """list of utensils fixture"""
    return {'utensils': [utensil(), utensil(), utensil()]}

@pytest.fixture
def ingredient():
    """ingredient fixture"""
    return {'id': 1, 'name': 'ingredient_1'}

@pytest.fixture
def ingredient_no_id():
    """ingredient with no id fixture"""
    return remove_id(ingredient())

@pytest.fixture
def ingredients():
    """list of ingredients fixture"""
    return {'ingredients': [ingredient(), ingredient(), ingredient()]}


@pytest.fixture
def recipe():
    """recipe fixture"""
    return {
        'id': 1,
        'name': 'recipe_1',
        'difficulty': 1,
        'people': 2,
        'duration': '0/5',
        'category': 'starter',
        'directions': {},
        'utensils': [{'id': 1}, {'name': 'utensil_2'}],
        'ingredients': [
            {'id': 1, 'measurement': 'L', 'quantity': 1},
            {'name': 'ingredient_2', 'measurement': 'oz', 'quantity': 1}
        ]
    }


@pytest.fixture
def recipe_no_id():
    """recipe with no id fixture"""
    return remove_id(recipe())

@pytest.fixture
def recipes():
    """list of recipe fixture"""
    return {'recipes': [recipe(), recipe()]}

@pytest.fixture
def model():
    """Create a fake model for testing purpose"""
    attrs = dict(id=peewee.PrimaryKeyField(), name=peewee.CharField())

    return type('FakeModel', (peewee.Model,), attrs)
