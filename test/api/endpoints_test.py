import pytest
import api

@pytest.fixture
def app():
    api.app.config['TESTING'] = True
    return api.app.test_client()

def test_root(app):
    root = app.get('/')
    assert 'Hello World!' in root.data
