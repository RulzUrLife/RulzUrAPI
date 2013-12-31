import unittest
from api import app


class ViewsTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_root(self):
        root = self.app.get('/')
        assert 'Hello World!' in root.data

if __name__ == '__main__':
    unittest.main()
