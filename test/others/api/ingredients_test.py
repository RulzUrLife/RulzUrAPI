import test.others.utils as utils
import pytest
import collections


ENDPOINT = 'ingredients'
INGREDIENTS = [{'name': 'ingredient_1'}, {'name': 'ingredient_2'}]

@pytest.fixture
def ingredients(client):
    return [client.post(ENDPOINT, data=ingredient).data.pop('ingredient')
            for ingredient in INGREDIENTS]

class TestIngredients(utils.TestEndpoint):
    endpoint = ENDPOINT

    def test_list(self, client, ingredients):
        ingredients = {'ingredients': ingredients}
        super(TestIngredients, self).test_list(client, ingredients)

    def test_post(self, client, ingredients):
        data = {'name': 'ingredient_foo'}
        data_expected = {
            'ingredient': {
                'id': utils.next_id(ingredients),
                'name': 'ingredient_foo'
            }
        }
        super(TestIngredients, self).test_post(client, data, data_expected)

    # test post extra

    def test_post_invalid(self, client):
        data = [{'name': int()}]
        errors = [{'name': ['Not a valid string.']}]

        super(TestIngredients, self).test_post_invalid(
            client, zip(data, errors)
        )

    def test_post_409(self, client, ingredients):
        super(TestIngredients, self).test_post_409(
            client, ingredients.pop(), 'ingredient already exists'
        )

    def test_put_list(self, client, ingredients):
        ingredients[0]['name'] = 'ingredient_foo'
        ingredients[1]['name'] = 'ingredient_bar'

        super(TestIngredients, self).test_put_list(
            client, ingredients, {'ingredients': ingredients}
        )

    def test_get(self, client, ingredients):
        data_expected = ingredients.pop()
        super(TestIngredients, self).test_get(
            client, data_expected['id'], {'ingredient': data_expected}
        )

    def test_get_404(self, client, ingredients):
        super(TestIngredients, self).test_get_404(
            client, utils.next_id(ingredients), 'ingredient not found'
        )

    def test_put(self, client, ingredients):
        data = ingredients.pop()
        data['name'] = 'ingredient_foo'

        super(TestIngredients, self).test_put(
            client, data, {'ingredient': data}
        )

    def test_put_404(self, client, ingredients):
        super(TestIngredients, self).test_put_404(
            client, {'id': utils.next_id(ingredients), 'name': 'foo'},
            'ingredient not found'
        )
