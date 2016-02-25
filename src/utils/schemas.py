"""Schemas for dumping and loading datas of RulzUrAPI"""
import collections

import marshmallow as m

import db.helpers
import utils.helpers


FULLFIL_HELP = ('More info about fulfilling this entity here: '
                'http://link/to/the/doc')

###############################################################################
#                                                                             #
#                                   Helpers                                   #
#                                                                             #
###############################################################################

class Default(m.Schema):
    """Default configuration for a Schema

    Has an id field required and a skip missing option
    (avoid setting a missing attribute to None)
    """

    id = m.fields.Integer()

    __envelope__ = {
        'single': None,
        'many': None
    }

    def get_envelope_key(self, many):
        """Helper to get the envelope key."""
        key = (self.__envelope__['many']
               if many else self.__envelope__['single'])
        return key

    @m.post_dump(pass_many=True)
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


default = Default()

# pylint: disable=too-few-public-methods
class Post(m.Schema):
    """Default configuration for post arguments

    Exclude the id field, and require all the other fields
    """

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = True

    class Meta(object):
        """Options for the PostSchema"""
        exclude = ('id',)


class Put(m.Schema):

    @m.validates_schema(pass_original=True)
    def put_id_validator(self, data, original):
        if m.utils.is_collection(original) and not data.get('id'):
            raise m.ValidationError(
                m.fields.Field.default_error_messages['required'], 'id'
            )


class Nested(m.Schema):

    __nested__ = None
    __get_or_insert__ = None

    def wrap_with_envelope(self, data, many):
        """"""
        return data

    @m.post_load(pass_many=True)
    def get_insert_or_raise(self, data, many):
        if many:
            elts, errors = self.__get_or_insert__([
                {'id': d['id']} if 'id' in d else {'name': d['name']}
                for d in data
            ])
            if errors:
                raise m.ValidationError(errors)
            else:
                for d, elt in zip(data, elts):
                    d.update(elt)

        return data

    def handle_error(self, errors, data):
        """Reorganise error"""
        errors = collections.defaultdict(dict, errors.messages)
        ignore = []

        for key, value in errors.items():
            _schema = value.pop('_schema', [{}])[0]

            field_not_present = [
                field not in value for
                field in self.__nested__.fields.keys()
            ]
            field_not_present.append('id' not in value)
            if all(field_not_present):
                value.update(_schema)
            if 'id' in value or 'name' in value:
                ignore.append(key)

        data = [d for i, d in enumerate(data) if i not in ignore]
        _, errs = self.__get_or_insert__(data)

        cpt = 0
        for i in range(max(len(errs), len(errors))):
            if i + cpt in ignore:
                cpt += 1
            if i in errs:
                errors[i + cpt].update(errs[i])

        raise m.ValidationError(errors)


    @m.validates_schema
    def validate_schema(self, data):
        errors = self.__nested__.validate(data) if 'id' not in data else None

        if errors:
            errors['_'] = FULLFIL_HELP
            raise m.ValidationError(errors)


###############################################################################
#                                                                             #
#                             Schemas definition                              #
#                                                                             #
###############################################################################


class Utensil(Default):
    """Utensil schema (for put method, ie: the 'id' field is required)"""

    __envelope__ = {
        'single': 'utensil',
        'many': 'utensils'
    }

    name = m.fields.String()


utensil_put = type('UtensilPut', (Put, Utensil), {})()
utensil_post = type('UtensilPost', (Post, Utensil), {})()


class RecipeUtensils(Nested, Utensil):

    __nested__ =  utensil_post
    __get_or_insert__ = db.helpers.get_or_insert_utensils

    @m.pre_dump
    def retrieve_internal(self, data):
        try:
            return data.utensil
        except AttributeError:
            return data


class Ingredient(Default):
    """Ingredient schema (for put method, ie: the 'id' field is required)"""

    __envelope__ = {
        'single': 'ingredient',
        'many': 'ingredients'
    }

    name = m.fields.String()

ingredient_put = type('IngredientPut', (Put, Ingredient), {})()
ingredient_post = type('IngredientPost', (Post, Ingredient), {})()

class RecipeIngredients(Nested, Ingredient):

    __nested__ = ingredient_post
    __get_or_insert__ = db.helpers.get_or_insert_ingrs

    quantity = m.fields.Integer(
        validate=m.validate.Range(0), required=True
    )
    measurement = m.fields.Str(
        validate=m.validate.OneOf(['L', 'g', 'oz', 'spoon']),
        required=True
    )

    @m.pre_dump
    def retrieve_internal(self, data):
        try:
            return dict(
                list(data.ingredient._data.items()) + list(data._data.items())
            )
        except AttributeError:
            return data


class Direction(Default):
    title = m.fields.String()
    text = m.fields.String()

    @m.post_load
    def to_tuple(self, data):
        return data['title'], data['text']

    @m.pre_dump
    def from_tuple(self, data):
        return dict(zip(['title', 'text'], data))


# pylint: disable=too-few-public-methods
class Recipe(Default):
    """Recipe schema (for put method, ie: the 'id' field is required)"""

    __envelope__ = {
        'single': 'recipe',
        'many': 'recipes'
    }

    name = m.fields.String()
    people = m.fields.Integer(
        validate=m.validate.Range(1, 12)
    )
    difficulty = m.fields.Integer(
        validate=m.validate.Range(1, 5)
    )
    duration = m.fields.Str(
        validate=m.validate.OneOf([
            '0/5', '5/10', '10/15', '15/20', '20/25', '25/30', '30/45',
            '45/60', '60/75', '75/90', '90/120', '120/150'
        ])
    )
    category = m.fields.Str(
        validate=m.validate.OneOf(['starter', 'main', 'dessert'])
    )

    directions = m.fields.Nested(Direction, many=True)
    utensils = m.fields.Nested(RecipeUtensils, many=True)
    ingredients = m.fields.Nested(RecipeIngredients, many=True)


class RecipePost(Post, Recipe):
    utensils =  m.fields.Nested(RecipeUtensils, many=True, missing=[])
    ingredients = m.fields.Nested(RecipeIngredients, many=True, missing=[])
    directions = m.fields.Nested(
        type('DirectionPost', (Post, Direction), {}), many=True, missing=[]
    )

class RecipePut(Put, Recipe):
    utensils =  m.fields.Nested(RecipeUtensils, many=True)
    ingredients = m.fields.Nested(RecipeIngredients, many=True)
    directions = m.fields.Nested(
        type('DirectionPost', (Post, Direction), {}), many=True
    )

###############################################################################
#                                                                             #
#                            Schemas instantiation                            #
#                                                                             #
###############################################################################

Schema = collections.namedtuple('Schema', ['dump', 'put', 'post'])

ingredient = Schema(Ingredient().dump, ingredient_put, ingredient_post)
utensil = Schema(Utensil().dump, utensil_put, utensil_post)

recipe = Schema(
    Recipe().dump,
    RecipePut(),
    RecipePost()
)
