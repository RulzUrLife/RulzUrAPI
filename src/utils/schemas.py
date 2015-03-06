"""Schemas for dumping and loading datas of RulzUrAPI"""
import functools

import marshmallow
import marshmallow.exceptions
import marshmallow.validate

import db.models


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


def validate_nested(field, needed_field, _, data):
    """Utility function for generating error messages"""

    if 'id' in data or 'name' in data:
        return
    raise marshmallow.ValidationError(
        'Missing data for required field if \'%s\' field is not '
        'provided.' % needed_field, field
    )


# pylint: disable=too-few-public-methods
class NestedSchema(marshmallow.Schema):
    """Default configuration for a nested schema

    If an object is nested the method can either be a post or a put, that is
    why we have a custom validation here.

    First no field is required, then, we check if 'id' or 'name' field is
    provided. If not, an error is raised.
    """
    id = marshmallow.fields.Integer()
    name = marshmallow.fields.String()

    def __init__(self, *args, **kwargs):
        super(NestedSchema, self).__init__(*args, **kwargs)


        self.validator(functools.partial(validate_nested, 'id', 'name'))
        self.validator(functools.partial(validate_nested, 'name', 'id'))


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
    quantity = marshmallow.fields.Integer(
        validate=marshmallow.validate.Range(0),
        required=True
    )
    measurement = marshmallow.fields.Select(
        ['L', 'g', 'oz', 'spoon'],
        required=True
    )

    def dump(self, obj, *args, **kwargs):
        """The entity has the ingredient nested, so it needs to be merged"""

        # handle both dict or object
        if isinstance(obj, dict):
            ingredient = obj['ingredient']
            ingredient = ingredient_schema.dump(ingredient).data
            obj.update(ingredient)
        else:
            ingredient = obj.ingredient
            ingredient = ingredient_schema.dump(ingredient).data
            for key, value in ingredient.items():
                setattr(obj, key, value)

        return super(RecipeIngredientsSchema, self).dump(obj, *args, **kwargs)


# pylint: disable=too-few-public-methods
class RecipeUtensilsSchema(NestedSchema, DefaultSchema):
    """Utensil nested schema for recipe"""

    def dump(self, obj, *args, **kwargs):
        if isinstance(obj, db.models.RecipeUtensils):
            obj = obj.utensil
        return super(RecipeUtensilsSchema, self).dump(obj, *args, **kwargs)


def validate_unique(model, field, elts):
    """Validate if an entry is unique

    Checks against the db if all the elements with ids exist and if all the
    elements are unique (no redundancy)
    """
    insert_elts = [elt for elt in elts if elt.get('id') is None]
    update_elts = [elt['id'] for elt in elts if elt.get('id') is not None]

    # check if all the elements are unique by name

    # avoid running the request if no elements
    if update_elts:
        update_elts_count = len(update_elts)

        update_elts = list(model
                           .select(model.name)
                           .where(model.id << update_elts)
                           .dicts())
        if update_elts_count != len(update_elts):
            raise marshmallow.ValidationError(
                'There is some entries to update which does not exist.'
            )


    elts_tmp = {elt['name'] for elt in update_elts + insert_elts}

    if len(elts_tmp) != len(elts):
        raise marshmallow.ValidationError(
            'There is multiple entries for the same entity.', field
        )


# pylint: disable=too-few-public-methods
class RecipeSchema(DefaultSchema):
    """Recipe schema (for put method, ie: the 'id' field is required)"""

    name = marshmallow.fields.String()
    people = marshmallow.fields.Integer(
        validate=marshmallow.validate.Range(1, 12), default=None
    )
    directions = marshmallow.fields.Raw()
    difficulty = marshmallow.fields.Integer(
        validate=marshmallow.validate.Range(1, 5), default=None
    )
    duration = marshmallow.fields.Select([
        '0/5', '5/10', '10/15', '15/20', '20/25', '25/30', '30/45',
        '45/60', '60/75', '75/90', '90/120', '120/150'
    ])
    category = marshmallow.fields.Select([
        'starter', 'main', 'dessert'
    ])
    ingredients = marshmallow.fields.List(
        marshmallow.fields.Nested(RecipeIngredientsSchema),
        validate=functools.partial(
            validate_unique, db.models.Ingredient, 'ingredients'
        )
    )
    utensils = marshmallow.fields.List(
        marshmallow.fields.Nested(RecipeUtensilsSchema),
        validate=functools.partial(
            validate_unique, db.models.Utensil, 'utensils'
        )
    )


def validate_recipes(recipes):
    """Checks if all the recipes in the request exist in the db"""
    ids = [recipe['id'] for recipe in recipes]
    db_recipes_count = (
        db.models.Recipe
        .select()
        .where(db.models.Recipe.id << ids)
        .count()
    )

    if len(recipes) != db_recipes_count:
        raise marshmallow.ValidationError(
            'One recipe or more do not match the database entries'
        )


# pylint: disable=too-few-public-methods
class RecipeListSchema(marshmallow.Schema):
    """RecipeList schema, this is for a bulk update.

    We need a list of recipes with the arguments of the put method
    """
    recipes = marshmallow.fields.List(
        marshmallow.fields.Nested(RecipeSchema), required=True,
        validate=validate_recipes
    )


# pylint: disable=too-few-public-methods
class RecipePostSchema(PostSchema, RecipeSchema):
    """Schema for recipe post arguments"""
    pass

utensil_schema = UtensilSchema()
utensil_schema_put = UtensilSchema(exclude=('id',))
utensil_schema_post = UtensilPostSchema()
utensil_schema_list = UtensilListSchema()

ingredient_schema = IngredientSchema()
ingredient_schema_put = IngredientSchema(exclude=('id',))
ingredient_schema_post = IngredientPostSchema()
ingredient_schema_list = IngredientListSchema()

recipe_schema = RecipeSchema()
recipe_schema_put = RecipeSchema(exclude=('id',))
recipe_schema_post = RecipePostSchema()
recipe_schema_list = RecipeListSchema()

