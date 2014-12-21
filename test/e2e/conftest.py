"""Test configuration for the database testing (integration testing)"""
import logging
import os

import pytest

import db.connector
import db.models

SCHEMA_TEST_NAME = 'test_rulzurkitchen'
DEBUG = False

# Print all queries to stderr if debug enabled
if int(os.environ.get('DEBUG', 0)) != 0:
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


@pytest.fixture(autouse=True, scope='session')
def create_test_db(request):
    """Create a schema for testing the application

    This use the clone_schema stored function from the database registry,
    the clone_schema only copies tables and sequences but no datas
    """

    def delete_test_db():
        """Delete the schema used by the test"""
        db.connector.database.execute_sql(
            'DROP SCHEMA IF EXISTS %s CASCADE' % SCHEMA_TEST_NAME)

    delete_test_db()
    db.connector.database.execute_sql(
        'SELECT clone_schema(%s, %s)', (
            db.connector.schema, SCHEMA_TEST_NAME))
    request.addfinalizer(delete_test_db)


@pytest.fixture()
def models():
    """List all models used in those tests

    The models can't be retrieved automatically because the order must be
    respected for the deletion phase
    """
    return [
        db.models.RecipeUtensils,
        db.models.RecipeIngredients,
        db.models.Recipe,
        db.models.Utensil,
        db.models.Ingredient,
    ]


@pytest.fixture(autouse=True)
#pylint: disable=redefined-outer-name
def patch_models(models):
    """Patch the models in order to give them the cloned schema"""
    for model in models:
        #pylint: disable=protected-access
        model._meta.schema = SCHEMA_TEST_NAME


@pytest.fixture(autouse=True)
#pylint: disable=redefined-outer-name
def clean_db(request, models):
    """Delete datas for all the models (tables)

    This function is ran after each test in order to be sure that the database
    is clean between each test
    """

    def clean():
        """Apply the sql statement for deletion on each model"""
        return [model.delete().execute() for model in  models]

    request.addfinalizer(clean)


def pytest_ignore_collect(*_):
    """Disable the collect if not on docker environment

    Those are integration tests and can not be ran on Travis CI
    """
    addr = os.environ.get('RULZURDB_PORT_5432_TCP_ADDR')
    port = os.environ.get('RULZURDB_PORT_5432_TCP_PORT')

    if not (bool(addr) and bool(port)):
        # instanciate db connection
        db.connector.database.init(**db.connector.config)

        return True
    else:
        return False
