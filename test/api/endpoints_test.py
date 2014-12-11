import pytest
import api
import json

@pytest.fixture()
def app():
    api.app.config['TESTING'] = True
    return api.app.test_client()

def test_root(app, monkeypatch):
    def list_table_mock(schema):
        assert schema == 'rulzurkitchen'
        return ['table1', 'table2']

    monkeypatch.setattr('db.connector.database.get_tables', list_table_mock)
    root = app.get('/')
    assert json.loads(root.data) == {'tables': ['table1', 'table2']}
