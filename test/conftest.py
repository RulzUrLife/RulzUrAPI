import app as app_builder

import db
import db.models as models
import db.utils

import utils.helpers

import pytest

import os
import fnmatch
import collections
import json


@pytest.fixture
def app():
    if not 'RULZURAPI_SETTINGS' in os.environ:
        os.environ['RULZURAPI_SETTINGS'] = 'test.test_settings'
    return app_builder.create_app()


@pytest.fixture
@pytest.mark.usefixtures('app')
@db.database.atomic()
def clean_db():
    # delete table content
    tables = [models.RecipeIngredients, models.RecipeUtensils,
              models.Ingredient, models.Utensil, models.Recipe]
    for table in tables:
        table.delete().execute()

    # reset id sequences
    sequences = [models.Ingredient.id.sequence, models.Utensil.id.sequence,
                 models.Recipe.id.sequence]
    for sequence in sequences:
        entity = db.utils.parse_entity(db.schema, sequence)
        db.database.execute_sql('ALTER SEQUENCE %s RESTART WITH 1' % (entity,))


@pytest.fixture
def client(app, clean_db):
    attrs = ['status_code', 'data', 'headers']
    Response = collections.namedtuple('Response', attrs)

    headers = {'Content-Type': 'application/json'}

    def client_open_decorator(func):
        def wrapper(*args, **kwargs):
            data = kwargs.get('data')
            if utils.helpers.is_iterable(data):
                kwargs['data'] = json.dumps(data)

            headers.update(kwargs.get('headers', {}))
            kwargs['headers'] = headers
            response = func(*args, **kwargs)

            response_data = json.loads(response.data.decode('utf8') or '{}')
            return Response(response.status_code, response_data,
                            response.headers)

        return wrapper

    client = app.test_client()
    client.open = client_open_decorator(client.open)

    return client


@pytest.yield_fixture
def gen_table(app):
    tables = []
    def make_table(table):
        table = type(table.__name__, (models.BaseModel, table,), {})
        table.create_table()
        tables.append(table)

        return table

    db.database.execute_sql('SET search_path TO %s,public' % db.schema)
    yield make_table

    for table in tables:
        table.drop_table()


@pytest.fixture
def next_id(app):
    def wrapper(model):
        entity = db.utils.parse_entity(model._meta.schema, model.id.sequence)

        return lambda: db.database.execute_sql(
            'SELECT last_value FROM %s' % (entity,)
        ).fetchone()[0]

    return wrapper
