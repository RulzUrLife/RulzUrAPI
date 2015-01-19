"""Schemas for dumping and loading datas of RulzUrAPI"""
import marshmallow
import marshmallow.exceptions

# pylint: disable=too-few-public-methods
class UtensilSchema(marshmallow.Schema):
    """Schema representation of an Utensil"""
    id = marshmallow.fields.Integer()
    name = marshmallow.fields.String()

# pylint: disable=too-few-public-methods
class UtensilListSchema(marshmallow.Schema):
    """Schema representation of a list of Utensils"""
    utensils = marshmallow.fields.List(
        marshmallow.fields.Nested(UtensilSchema()),
    )

def post_utensils_schema():
    """Build a post_utensils request parser"""
    utensil_schema = UtensilSchema(exclude=('id',))
    utensil_schema.fields['name'].required = True

    return utensil_schema

def put_utensils_schema():
    """Build a put_utensils request parser"""
    utensil_list_schema = UtensilListSchema()

    utensils_field = utensil_list_schema.fields['utensils']
    utensil_schema = utensils_field.container.nested

    utensils_field.required = True
    utensil_schema.fields['id'].required = True

    return utensil_list_schema

# pylint: disable=too-few-public-methods
class IngredientSchema(marshmallow.Schema):
    """Schema representation of an Ingredient"""
    id = marshmallow.fields.Integer()
    name = marshmallow.fields.String()

# pylint: disable=too-few-public-methods
class IngredientListSchema(marshmallow.Schema):
    """Schema representation of a list of Ingredients"""
    ingredients = marshmallow.fields.List(
        marshmallow.fields.Nested(IngredientSchema()),
    )

def post_ingredients_schema():
    """Build a post_ingredients request parser"""
    ingredient_schema = IngredientSchema(exclude=('id',))
    ingredient_schema.fields['name'].required = True

    return ingredient_schema

def put_ingredients_schema():
    """Build a put_ingredients request parser"""
    ingredient_list_schema = IngredientListSchema()

    ingredients_field = ingredient_list_schema.fields['ingredients']
    ingredient_schema = ingredients_field.container.nested

    ingredients_field.required = True
    ingredient_schema.fields['id'].required = True

    return ingredient_list_schema


def people_validation(people_number):
    """Validate the number of people for a recipe"""
    if people_number < 1 or people_number > 12:
        raise marshmallow.exceptions.ValidationError(
            'People number must be between 1 and 12.'
        )

def difficulty_validation(difficulty_level):
    """Validate the difficulty level for a recipe"""
    if difficulty_level < 1 or difficulty_level > 5:
        raise marshmallow.exceptions.ValidationError(
            'Difficulty level must be between 1 and 5.'
        )

def duration_validation(duration):
    """Validate the duration value for a recipe"""
    durations = [
        '0/5', '5/10', '10/15', '15/20', '20/25', '25/30', '30/45', '45/60',
        '60/75', '75/90', '90/120', '120/150'
    ]

    if duration not in durations:
        raise marshmallow.exceptions.ValidationError(
            'Duration value is not a valid one.'
        )

def category_validation(category):
    """Validate the category field for a recipe"""
    categories = ['starter', 'main', 'dessert']
    if category not in categories:
        raise marshmallow.exceptions.ValidationError(
            'Recipe category is not a valid one (allowed values: %s).' %
            ', '.join(categories)
        )

class RecipeIngredientsSchema(marshmallow.Schema):
    """Schema representation of RecipeIngredients"""
    quantity = marshmallow.fields.Integer()
    name = marshmallow.fields.String()
    ingredient = marshmallow.fields.Nested(IngredientSchema())

class RecipeSchema(marshmallow.Schema):
    """Schema representation of a Recipe"""

    id = marshmallow.fields.Integer()
    name = marshmallow.fields.String()
    people = marshmallow.fields.Integer(
        validate=people_validation
    )
    directions = marshmallow.fields.Raw()
    difficulty = marshmallow.fields.Integer(
        validate=difficulty_validation
    )
    duration = marshmallow.fields.String(
        validate=duration_validation
    )
    category = marshmallow.fields.String(
        validate=category_validation
    )
    ingredients = marshmallow.fields.List(
        marshmallow.fields.Nested(RecipeIngredientsSchema()),
    )
    utensils = marshmallow.fields.List(
        marshmallow.fields.Nested(UtensilSchema()),
    )

def post_recipes_schema():
    """Build a post_recipes request parser"""
    recipe_schema = RecipeSchema()
    fields = [
        'name', 'people', 'directions', 'difficulty', 'duration', 'category',
        'ingredients', 'utensils'
    ]
    for field in fields:
        recipe_schema.fields[field].required = True

    return recipe_schema

def recipe_parser_schema():
    """Build a recipe_parser request parser"""
    recipe_schema = RecipeSchema()
    recipe_schema.fields['ingredients'].container.nested.exclude = ('name',)
    return recipe_schema


post_utensils_parser = post_utensils_schema()
put_utensils_parser = put_utensils_schema()
utensil_parser = UtensilSchema()

post_ingredients_parser = post_ingredients_schema()
put_ingredients_parser = put_ingredients_schema()
ingredient_parser = IngredientSchema()

post_recipes_parser = post_recipes_schema()
recipe_parser = recipe_parser_schema()
