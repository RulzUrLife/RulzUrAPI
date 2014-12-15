import inspect
import logging
import os

import pytest

import db.connector
import db.models

SCHEMA_TEST_NAME = 'test_rulzurkitchen'
DEBUG = False

# Print all queries to stderr if debug enabled
if DEBUG:
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


@pytest.fixture(autouse=True, scope='session')
def create_test_db(request):
    def delete_test_db():
        db.connector.database.execute_sql(
            'DROP SCHEMA IF EXISTS %s CASCADE' % SCHEMA_TEST_NAME)

    delete_test_db();
    db.connector.database.execute_sql(
        'SELECT clone_schema(%s, %s)', (
            db.connector.schema, SCHEMA_TEST_NAME))
    request.addfinalizer(delete_test_db)


@pytest.fixture()
def models():
    # The models can't be retrieved automatically because the order must be
    # respected for the deletion phase
    return [db.models.RecipeUtensils,
            db.models.RecipeIngredients,
            db.models.Recipe,
            db.models.Utensil,
            db.models.Ingredient,
            ]


@pytest.fixture(autouse=True)
def patch_models(models):
    for model in models:
        model._meta.schema = SCHEMA_TEST_NAME


@pytest.fixture(autouse=True)
def clean_db(request, models):
    def delete_function(model):
        q = model.delete()
        q.execute()

    def clean():
        map(delete_function, models)

    request.addfinalizer(clean)


# Those are integration tests and can not be ran on the CI
def pytest_ignore_collect(path, config):
    addr = os.environ.get('RULZURDB_PORT_5432_TCP_ADDR')
    port = os.environ.get('RULZURDB_PORT_5432_TCP_PORT')

    if not (bool(addr) and bool(port)):
        # instanciate db connection
        db.connector.database.init(**db.connector.config)

        return True
    else:
        return False
