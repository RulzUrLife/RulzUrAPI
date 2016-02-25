import db.models as models
import test.api.utils as utils

import pytest
import collections

@pytest.fixture
def next_id(next_id):
    return next_id(models.Ingredient)


class TestIngredients(utils.TestSubEndpoint):
    endpoint = 'ingredients'
    E_404 = 'ingredient not found'
    E_409 = 'ingredient already exists'

    def test_list(self, client, ingredients):
        ingredients = {'ingredients': ingredients}
        super(TestIngredients, self).test_list(client, ingredients)


    def test_post(self, client, next_id):
        data = {'name': 'ingredient_1'}
        data_expected = {
            'ingredient': utils.dict_merge(data, {'id': next_id()})
        }
        super(TestIngredients, self).test_post(client, data, data_expected)


    def test_post_invalid(self, client):
        data = {'name': int()}
        errors = {'name': [utils.STRING]}

        super(TestIngredients, self).test_post_invalid(client, data, errors)


    def test_post_409(self, client, ingredient):
        super(TestIngredients, self).test_post_409(client, ingredient)


    def test_put_list(self, client, ingredients):
        ingredients[0]['name'] = 'ingredient_foo'
        ingredients[1]['name'] = 'ingredient_bar'
        exp = {'ingredients': ingredients}

        super(TestIngredients, self).test_put_list(client, ingredients, exp)


    def test_get(self, client, ingredient):
        exp = {'ingredient': ingredient}
        super(TestIngredients, self).test_get(client, ingredient['id'], exp)


    def test_get_404(self, client, next_id):
        super(TestIngredients, self).test_get_404(client, next_id())


    def test_put(self, client, ingredient):
        ingredient['name'] = 'ingredient_foo'
        exp = {'ingredient': ingredient}

        super(TestIngredients, self).test_put(client, ingredient, exp)


    def test_put_invalid(self, client):
        data = {'name': int()}
        errors = {'0': {'name': [utils.STRING], 'id': [utils.MISSING]}}
        super(TestIngredients, self).test_put_invalid(client, [data], errors)


    def test_put_404(self, client, next_id):
        ingredient = {'id': next_id(), 'name': 'ingredient_1'}
        super(TestIngredients, self).test_put_404(client, ingredient)


    def test_get_recipes(self, client, recipes, ingredients):
        res = client.get(
            utils.urlize(self.endpoint, ingredients[0]['id'], 'recipes')
        )
        for recipe in res.data['recipes']:
            utils.unorder_recipe(recipe)

        assert res.status_code == 200
        assert res.data == {'recipes': [utils.unorder_recipe(recipes[0])]}


    def test_get_recipes(self, client, recipes, ingredients):
        expected = {'recipes': [utils.unorder_recipe(recipes[0])]}
        id =  ingredients[0]['id']
        super(TestIngredients, self).test_get_recipes(client, id, expected)


    def test_get_recipes_404(self, client, next_id):
        super(TestIngredients, self).test_get_recipes_404(client, next_id())
