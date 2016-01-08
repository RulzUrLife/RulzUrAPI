"""Schemas for dumping and loading datas of RulzUrAPI"""
import functools

import marshmallow
import marshmallow.exceptions
import marshmallow.validate

import db.models
import collections



Schema = collections.namedtuple('Schema', ['dump', 'put', 'post'])

class DefaultSchema(marshmallow.Schema):
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
        key = self.__envelope__['many'] if many else self.__envelope__['single']
        assert key is not None, 'Envelope key undefined'
        return key

    @marshmallow.post_dump(pass_many=True)
    def wrap_with_envelope(self, data, many):
        key = self.get_envelope_key(many)
        return {key: data}

    def handle_error(self, exc, data):
        if '_schema' in exc.messages:
            raise exc


# pylint: disable=too-few-public-methods
class PostSchema(marshmallow.Schema):
    """Default configuration for post arguments

    Exclude the id field, and require all the other fields
    """

    def __init__(self, *args, **kwargs):
        super(PostSchema, self).__init__(*args, **kwargs)

        self.__processors__.clear()
        for field in self.fields.values():
            field.required = True

    class Meta(object):
        """Options for the PostSchema"""
        exclude = ('id',)


class PutSchema(marshmallow.Schema):

    @marshmallow.post_load(pass_many=True)
    def remove_id_field(self, data, many):
        if not many:
            data.pop('id', None)
        return data


class IngredientSchema(DefaultSchema):
    """Ingredient schema (for put method, ie: the 'id' field is required)"""

    __envelope__ = {
        'single': 'ingredient',
        'many': 'ingredients'
    }

    name = marshmallow.fields.String()


# pylint: disable=too-few-public-methods
class IngredientPostSchema(PostSchema, IngredientSchema):
    """Schema for ingredient post arguments"""


# pylint: disable=too-few-public-methods
class IngredientPutSchema(PutSchema, IngredientSchema):
    """Schema for ingredient put arguments"""


ingredient = Schema(IngredientSchema().dump, IngredientPutSchema(),
                    IngredientPostSchema())


class UtensilSchema(DefaultSchema):
    """Utensil schema (for put method, ie: the 'id' field is required)"""

    __envelope__ = {
        'single': 'utensil',
        'many': 'utensils'
    }

    name = marshmallow.fields.String()


# pylint: disable=too-few-public-methods
class UtensilPostSchema(PostSchema, UtensilSchema):
    """Schema for utensil post arguments"""


# pylint: disable=too-few-public-methods
class UtensilPutSchema(PutSchema, UtensilSchema):
    """Schema for utensil put arguments"""


utensil = Schema(UtensilSchema().dump, UtensilPutSchema(),
                 UtensilPostSchema())

#def validate_nested(field, needed_field, _, data):
#    """Utility function for generating error messages"""
#
#    if 'id' in data or 'name' in data:
#        return
#    raise marshmallow.ValidationError(
#        'Missing data for required field if \'%s\' field is not '
#        'provided.' % needed_field, field
#    )


# pylint: disable=too-few-public-methods
#class NestedSchema(marshmallow.Schema):
#    """Default configuration for a nested schema
#
#    If an object is nested the method can either be a post or a put, that is
#    why we have a custom validation here.
#
#    First no field is required, then, we check if 'id' or 'name' field is
#    provided. If not, an error is raised.
#    """
#    id = marshmallow.fields.Integer()
#    name = marshmallow.fields.String()
#
#    def __init__(self, *args, **kwargs):
#        super(NestedSchema, self).__init__(*args, **kwargs)
#
#        marshmallow.validates_schema(
#            functools.partial(validate_nested, 'id', 'name')
#        )
#        marshmallow.validates_schema(
#            functools.partial(validate_nested, 'name', 'id')
#        )
#
#
#
## pylint: disable=too-few-public-methods
#class RecipeIngredientsSchema(NestedSchema, DefaultSchema):
#    """Ingredient nested schema for recipe"""
#    quantity = marshmallow.fields.Integer(
#        validate=marshmallow.validate.Range(0),
#        required=True
#    )
#    measurement = marshmallow.fields.Select(
#        ['L', 'g', 'oz', 'spoon'],
#        required=True
#    )
#
#    def dump(self, obj, *args, **kwargs):
#        """The entity has the ingredient nested, so it needs to be merged"""
#
#        # handle both dict or object
#        if isinstance(obj, dict):
#            ingredient = obj['ingredient']
#            ingredient = ingredient_schema.dump(ingredient).data
#            obj.update(ingredient)
#        else:
#            ingredient = obj.ingredient
#            ingredient = ingredient_schema.dump(ingredient).data
#            for key, value in ingredient.items():
#                setattr(obj, key, value)
#
#        return super(RecipeIngredientsSchema, self).dump(obj, *args, **kwargs)
#
#
## pylint: disable=too-few-public-methods
#class RecipeUtensilsSchema(NestedSchema, DefaultSchema):
#    """Utensil nested schema for recipe"""
#
#    def dump(self, obj, *args, **kwargs):
#        if isinstance(obj, db.models.RecipeUtensils):
#            obj = obj.utensil
#        return super(RecipeUtensilsSchema, self).dump(obj, *args, **kwargs)
#
#
#def validate_unique(model, field, elts):
#    """Validate if an entry is unique
#
#    Checks against the db if all the elements with ids exist and if all the
#    elements are unique (no redundancy)
#    """
#    insert_elts = [elt for elt in elts if elt.get('id') is None]
#    update_elts = [elt['id'] for elt in elts if elt.get('id') is not None]
#
#    # check if all the elements are unique by name
#
#    # avoid running the request if no elements
#    if update_elts:
#        update_elts_count = len(update_elts)
#
#        update_elts = list(model
#                           .select(model.name)
#                           .where(model.id << update_elts)
#                           .dicts())
#        if update_elts_count != len(update_elts):
#            raise marshmallow.ValidationError(
#                'There is some entries to update which does not exist.'
#            )
#
#
#    elts_tmp = {elt['name'] for elt in update_elts + insert_elts}
#
#    if len(elts_tmp) != len(elts):
#        raise marshmallow.ValidationError(
#            'There is multiple entries for the same entity.', field
#        )
#
#
## pylint: disable=too-few-public-methods
#class RecipeSchema(DefaultSchema):
#    """Recipe schema (for put method, ie: the 'id' field is required)"""
#
#    name = marshmallow.fields.String()
#    people = marshmallow.fields.Integer(
#        validate=marshmallow.validate.Range(1, 12), default=None
#    )
#    directions = marshmallow.fields.Raw()
#    difficulty = marshmallow.fields.Integer(
#        validate=marshmallow.validate.Range(1, 5), default=None
#    )
#    duration = marshmallow.fields.Select(
#        [
#            '0/5', '5/10', '10/15', '15/20', '20/25', '25/30', '30/45',
#            '45/60', '60/75', '75/90', '90/120', '120/150'
#        ]
#    )
#    category = marshmallow.fields.Select(['starter', 'main', 'dessert'])
#
#    ingredients = marshmallow.fields.List(
#        marshmallow.fields.Nested(RecipeIngredientsSchema),
#        validate=functools.partial(
#            validate_unique, db.models.Ingredient, 'ingredients'
#        )
#    )
#    utensils = marshmallow.fields.List(
#        marshmallow.fields.Nested(RecipeUtensilsSchema),
#        validate=functools.partial(
#            validate_unique, db.models.Utensil, 'utensils'
#        )
#    )
#
#
#def validate_recipes(recipes):
#    """Checks if all the recipes in the request exist in the db"""
#    ids = [recipe['id'] for recipe in recipes]
#    db_recipes_count = (
#        db.models.Recipe
#        .select()
#        .where(db.models.Recipe.id << ids)
#        .count()
#    )
#
#    if len(recipes) != db_recipes_count:
#        raise marshmallow.ValidationError(
#            'One recipe or more do not match the database entries'
#        )
#
#
## pylint: disable=too-few-public-methods
#class RecipeListSchema(marshmallow.Schema):
#    """RecipeList schema, this is for a bulk update.
#
#    We need a list of recipes with the arguments of the put method
#    """
#    recipes = marshmallow.fields.List(
#        marshmallow.fields.Nested(RecipeSchema), required=True,
#        validate=validate_recipes
#    )
#
#
## pylint: disable=too-few-public-methods
#class RecipePostSchema(PostSchema, RecipeSchema):
#    """Schema for recipe post arguments"""
#    pass
#

