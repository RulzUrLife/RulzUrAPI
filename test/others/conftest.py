import app as app_builder
import db

import os
import pytest
import collections
import json

@pytest.fixture
def app():
    if not 'RULZURAPI_SETTINGS' in os.environ:
        os.environ['RULZURAPI_SETTINGS'] = 'test.others.test_settings'
    return app_builder.create_app()

@pytest.fixture
@db.database.transaction()
def clean_db():
    tables = ['recipe_utensils', 'recipe_ingredients', 'recipe', 'utensil',
              'ingredient']
    for table in tables:
        query = 'DELETE FROM %s.%s' % (db.schema, table)
        db.models.BaseModel.raw(query).execute()

@pytest.fixture
def client(app, clean_db):
    attrs = ['status_code', 'data', 'headers']
    Response = collections.namedtuple('Response', attrs)

    headers = {'Content-Type': 'application/json'}

    def client_open_decorator(func):
        def wrapper(*args, **kwargs):
            data = kwargs.get('data')
            #if isinstance(data, dict):
            if data:
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
