import test.others.utils as utils
import pytest
import collections


ENDPOINT = 'utensils'
UTENSILS = [{'name': 'utensil_1'}, {'name': 'utensil_2'}]

@pytest.fixture
def utensils(client):
    return [client.post(ENDPOINT, data=utensil).data.pop('utensil')
            for utensil in UTENSILS]

class TestUtensils(utils.TestEndpoint):
    endpoint = ENDPOINT

    def test_list(self, client, utensils):
        super(TestUtensils, self).test_list(client, {'utensils': utensils})

    def test_post(self, client, utensils):
        data = {'name': 'utensil_foo'}
        data_expected = {
            'utensil': {
                'id': utils.next_id(utensils),
                'name': 'utensil_foo'
            }
        }
        super(TestUtensils, self).test_post(client, data, data_expected)

    def test_post_invalid(self, client):
        data = [{'name': int()}]
        errors = [{'name': ['Not a valid string.']}]

        super(TestUtensils, self).test_post_invalid(client, zip(data, errors))

    def test_post_409(self, client, utensils):
        super(TestUtensils, self).test_post_409(
            client, utensils.pop(), 'utensil already exists'
        )

    def test_put_list(self, client, utensils):
        utensils[0]['name'] = 'utensil_foo'
        utensils[1]['name'] = 'utensil_bar'
        super(TestUtensils, self).test_put_list(
            client, utensils, {'utensils': utensils}
        )

    def test_get(self, client, utensils):
        data_expected = utensils.pop()
        super(TestUtensils, self).test_get(
            client, data_expected['id'], {'utensil': data_expected}
        )

    def test_get_404(self, client, utensils):
        super(TestUtensils, self).test_get_404(
            client, utils.next_id(utensils), 'utensil not found'
        )

    def test_put(self, client, utensils):
        data = utensils.pop()
        data['name'] = 'utensil_foo'

        super(TestUtensils, self).test_put(client, data, {'utensil': data})

    def test_put_404(self, client, utensils):
        super(TestUtensils, self).test_put_404(
            client, {'id': utils.next_id(utensils), 'name': 'foo'},
            'utensil not found'
        )
