"""Schemas for dumping and loading datas of RulzUrAPI"""
import functools

import marshmallow
import marshmallow.exceptions
import marshmallow.validate

import db.models
import collections



Schema = collections.namedtuple('Schema', ['dump', 'put', 'post'])

class Default(marshmallow.Schema):
    """Default configuration for a Schema

    Has an id field required and a skip missing option
    (avoid setting a missing attribute to None)
    """

    id = marshmallow.fields.Integer()

    __envelope__ = {
        'single': None,
        'many': None
    }

    def get_envelope_key(self, many):
        """Helper to get the envelope key."""
        key = (self.__envelope__['many']
               if many else self.__envelope__['single'])
        return key

    @marshmallow.post_dump(pass_many=True)
    def wrap_with_envelope(self, data, many):
        key = self.get_envelope_key(many)
        return data if key is None else {key: data}

    def handle_error(self, exc, data):
        errors = exc.args[0]
        schema_errors = errors.pop('_schema', None)
        for key, value in errors.items():
            if not errors[key]:
                errors[key] = schema_errors.pop()

    class Meta:
        index_errors = True


# pylint: disable=too-few-public-methods
class Post(marshmallow.Schema):
    """Default configuration for post arguments

    Exclude the id field, and require all the other fields
    """

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)

        self.__processors__.clear()
        for field in self.fields.values():
            field.required = True

    class Meta(object):
        """Options for the PostSchema"""
        exclude = ('id',)


class Put(marshmallow.Schema):

    @marshmallow.post_load(pass_many=True)
    def remove_id_field(self, data, many):
        if not many:
            data.pop('id', None)
        return data


class Ingredient(Default):
    """Ingredient schema (for put method, ie: the 'id' field is required)"""

    __envelope__ = {
        'single': 'ingredient',
        'many': 'ingredients'
    }

    name = marshmallow.fields.String()


ingredient = Schema(
    Ingredient().dump,
    type('IngredientPut', (Put, Ingredient), {})(),
    type('IngredientPost', (Post, Ingredient), {})()
)


class Utensil(Default):
    """Utensil schema (for put method, ie: the 'id' field is required)"""

    __envelope__ = {
        'single': 'utensil',
        'many': 'utensils'
    }

    name = marshmallow.fields.String()


utensil = Schema(
    Utensil().dump,
    type('UtensilPut', (Put, Utensil), {})(),
    type('UtensilPost', (Post, Utensil), {})()
)

class RecipeUtensils(Utensil):

    @marshmallow.pre_dump
    def retrieve_internal(self, data):
        return data.utensil

    def wrap_with_envelope(self, data, many):
        return data

class RecipeIngredients(Ingredient):

    quantity = marshmallow.fields.Integer(
        validate=marshmallow.validate.Range(0)
    )
    measurement = marshmallow.fields.Str(
        validate=marshmallow.validate.OneOf(['L', 'g', 'oz', 'spoon'])
    )

    @marshmallow.pre_dump
    def retrieve_internal(self, data):
        # crappy way to perform this, but only concise one which works
        data.ingredient._data.update(data._data)
        return data.ingredient._data

    def wrap_with_envelope(self, data, many):
        return data


class Direction(Default):
    title = marshmallow.fields.String()
    text = marshmallow.fields.String()


# pylint: disable=too-few-public-methods
class Recipe(Default):
    """Recipe schema (for put method, ie: the 'id' field is required)"""

    __envelope__ = {
        'single': 'recipe',
        'many': 'recipes'
    }

    name = marshmallow.fields.String()
    people = marshmallow.fields.Integer(
        validate=marshmallow.validate.Range(1, 12)
    )
    difficulty = marshmallow.fields.Integer(
        validate=marshmallow.validate.Range(1, 5)
    )
    duration = marshmallow.fields.Str(
        validate=marshmallow.validate.OneOf([
            '0/5', '5/10', '10/15', '15/20', '20/25', '25/30', '30/45',
            '45/60', '60/75', '75/90', '90/120', '120/150'
        ])
    )
    category = marshmallow.fields.Str(
        validate=marshmallow.validate.OneOf(['starter', 'main', 'dessert'])
    )

    directions = marshmallow.fields.Nested(Direction, many=True)
    utensils = marshmallow.fields.Nested(RecipeUtensils, many=True)
    ingredients = marshmallow.fields.Nested(RecipeIngredients, many=True)

def create_nested_post(cls):
    cls_name = '%sPost' % (type(cls).__name__,)
    return marshmallow.fields.Nested(
        type(cls_name, (Post, cls), {}), many=True, missing=[]
    )

RecipePost = type('RecipePost', (Post, Recipe), {
    'directions': create_nested_post(Direction),
    'utensils': create_nested_post(RecipeUtensils),
    'ingredients': create_nested_post(RecipeIngredients)
})

recipe = Schema(
    Recipe().dump,
    None,
    RecipePost()
)
