"""Integration tests for models

Checks if models are valids by testing them against a clone of the database
"""

import db.models


def test_model():
    """Test insertions and linking"""

    ingredient_1 = db.models.Ingredient.create(name='test_ingredient_1')
    ingredient_2 = db.models.Ingredient.create(name='test_ingredient_2')

    assert ingredient_1.id == 1
    assert ingredient_2.id == 2

    utensil_1 = db.models.Utensil.create(name='test_utensil_1')
    utensil_2 = db.models.Utensil.create(name='test_utensil_2')

    assert utensil_1.id == 1
    assert utensil_2.id == 2

    recipe = db.models.Recipe.create(
        name='test_recipe',
        directions={
            'step 1': 'do whatever you want'
        },
        difficulty=1,
        people=1,
        duration='0/5',
        type='dessert'
    )
    assert recipe.id == 1

    db.models.RecipeIngredients.create(
        quantity=1,
        recipe=recipe,
        ingredient=ingredient_1,
        measurement='oz'
    )

    db.models.RecipeIngredients.create(
        quantity=1,
        recipe=recipe,
        ingredient=ingredient_2,
        measurement='oz'
    )
    assert recipe.ingredients.count() == 2
    ingredients = [ingredient_1, ingredient_2]

    for recipe_ingredient in recipe.ingredients.select():
        ingredient = recipe_ingredient.ingredient

        assert ingredient in ingredients
        ingredients.remove(ingredient)

    assert len(ingredients) == 0

    db.models.RecipeUtensils.create(
        recipe=recipe,
        utensil=utensil_1
    )

    db.models.RecipeUtensils.create(
        recipe=recipe,
        utensil=utensil_2
    )
    assert recipe.utensils.count() == 2
    utensils = [utensil_1, utensil_2]

    for recipe_utensil in recipe.utensils.select():
        utensil = recipe_utensil.utensil

        assert utensil in utensils
        utensils.remove(utensil)

    assert len(ingredients) == 0

