"""Test for schemas"""
# pylint: disable=no-self-use, too-many-statements, too-many-locals,
# pylint: disable=too-few-public-methods
import copy
import imp
import unittest.mock as mock

import marshmallow
import peewee
import pytest

import db.models as models
import utils.schemas as schemas


class TestUtensilSchemas(object):
    """Test schemas related to utensils"""

    def test_utensil(self, utensil):
        """Test simple utensil schema"""
        data, errors = schemas.utensil_schema.load(utensil)
        assert errors == {}
        assert data == utensil

        utensil.pop('name')
        data, errors = schemas.utensil_schema.load(utensil)
        assert errors == {}
        assert data == utensil

        utensil.pop('id')
        data, errors = schemas.utensil_schema.load(utensil)
        assert errors == {'id': ['Missing data for required field.']}
        assert data == {}


    def test_utensil_cleanup(self, utensil):
        """Test marshmallow cleanup ability on utensil schema"""
        utensil['foo'] = 'bar'
        data, errors = schemas.utensil_schema.load(utensil)
        utensil.pop('foo')
        assert errors == {}
        assert data == utensil


    def test_utensil_put(self, utensil_no_id):
        """Test put utensil schema"""
        data, errors = schemas.utensil_schema_put.load(utensil_no_id)
        assert errors == {}
        assert data == utensil_no_id

        utensil_no_id.pop('name')
        data, errors = schemas.utensil_schema_put.load(utensil_no_id)
        assert errors == {}
        assert data == utensil_no_id

    def test_utensil_put_cleanup(self, utensil_no_id):
        """Test marshmallow cleanup on put method"""
        utensil_no_id['foo'] = 'bar'
        data, errors = schemas.utensil_schema_put.load(utensil_no_id)
        utensil_no_id.pop('foo')
        assert errors == {}
        assert data == utensil_no_id


    def test_utensil_post(self, utensil_no_id):
        """Test post utensil schema"""
        data, errors = schemas.utensil_schema_post.load(utensil_no_id)
        assert errors == {}
        assert data == utensil_no_id

        utensil_no_id.pop('name')
        data, errors = schemas.utensil_schema_post.load(utensil_no_id)
        assert errors == {'name': ['Missing data for required field.']}
        assert data == {}


    def test_utensil_post_cleanup(self, utensil_no_id):
        """Test marshmallow cleanup on post method"""
        utensil_no_id['foo'] = 'bar'
        data, errors = schemas.utensil_schema_post.load(utensil_no_id)
        utensil_no_id.pop('foo')
        assert errors == {}
        assert data == utensil_no_id


    def test_utensil_list(self, utensils):
        """Test utensil list schema"""
        data, errors = schemas.utensil_schema_list.load(utensils)
        assert errors == {}
        assert data == utensils

        utensil = utensils['utensils'][0]
        utensil.pop('name')
        data, errors = schemas.utensil_schema_list.load(utensils)
        assert errors == {}
        assert data == utensils

        utensil.pop('id')
        data, errors = schemas.utensil_schema_list.load(utensils)
        error_msg = {'utensils': {'id': ['Missing data for required field.']}}
        assert errors == error_msg
        assert data == {'utensils': None}

        utensils.pop('utensils')
        data, errors = schemas.utensil_schema_list.load(utensils)
        assert errors == {'utensils': ['Missing data for required field.']}
        assert data == {}


    def test_utensil_list_cleanup(self, utensils):
        """Test marshmallow cleanup on list schema"""
        utensils_copy = copy.deepcopy(utensils)
        utensils['foo'] = 'bar'
        utensils['utensils'][0]['foo'] = 'bar'
        data, errors = schemas.utensil_schema_list.load(utensils)
        assert errors == {}
        assert data == utensils_copy


class TestIngredientSchemas(object):
    """Test schemas related to ingredients"""

    def test_ingredient(self, ingredient):
        """Test ingredient schema"""
        data, errors = schemas.ingredient_schema.load(ingredient)
        assert errors == {}
        assert data == ingredient

        ingredient.pop('name')
        data, errors = schemas.ingredient_schema.load(ingredient)
        assert errors == {}
        assert data == ingredient

        ingredient.pop('id')
        data, errors = schemas.ingredient_schema.load(ingredient)
        assert errors == {'id': ['Missing data for required field.']}
        assert data == {}


    def test_ingredient_cleanup(self, ingredient):
        """Test marshmallow cleanup on ingredient schema"""
        ingredient['foo'] = 'bar'
        data, errors = schemas.ingredient_schema.load(ingredient)
        ingredient.pop('foo')
        assert errors == {}
        assert data == ingredient


    def test_ingredient_put(self, ingredient_no_id):
        """Test put ingredient schema"""
        data, errors = schemas.ingredient_schema_put.load(ingredient_no_id)
        assert errors == {}
        assert data == ingredient_no_id

        ingredient_no_id.pop('name')
        data, errors = schemas.ingredient_schema_put.load(ingredient_no_id)
        assert errors == {}
        assert data == ingredient_no_id

    def test_ingredient_put_cleanup(self, ingredient_no_id):
        """Test marshmallow cleanup on ingredient put schema"""
        ingredient_no_id['foo'] = 'bar'
        data, errors = schemas.ingredient_schema_put.load(ingredient_no_id)
        ingredient_no_id.pop('foo')
        assert errors == {}
        assert data == ingredient_no_id


    def test_ingredient_post(self, ingredient_no_id):
        """Test post ingredient schema"""
        data, errors = schemas.ingredient_schema_post.load(ingredient_no_id)
        assert errors == {}
        assert data == ingredient_no_id

        ingredient_no_id.pop('name')
        data, errors = schemas.ingredient_schema_post.load(ingredient_no_id)
        assert errors == {'name': ['Missing data for required field.']}
        assert data == {}


    def test_ingredient_post_cleanup(self, ingredient_no_id):
        """Test marshmallow cleanup on ingredient post schema"""
        ingredient_no_id['foo'] = 'bar'
        data, errors = schemas.ingredient_schema_post.load(ingredient_no_id)
        ingredient_no_id.pop('foo')
        assert errors == {}
        assert data == ingredient_no_id


    def test_ingredient_list(self, ingredients):
        """Test ingredient list schema"""
        data, errors = schemas.ingredient_schema_list.load(ingredients)
        assert errors == {}
        assert data == ingredients

        ingredient = ingredients['ingredients'][0]
        ingredient.pop('name')
        data, errors = schemas.ingredient_schema_list.load(ingredients)
        assert errors == {}
        assert data == ingredients

        ingredient.pop('id')
        data, errors = schemas.ingredient_schema_list.load(ingredients)
        error_msg = {'ingredients': {'id': ['Missing data for required field.']}}
        assert errors == error_msg
        assert data == {'ingredients': None}

        ingredients.pop('ingredients')
        data, errors = schemas.ingredient_schema_list.load(ingredients)
        assert errors == {'ingredients': ['Missing data for required field.']}
        assert data == {}


    def test_ingredient_list_cleanup(self, ingredients):
        """Test marshmallow cleanup on ingredient list schema"""
        ingredients_copy = copy.deepcopy(ingredients)
        ingredients['foo'] = 'bar'
        ingredients['ingredients'][0]['foo'] = 'bar'
        data, errors = schemas.ingredient_schema_list.load(ingredients)
        assert errors == {}
        assert data == ingredients_copy


class TestRecipeIngredientsSchema(object):
    """Test schemas related to RecipeIngredients"""

    def test_dump_dict(self, monkeypatch):
        """Test the custom dump method on a dict"""
        mock_recipe_ingredients_dict = mock.MagicMock(spec=dict)
        update = mock_recipe_ingredients_dict.update
        get_item = mock_recipe_ingredients_dict.__getitem__
        get_item.return_value = mock.sentinel.ingredient

        mock_ingredient_data = mock.Mock(data=mock.sentinel.ingredient_data)
        mock_ingredient_dump = mock.Mock(return_value=mock_ingredient_data)

        mock_super_dump = mock.Mock(return_value=mock.sentinel.rv)

        monkeypatch.setattr('utils.schemas.NestedSchema.dump', mock_super_dump)
        monkeypatch.setattr('utils.schemas.ingredient_schema.dump',
                            mock_ingredient_dump)

        recipe_ingredients_schema = schemas.RecipeIngredientsSchema()
        rv = recipe_ingredients_schema.dump(mock_recipe_ingredients_dict)

        ingredient_dump_calls = [mock.call(mock.sentinel.ingredient)]
        update_calls = [mock.call(mock.sentinel.ingredient_data)]
        super_dump_calls = [mock.call(mock_recipe_ingredients_dict)]

        assert get_item.call_args_list == [mock.call('ingredient')]
        assert mock_ingredient_dump.call_args_list == ingredient_dump_calls
        assert update.call_args_list == update_calls
        assert mock_super_dump.call_args_list == super_dump_calls
        assert rv == mock.sentinel.rv


    def test_dump_object(self, monkeypatch):
        """Test the custom dump method on an object"""
        mock_recipe_ingredients_object = mock.MagicMock(
            spec=object, ingredient=mock.sentinel.ingredient
        )
        mock_ingredient = mock.Mock()
        mock_ingredient.items.return_value = [('foo', mock.sentinel.bar)]

        mock_ingredient_data = mock.Mock(data=mock_ingredient)
        mock_ingredient_dump = mock.Mock(return_value=mock_ingredient_data)

        mock_super_dump = mock.Mock(return_value=mock.sentinel.rv)

        monkeypatch.setattr('utils.schemas.NestedSchema.dump', mock_super_dump)
        monkeypatch.setattr('utils.schemas.ingredient_schema.dump',
                            mock_ingredient_dump)

        recipe_ingredients_schema = schemas.RecipeIngredientsSchema()
        rv = recipe_ingredients_schema.dump(mock_recipe_ingredients_object)

        ingredient_dump_calls = [mock.call(mock.sentinel.ingredient)]
        super_dump_calls = [mock.call(mock_recipe_ingredients_object)]

        assert mock_ingredient_dump.call_args_list == ingredient_dump_calls
        assert mock_ingredient.items.call_args_list == [mock.call()]
        assert mock_recipe_ingredients_object.foo == mock.sentinel.bar
        assert mock_super_dump.call_args_list == super_dump_calls
        assert rv == mock.sentinel.rv


class TestRecipeUtensilsSchema(object):
    """Test schemas related to RecipeUtensils"""

    def test_dump(self, monkeypatch):
        """Test the custom dump method"""
        mock_recipe_utensils = mock.Mock(spec=models.RecipeUtensils,
                                         utensil=mock.sentinel.utensil)
        mock_super_dump = mock.Mock(return_value=mock.sentinel.rv)

        monkeypatch.setattr('utils.schemas.NestedSchema.dump', mock_super_dump)

        recipe_utensils_schema = schemas.RecipeUtensilsSchema()
        rv = recipe_utensils_schema.dump(mock_recipe_utensils)

        super_dump_calls = [mock.call(mock.sentinel.utensil)]
        assert mock_super_dump.call_args_list == super_dump_calls
        assert rv == mock.sentinel.rv


class TestValidateFunctions(object):
    """Test validation functions"""

    def test_validate_nested_missing_attr(self):
        """Test the validation function for nested elements"""
        data = {'foo': 'bar'}

        with pytest.raises(marshmallow.ValidationError) as excinfo:
            schemas.validate_nested(mock.sentinel.field, 'foo', None, data)

        assert excinfo.value.args == ('Missing data for required field if '
                                      '\'foo\' field is not provided.',)
        assert excinfo.value.field == mock.sentinel.field

        data = {'id': None, 'foo': 'bar'}
        schemas.validate_nested(None, None, None, data)

        data = {'name': None, 'foo': 'bar'}
        schemas.validate_nested(None, None, None, data)


    def test_validate_unique(self, monkeypatch, model):
        """Test the validation for unique db constraint (mostly name attr)"""
        mock_model_select = mock.Mock()
        model_where = mock_model_select.return_value.where
        model_dicts = model_where.return_value.dicts

        model_dicts.return_value = [{'name': 'elt_1'}]

        elts = [{'id': 1}, {'name': 'elt_2'}]
        field = mock.sentinel.field

        monkeypatch.setattr(model, 'select', mock_model_select)
        schemas.validate_unique(model, field, elts)

        model_select_calls = [mock.call(model.name)]
        model_where_exp = peewee.Expression(model.id, peewee.OP.IN, [1])

        assert mock_model_select.call_args_list == model_select_calls
        assert model_where.call_args_list == [mock.call(model_where_exp)]
        assert model_dicts.call_args_list == [mock.call()]


    def test_validate_unique_no_entry(self, monkeypatch, model):
        """Test the unique validation if the element does not exist in db"""
        mock_model_select = mock.Mock()
        (mock_model_select.return_value
         .where.return_value
         .dicts.return_value) = []

        elts = [{'id': 1}]
        monkeypatch.setattr(model, 'select', mock_model_select)
        with pytest.raises(marshmallow.ValidationError) as excinfo:
            schemas.validate_unique(model, None, elts)

        assert excinfo.value.args == ('There is some entries to update which '
                                      'does not exist.',)


    def test_validate_unique_multiple_entries(self, monkeypatch, model):
        """Test the unique validation for the same object multiple reference"""
        mock_model_select = mock.Mock()
        (mock_model_select.return_value
         .where.return_value
         .dicts.return_value) = [{'name': 'elt_1'}]

        elts = [{'id': 1}, {'name': 'elt_1'}]

        monkeypatch.setattr(model, 'select', mock_model_select)
        with pytest.raises(marshmallow.ValidationError) as excinfo:
            schemas.validate_unique(model, mock.sentinel.field, elts)

        assert excinfo.value.args == ('There is multiple entries for the same '
                                      'entity.',)
        assert excinfo.value.field == mock.sentinel.field


    def test_validate_recipes(self, monkeypatch):
        """Test the validation function on put method for recipes"""
        mock_recipe_select = mock.Mock()
        recipe_where = mock_recipe_select.return_value.where
        recipe_count = recipe_where.return_value.count
        recipe_count.return_value = 1

        recipes = [{'id': 1}]

        monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)
        schemas.validate_recipes(recipes)

        where_exp = peewee.Expression(models.Recipe.id, peewee.OP.IN, [1])

        assert mock_recipe_select.call_args_list == [mock.call()]
        assert recipe_where.call_args_list == [mock.call(where_exp)]
        assert recipe_count.call_args_list == [mock.call()]


    def test_validate_recipes_no_entry(self, monkeypatch):
        """Test recipes validation with errors"""
        mock_recipe_select = mock.Mock()
        (mock_recipe_select.return_value
         .where.return_value.count
         .return_value) = 0

        recipes = [{'id': 1}]
        monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)

        with pytest.raises(marshmallow.ValidationError) as excinfo:
            schemas.validate_recipes(recipes)

        assert excinfo.value.args == ('One recipe or more do not match the '
                                      'database entries',)


class TestRecipeSchema(object):
    """Test schemas related to recipes"""

    @staticmethod
    @pytest.fixture
    def mock_validate_unique(monkeypatch):
        """Fixture which provides mock objects for ingredients and utensils"""
        mock_unique_ingrs = mock.Mock()
        mock_unique_utensils = mock.Mock()

        mock_partials_return = [mock_unique_ingrs, mock_unique_utensils]
        mock_partial = mock.Mock(side_effect=iter(mock_partials_return))

        monkeypatch.setattr('functools.partial', mock_partial)
        imp.reload(schemas)
        monkeypatch.undo()

        return mock_unique_ingrs, mock_unique_utensils


    def test_recipe_init(self, monkeypatch):
        """Test the initialization of recipe schema attributes"""
        mock_partial = mock.Mock()

        monkeypatch.setattr('functools.partial', mock_partial)
        imp.reload(schemas)

        partial_calls = [mock.call(schemas.validate_unique,
                                   models.Ingredient, 'ingredients'),
                         mock.call(schemas.validate_unique, models.Utensil,
                                   'utensils')]
        assert mock_partial.call_args_list == partial_calls


    def test_recipe_validate(self, monkeypatch, mock_validate_unique, recipe):
        """Test validation of a recipe"""

        def build_nested_calls(schema, elts):
            """Generate list of calls for nested recipe attrs"""
            validate_nested_calls = []
            for elt in elts:
                validate_id_call = mock.call('id', 'name', schema, elt)
                validate_name_call = mock.call('name', 'id', schema, elt)
                validate_nested_calls += [validate_id_call, validate_name_call]

            return validate_nested_calls

        mock_unique_ingrs, mock_unique_utensils = mock_validate_unique
        mock_validate_nested = mock.Mock()
        monkeypatch.setattr('utils.schemas.validate_nested',
                            mock_validate_nested)

        schema = schemas.recipe_schema

        data, errors = schema.load(recipe)

        utensils = recipe['utensils']
        ingrs = recipe['ingredients']

        utensils_validate_calls = build_nested_calls(
            schemas.recipe_schema.fields['utensils'].container.schema, utensils
        )
        ingrs_validate_calls = build_nested_calls(
            schemas.recipe_schema.fields['ingredients'].container.schema, ingrs
        )
        validate_nested_calls = ingrs_validate_calls + utensils_validate_calls

        # the order of the validate calls can vary, so we set an arbitrary one
        args_list_key = lambda x: x[0][2].__class__.__name__
        mock_validate_nested.call_args_list.sort(key=args_list_key)

        assert errors == {}
        assert data == recipe

        assert mock_unique_utensils.call_args_list == [mock.call(utensils)]
        assert mock_unique_ingrs.call_args_list == [mock.call(ingrs)]
        assert mock_validate_nested.call_args_list == validate_nested_calls


    def test_recipe(self, mock_validate_unique, recipe):
        """Test recipe schema"""
        del mock_validate_unique

        data, errors = schemas.recipe_schema.load(recipe)
        assert errors == {}
        assert data == recipe

        recipe.pop('name')
        data, errors = schemas.recipe_schema.load(recipe)
        assert errors == {}
        assert data == recipe

        recipe.pop('people')
        data, errors = schemas.recipe_schema.load(recipe)
        assert errors == {}
        assert data == recipe

        recipe.pop('directions')
        data, errors = schemas.recipe_schema.load(recipe)
        assert errors == {}
        assert data == recipe

        recipe.pop('difficulty')
        data, errors = schemas.recipe_schema.load(recipe)
        assert errors == {}
        assert data == recipe

        recipe.pop('duration')
        data, errors = schemas.recipe_schema.load(recipe)
        assert errors == {}
        assert data == recipe

        recipe.pop('category')
        data, errors = schemas.recipe_schema.load(recipe)
        assert errors == {}
        assert data == recipe

        recipe.pop('ingredients')
        data, errors = schemas.recipe_schema.load(recipe)
        assert errors == {}
        assert data == recipe

        recipe.pop('utensils')
        data, errors = schemas.recipe_schema.load(recipe)
        assert errors == {}
        assert data == recipe

        recipe.pop('id')
        data, errors = schemas.recipe_schema.load(recipe)
        assert errors == {'id': ['Missing data for required field.']}
        assert data == {}


    def test_recipe_errors(self, mock_validate_unique, recipe):
        """Test recipe schemas by introducing errors, and check messages"""
        del mock_validate_unique

        returned_errors = {}

        recipe['people'] = 0
        returned_errors['people'] = ['Must be between 1 and 12.']
        _, errors = schemas.recipe_schema.load(recipe)
        assert errors == returned_errors

        recipe['difficulty'] = 0
        returned_errors['difficulty'] = ['Must be between 1 and 5.']
        _, errors = schemas.recipe_schema.load(recipe)
        assert errors == returned_errors

        recipe['duration'] = 'error'
        returned_errors['duration'] = ["'error' is not a valid choice for this"
                                       " field."]
        _, errors = schemas.recipe_schema.load(recipe)
        assert errors == returned_errors

        recipe['category'] = 'error'
        returned_errors['category'] = ["'error' is not a valid choice for this"
                                       " field."]
        _, errors = schemas.recipe_schema.load(recipe)
        assert errors == returned_errors

        recipe['ingredients'][0]['measurement'] = 'error'
        returned_errors['ingredients'] = {}
        returned_errors['ingredients']['measurement'] = [
            "'error' is not a valid choice for this field."
        ]
        _, errors = schemas.recipe_schema.load(recipe)
        assert errors == returned_errors

        recipe['ingredients'][0]['quantity'] = -1
        returned_errors['ingredients']['measurement'] = [
            "'error' is not a valid choice for this field."
        ]
        _, errors = schemas.recipe_schema.load(recipe)
        returned_errors['ingredients']['quantity'] = ['Must be at least 0.']
        assert errors == returned_errors


    def test_recipe_cleanup(self, mock_validate_unique, recipe):
        """Test marshmallow cleanup on recipe schema"""
        del mock_validate_unique

        recipe['foo'] = 'bar'
        data, errors = schemas.recipe_schema.load(recipe)
        recipe.pop('foo')
        assert errors == {}
        assert data == recipe


    def test_recipe_put(self, mock_validate_unique, recipe_no_id):
        """Test put recipe schema"""
        del mock_validate_unique

        data, errors = schemas.recipe_schema_put.load(recipe_no_id)
        assert errors == {}
        assert data == recipe_no_id

        recipe_no_id.pop('name')
        data, errors = schemas.recipe_schema_put.load(recipe_no_id)
        assert errors == {}
        assert data == recipe_no_id

        recipe_no_id.pop('people')
        data, errors = schemas.recipe_schema_put.load(recipe_no_id)
        assert errors == {}
        assert data == recipe_no_id

        recipe_no_id.pop('directions')
        data, errors = schemas.recipe_schema_put.load(recipe_no_id)
        assert errors == {}
        assert data == recipe_no_id

        recipe_no_id.pop('difficulty')
        data, errors = schemas.recipe_schema_put.load(recipe_no_id)
        assert errors == {}
        assert data == recipe_no_id

        recipe_no_id.pop('duration')
        data, errors = schemas.recipe_schema_put.load(recipe_no_id)
        assert errors == {}
        assert data == recipe_no_id

        recipe_no_id.pop('category')
        data, errors = schemas.recipe_schema_put.load(recipe_no_id)
        assert errors == {}
        assert data == recipe_no_id

        recipe_no_id.pop('ingredients')
        data, errors = schemas.recipe_schema_put.load(recipe_no_id)
        assert errors == {}
        assert data == recipe_no_id

        recipe_no_id.pop('utensils')
        data, errors = schemas.recipe_schema_put.load(recipe_no_id)
        assert errors == {}
        assert data == recipe_no_id


    def test_recipe_put_cleanup(self, mock_validate_unique, recipe_no_id):
        """Test marshmallow cleanup on recipe put schema"""
        del mock_validate_unique

        recipe_no_id['foo'] = 'bar'
        data, errors = schemas.recipe_schema_put.load(recipe_no_id)
        recipe_no_id.pop('foo')
        assert errors == {}
        assert data == recipe_no_id


    def test_recipe_post(self, mock_validate_unique, recipe_no_id):
        """Test post recipe schema"""
        del mock_validate_unique

        returned_error = {}

        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == {}
        assert data == recipe_no_id

        recipe_no_id.pop('name')
        returned_error['name'] = ['Missing data for required field.']
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == returned_error

        recipe_no_id.pop('people')
        returned_error['people'] = ['Missing data for required field.']
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == returned_error

        recipe_no_id.pop('directions')
        returned_error['directions'] = ['Missing data for required field.']
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == returned_error

        recipe_no_id.pop('difficulty')
        returned_error['difficulty'] = ['Missing data for required field.']
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == returned_error

        recipe_no_id.pop('duration')
        returned_error['duration'] = ['Missing data for required field.']
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == returned_error

        recipe_no_id.pop('category')
        returned_error['category'] = ['Missing data for required field.']
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == returned_error

        recipe_no_id['ingredients'][0].pop('measurement')
        returned_error['ingredients'] = {}
        returned_error['ingredients']['measurement'] = ['Missing data for '
                                                        'required field.']
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == returned_error

        recipe_no_id['ingredients'][0].pop('quantity')
        returned_error['ingredients']['quantity'] = ['Missing data for '
                                                     'required field.']
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == returned_error

        recipe_no_id['ingredients'][0].pop('id')
        returned_error['ingredients']['id'] = [
            "Missing data for required field if 'name' field is not provided."
        ]
        returned_error['ingredients']['name'] = [
            "Missing data for required field if 'id' field is not provided."
        ]
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == returned_error

        recipe_no_id.pop('ingredients')
        returned_error['ingredients'] = ['Missing data for required field.']
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == returned_error

        recipe_no_id['utensils'][0].pop('id')
        returned_error['utensils'] = {}
        returned_error['utensils']['id'] = [
            "Missing data for required field if 'name' field is not provided."
        ]
        returned_error['utensils']['name'] = [
            "Missing data for required field if 'id' field is not provided."
        ]
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == returned_error

        recipe_no_id.pop('utensils')
        returned_error['utensils'] = ['Missing data for required field.']
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        assert errors == returned_error

        assert recipe_no_id == {}


    def test_recipe_post_cleanup(self, mock_validate_unique, recipe_no_id):
        """Test marshmallow cleanup on recipe post schema"""
        del mock_validate_unique

        recipe_no_id['foo'] = 'bar'
        data, errors = schemas.recipe_schema_post.load(recipe_no_id)
        recipe_no_id.pop('foo')
        assert errors == {}
        assert data == recipe_no_id


    def test_recipe_list_validate(self, recipes):
        """Test recipe list schema validation"""
        mock_validate_recipes = mock.Mock()
        recipes_field = schemas.recipe_schema_list.fields['recipes']
        assert recipes_field.validators == [schemas.validate_recipes]

        recipes_field.validators = [mock_validate_recipes]
        data, errors = schemas.recipe_schema_list.load(recipes)

        assert data == recipes
        assert errors == {}
        assert mock_validate_recipes.call_args_list == [
            mock.call(recipes['recipes'])
        ]


    def test_recipe_list(self, mock_validate_unique, recipes):
        """Test utensil list schema"""
        del mock_validate_unique
        schemas.recipe_schema_list.fields['recipes'].validators = [mock.Mock()]

        data, errors = schemas.recipe_schema_list.load(recipes)
        assert errors == {}
        assert data == recipes

        recipe = recipes['recipes'][0]
        recipe.pop('name')
        data, errors = schemas.recipe_schema_list.load(recipes)
        assert errors == {}
        assert data == recipes

        # do not repeat, have to find a way for testing this, or just assume
        # marshmallow is working?

        recipe.pop('id')
        data, errors = schemas.recipe_schema_list.load(recipes)
        error_msg = {'recipes': {'id': ['Missing data for required field.']}}
        import ipdb; ipdb.set_trace()
        assert errors == error_msg
        assert data == {'recipes': None}

        recipes.pop('recipes')
        data, errors = schemas.recipe_schema_list.load(recipes)
        assert errors == {'recipes': ['Missing data for required field.']}
        assert data == {}


    def test_recipe_list_cleanup(self, mock_validate_unique, recipes):
        """Test marshmallow cleanup on utensil list schema"""
        del mock_validate_unique
        schemas.recipe_schema_list.fields['recipes'].validators = [mock.Mock()]

        recipes_copy = copy.deepcopy(recipes)
        recipes['foo'] = 'bar'
        recipes['recipes'][0]['foo'] = 'bar'
        data, errors = schemas.recipe_schema_list.load(recipes)
        assert errors == {}
        assert data == recipes_copy

