"""Configuration and fixture for unit testing"""
import pytest
import api

@pytest.fixture(autouse=True)
def app():
    """Load flask in testing mode"""
    api.app.config['TESTING'] = True
    return api.app.test_client()


@pytest.fixture
def fake_model_factory():
    """Provide a factory for creating FakeModel instances from datas"""

    #pylint: disable=too-few-public-methods
    class FakeModel(object):
        """Fake model mocks BaseModel

        It only mocks the to_dict method to ease testing
        """
        def __init__(self, data):
            self.data = data

        def to_dict(self):
            """Clone the to_dict function from db.models.BaseModel"""
            return self.data

    return FakeModel
