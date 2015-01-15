"""Schemas for dumping and loading datas of RulzUrAPI"""
import marshmallow

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

post_utensils_parser = post_utensils_schema()
put_utensils_parser = put_utensils_schema()
utensil_parser = UtensilSchema()

post_ingredients_parser = post_ingredients_schema()
put_ingredients_parser = put_ingredients_schema()
ingredient_parser = IngredientSchema()
