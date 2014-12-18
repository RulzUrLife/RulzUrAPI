"""API endpoints testing"""
import pytest
import api
import json

@pytest.fixture()
def app():
    """Load flask in testing mode"""
    api.app.config['TESTING'] = True
    return api.app.test_client()


#pylint: disable=redefined-outer-name
def test_root(app, monkeypatch):
    """Test the / route from the API"""

    def list_table_mock(schema):
        """Mock a list of tables"""
        assert schema == 'rulzurkitchen'
        return ['table1', 'table2']

    monkeypatch.setattr('db.connector.database.get_tables', list_table_mock)
    root = app.get('/')
    assert json.loads(root.data) == {'tables': ['table1', 'table2']}
