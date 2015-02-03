"""Schemas for dumping and loading datas of RulzUrAPI"""
import functools

import marshmallow
import marshmallow.exceptions
import marshmallow.validate

# pylint: disable=too-few-public-methods
class DefaultSchema(marshmallow.Schema):
    """Default configuration for a Schema

    Has an id field required and a skip missing option
    (avoid setting a missing attribute to None)
    """
    id = marshmallow.fields.Integer(required=True)

    class Meta(object):
        """Options for DefaultSchema"""
        skip_missing = True

# pylint: disable=too-few-public-methods
class PostSchema(marshmallow.Schema):
    """Default configuration for post arguments

    Exclude the id field, and require all the other fields
    """

    def __init__(self, *args, **kwargs):
        super(PostSchema, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = True

    class Meta(object):
        """Options for the PostSchema"""
        exclude = ('id',)


# pylint: disable=too-few-public-methods
class NestedSchema(marshmallow.Schema):
    """Default configuration for a nested schema

    If an object is nested the method can either be a post or a put, that is
    why we have a custom validation here.

    First no field is required, then, we check if all attributes are provided
    or if the id one is present. If not, an error is raised.
    """
    id = marshmallow.fields.Integer()

    def __init__(self, *args, **kwargs):
        super(NestedSchema, self).__init__(*args, **kwargs)
        def validate_nested(field, _, data):
            """Validator function for a specific field

            Provide a message if the field is missing and the 'id' is not
            provided
            """

            if 'id' in data or field in data:
                return
            raise marshmallow.ValidationError(
                'Missing data for required field if \'id\' field is not '
                'provided.',
                field
            )

        def validate_nested_id(fields, _, data):
            """Validator function for the id field

            same as validate nested but the message is different
            """
            if 'id' in data or all([field in data for field in fields]):
                return
            raise marshmallow.ValidationError(
                'Missing data for required field if \'%s\' fields are not '
                'provided.' % ', '.join(sorted(fields)), 'id'
            )

        fields = [key for key in self.fields.keys() if key != 'id']

        self.validator(functools.partial(validate_nested_id, fields))
        for field in fields:
            self.validator(functools.partial(validate_nested, field))


# pylint: disable=too-few-public-methods
class UtensilSchema(DefaultSchema):
    """Utensil schema (for put method, ie: the 'id' field is required)"""
    name = marshmallow.fields.String()


# pylint: disable=too-few-public-methods
class UtensilListSchema(marshmallow.Schema):
    """UtensilList schema, this is for a bulk update.

    We need a list of utensils with the arguments of the put method
    """
    utensils = marshmallow.fields.List(
        marshmallow.fields.Nested(UtensilSchema), required=True
    )


# pylint: disable=too-few-public-methods
class UtensilPostSchema(PostSchema, UtensilSchema):
    """Schema for utensil post arguments"""
    pass


# pylint: disable=too-few-public-methods
class IngredientSchema(DefaultSchema):
    """Ingredient schema (for put method, ie: the 'id' field is required)"""
    name = marshmallow.fields.String()


# pylint: disable=too-few-public-methods
class IngredientListSchema(marshmallow.Schema):
    """UtensilList schema, this is for a bulk update.

    We need a list of utensils with the arguments of the put method
    """
    ingredients = marshmallow.fields.List(
        marshmallow.fields.Nested(IngredientSchema), required=True
    )


# pylint: disable=too-few-public-methods
class IngredientPostSchema(PostSchema, IngredientSchema):
    """Schema for ingredient post arguments"""
    pass


# pylint: disable=too-few-public-methods
class RecipeIngredientsSchema(NestedSchema, DefaultSchema):
    """Ingredient nested schema for recipe"""
    name = marshmallow.fields.String()
    quantity = marshmallow.fields.Integer(
        validate=marshmallow.validate.Range(0)
    )
    measurement = marshmallow.fields.Select(['L', 'g', 'oz', 'spoon'])

    def dump(self, obj, *args, **kwargs):
        """The entity has the ingredient nested, so it needs to be merged"""
        ingredient = obj.pop('ingredient')
        ingredient = IngredientSchema().dump(ingredient).data
        obj.update(ingredient)
        return super(RecipeIngredientsSchema, self).dump(obj, *args, **kwargs)


# pylint: disable=too-few-public-methods
class RecipeUtensilsSchema(NestedSchema, DefaultSchema):
    """Utensil nested schema for recipe"""
    name = marshmallow.fields.String()


# pylint: disable=too-few-public-methods
class RecipeSchema(DefaultSchema):
    """Recipe schema (for put method, ie: the 'id' field is required)"""

    name = marshmallow.fields.String()
    people = marshmallow.fields.Integer(
        validate=marshmallow.validate.Range(1, 12)
    )
    directions = marshmallow.fields.Raw()
    difficulty = marshmallow.fields.Integer(
        validate=marshmallow.validate.Range(1, 5)
    )
    duration = marshmallow.fields.Select([
        '0/5', '5/10', '10/15', '15/20', '20/25', '25/30', '30/45',
        '45/60', '60/75', '75/90', '90/120', '120/150'
    ])
    category = marshmallow.fields.Select([
        'starter', 'main', 'dessert'
    ])
    ingredients = marshmallow.fields.List(
        marshmallow.fields.Nested(RecipeIngredientsSchema)
    )
    utensils = marshmallow.fields.List(
        marshmallow.fields.Nested(RecipeUtensilsSchema)
    )


# pylint: disable=too-few-public-methods
class RecipePostSchema(PostSchema, RecipeSchema):
    """Schema for recipe post arguments"""
    pass

