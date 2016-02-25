import db.models as models
import test.api.utils as utils

import pytest
import collections


@pytest.fixture
def next_id(next_id):
    return next_id(models.Utensil)

class TestUtensils(utils.TestSubEndpoint):
    endpoint = 'utensils'
    E_404 = 'utensil not found'
    E_409 = 'utensil already exists'


    def test_list(self, client, utensils):
        utensils = {'utensils': utensils}
        super(TestUtensils, self).test_list(client, utensils)


    def test_post(self, client, next_id):
        data = {'name': 'utensil_1'}
        data_expected = {
            'utensil': utils.dict_merge(data, {'id': next_id()})
        }
        super(TestUtensils, self).test_post(client, data, data_expected)

    # test post extra

    def test_post_invalid(self, client):
        data = {'name': int()}
        errors = {'name': [utils.STRING]}

        super(TestUtensils, self).test_post_invalid(client, data, errors)


    def test_post_409(self, client, utensil):
        super(TestUtensils, self).test_post_409(client, utensil)


    def test_put_list(self, client, utensils):
        utensils[0]['name'] = 'utensil_foo'
        utensils[1]['name'] = 'utensil_bar'
        expected = {'utensils': utensils}

        super(TestUtensils, self).test_put_list(client, utensils, expected)


    def test_get(self, client, utensil):
        expected = {'utensil': utensil}
        super(TestUtensils, self).test_get(client, utensil['id'], expected)


    def test_get_404(self, client, next_id):
        super(TestUtensils, self).test_get_404(client, next_id())


    def test_put(self, client, utensil):
        utensil['name'] = 'utensil_foo'
        expected = {'utensil': utensil}
        super(TestUtensils, self).test_put(client, utensil, expected)


    def test_put_invalid(self, client):
        data = {'name': int()}
        errors = {'0': {'name': [utils.STRING], 'id': [utils.MISSING]}}
        super(TestUtensils, self).test_put_invalid(client, [data], errors)


    def test_put_404(self, client, next_id):
        utensil = {'id': next_id(), 'name': 'utensil_1'}
        super(TestUtensils, self).test_put_404(client, utensil)


    def test_get_recipes(self, client, recipes, utensils):
        expected = {'recipes': [utils.unorder_recipe(recipes[0])]}
        id =  utensils[0]['id']
        super(TestUtensils, self).test_get_recipes(client, id, expected)


    def test_get_recipes_404(self, client, next_id):
        super(TestUtensils, self).test_get_recipes_404(client, next_id())
