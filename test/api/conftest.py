import pytest

def utensil_post(client, data):
    return client.post('utensils', data=data).data['utensil']

def ingredient_post(client, data):
    return client.post('ingredients', data=data).data['ingredient']

def recipe_post(client, data):
    return client.post('recipes', data=data).data['recipe']

@pytest.fixture
def utensil(client):
    return utensil_post(client, {'name': 'utensil_1'})

@pytest.fixture
def utensils(client):
    return [utensil_post(client, {'name': 'utensil_1'}),
            utensil_post(client, {'name': 'utensil_2'})]

@pytest.fixture
def ingredient(client):
    return ingredient_post(client, {'name': 'ingredient_1'})

@pytest.fixture
def ingredients(client):
    return [ingredient_post(client, {'name': 'ingredient_1'}),
            ingredient_post(client, {'name': 'ingredient_2'})]

@pytest.fixture
def recipe(client, ingredients, utensils):
    return recipe_post(client, {
        'name': 'recipe_1', 'difficulty': 1, 'people': 2, 'duration': '0/5',
        'category': 'starter',
        'directions': [
            {'title': 'step_1', 'text': 'instruction recipe 1 step 1'},
            {'title': 'step_2', 'text': 'instruction recipe 1 step 2'}
        ],
        'utensils': [
            {'id': utensils[0]['id']},
            {'name': utensils[1]['name']},
        ],
        'ingredients': [
            {'id': ingredients[0]['id'], 'measurement': 'L', 'quantity': 1},
            {
                'name': ingredients[1]['name'], 'measurement': 'g',
                'quantity': 2
            }
        ]
    })

@pytest.fixture
def recipes(client, recipe):
    recipe_2 = recipe_post(client, {
        'name': 'recipe_2', 'difficulty': 1, 'people': 2, 'duration': '0/5',
        'category': 'starter'
    })
    return [recipe, recipe_2]
