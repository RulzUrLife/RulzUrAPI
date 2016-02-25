import abc
import utils.helpers



FULLFIL = ('More info about fulfilling this entity here: '
           'http://link/to/the/doc')
MISSING = 'Missing data for required field.'
STRING = 'Not a valid string.'
CHOICE = 'Not a valid choice.'
INTEGER = 'Not a valid integer.'
MULTIPLE = 'Multiple entries for the same element.'
CORRESPONDING = 'No corresponding id in database.'

dict_merge = utils.helpers.dict_merge

urlize = lambda *args: '/'.join([str(arg) for arg in args])

def sanitize_recipe(recipe):
    for key in ['ingredients', 'utensils']:
        for elt in recipe[key]:
            elt.pop('id')


def unorder_recipe(recipe):
    for key in ['ingredients', 'utensils']:
        recipe[key] = set(frozenset(elt.items()) for elt in recipe[key])
    return recipe


class TestEndpoint(abc.ABC):

    @staticmethod
    def _test_incorrect_json(method, endpoint):
        incorrect_datas = ['{', '"{"']
        data_expected = {
            'status_code': 400,
            'message': 'request malformed',
            'errors': 'JSON is incorrect'
        }
        res = method(endpoint)
        assert res.status_code == 400
        assert res.data == data_expected

        for data in incorrect_datas:
            res = method(endpoint, data=data)
            assert res.status_code == 400
            assert res.data == data_expected

    @abc.abstractmethod
    def test_list(self, client, data_expected, cb=None):
        res = client.get(self.endpoint)

        cb(res.data) if cb else None
        assert res.status_code == 200
        assert res.data == data_expected

    @abc.abstractmethod
    def test_post(self, client, data, data_expected, cb=None):
        res = client.post(self.endpoint, data=data)

        cb(res.data) if cb else None
        assert res.status_code == 201
        assert res.data == data_expected

    def test_post_incorrect_json(self, client):
        self._test_incorrect_json(client.post, self.endpoint)

    @abc.abstractmethod
    def test_post_invalid(self, client, data, errors):
        res = client.post(self.endpoint, data=data)

        assert res.status_code == 400
        assert res.data['status_code'] == 400
        assert res.data['message'] == 'request malformed'
        assert res.data['errors'] == errors

    @abc.abstractmethod
    def test_post_409(self, client, data):
        res = client.post(self.endpoint, data=data)

        assert res.status_code == 409
        assert res.data['message'] == self.E_409

    @abc.abstractmethod
    def test_put_list(self, client, data, data_expected):
        res = client.put(self.endpoint, data=data)

        assert res.status_code == 200
        assert res.data == data_expected

    @abc.abstractmethod
    def test_get(self, client, data_id, data_expected, cb=None):
        res = client.get('%s/%d' % (self.endpoint, data_id))

        cb(res.data) if cb else None
        assert res.status_code == 200
        assert res.data == data_expected

    @abc.abstractmethod
    def test_get_404(self, client, data_id):
        res = client.get('%s/%d' % (self.endpoint, data_id))

        assert res.status_code == 404
        assert res.data['message'] == self.E_404

    @abc.abstractmethod
    def test_put(self, client, data, data_expected):
        res = client.put('%s/%d' % (self.endpoint, data['id']), data=data)
        assert res.status_code == 200
        assert res.data == data_expected

    @abc.abstractmethod
    def test_put_invalid(self, client, data, errors):
        res = client.put(self.endpoint, data=data)

        assert res.status_code == 400
        assert res.data['status_code'] == 400
        assert res.data['message'] == 'request malformed'
        assert res.data['errors'] == errors


    def test_put_incorrect_json(self, client):
        endpoint = '%s/%d' % (self.endpoint, int())
        self._test_incorrect_json(client.put, endpoint)


    def test_put_empty_data(self, client):
        res = client.put('%s/%d' % (self.endpoint, int()), data={'foo': 'bar'})

        assert res.status_code == 400
        assert res.data == {
            'status_code': 400,
            'message': 'no data provided for update'
        }

    @abc.abstractmethod
    def test_put_404(self, client, data):
        res = client.put('%s/%d' % (self.endpoint, data['id']), data=data)

        assert res.status_code == 404
        assert res.data['message'] == self.E_404

class TestSubEndpoint(TestEndpoint):

    @abc.abstractmethod
    def test_get_recipes(self, client, id, expected):
        res = client.get(urlize(self.endpoint, id, 'recipes'))

        for recipe in res.data['recipes']:
            unorder_recipe(recipe)

        assert res.status_code == 200
        assert res.data == expected

    @abc.abstractmethod
    def test_get_recipes_404(self, client, id):
        res = client.get(urlize(self.endpoint, id, 'recipes'))

        assert res.status_code == 404
        assert res.data['status_code'] == 404
        assert res.data['message'] == self.E_404
