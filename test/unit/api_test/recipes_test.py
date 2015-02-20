"""API endpoints testing"""

import copy
import json
import peewee
import unittest.mock as mock
import db.models
import test.utils as utils
import utils.helpers as helpers
import utils.schemas as schemas

def initialize_nested(elts, name):
    """Prepare the nested tests mocks collections

    The first element returned will be used for checking the insertion,
    the second one will be the query result (it adds the id field),
    the third one is for mocking the validate_if_unique checker
    """
    insert, insert_return, validate_return = [], [], []
    for i, elt in enumerate(elts):
        elt_name = elt.get('name')
        elt_id = i + 1

        if elt_name is None:
            elt_name = '%s_%d' % (name, elt_id)
            validate_return.append({'name': elt_name})
        else:
            insert.append({'name': elt_name})

        insert_return.append(
            utils.FakeModel({'id': elt_id, 'name': elt_name})
        )
    return insert, insert_return, validate_return


def test_recipes_list(app, monkeypatch):
    """Test /recipes/"""

    recipes = [
        {'recipe_1': 'recipe_1_content'},
        {'recipe_2': 'recipe_2_content'}
    ]

    mock_recipe_select = mock.Mock()
    mock_recipe_select.return_value.dicts.return_value = recipes
    monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)
    recipes_page = app.get('/recipes/')
    mock_recipe_select.assert_called_once_with()
    assert utils.load(recipes_page) == {'recipes': recipes}


def test_recipe_get(app, monkeypatch, recipe_db_fixture, recipe_dump_fixture):
    """Test /recipes/<id>"""
    mock_recipe_select = mock.Mock()
    (mock_recipe_select.return_value
     .join.return_value
     .join.return_value
     .switch.return_value
     .join.return_value
     .join.return_value
     .where.return_value
     .aggregate_rows.return_value
     .execute.return_value) = iter([utils.FakeModel(recipe_db_fixture)])

    recipe_dict = db.models.Recipe.__dict__
    recipe_ingredients_dict = db.models.RecipeIngredients.__dict__
    recipe_utensils_dict = db.models.RecipeUtensils.__dict__

    utensil_dict = db.models.Utensil.__dict__
    ingredient_dict = db.models.Ingredient.__dict__

    monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)

    recipe_page = app.get('/recipes/1')

    assert mock_recipe_select.call_count == 1
    (recipe_model, recipe_ingredients_model, ingredient_model,
     recipe_utensils_model, utensil_model), _ = mock_recipe_select.call_args
    assert recipe_model.__dict__ == recipe_dict
    assert recipe_ingredients_model.__dict__ == recipe_ingredients_dict
    assert recipe_utensils_model.__dict__ == recipe_utensils_dict

    assert utensil_model.__dict__ == utensil_dict
    assert ingredient_model.__dict__ == ingredient_dict


    join = mock_recipe_select.return_value.join
    assert join.call_count == 1
    (recipe_ingredients_model,), _ = join.call_args
    assert recipe_ingredients_model.__dict__ == recipe_ingredients_dict

    join = join.return_value.join
    assert join.call_count == 1
    (ingredient_model,), _ = join.call_args
    assert ingredient_model.__dict__ == ingredient_dict

    switch = join.return_value.switch
    assert switch.call_count == 1
    (recipe_model,), _ = switch.call_args
    assert recipe_model.__dict__ == recipe_dict

    join = switch.return_value.join
    assert join.call_count == 1
    (recipe_utensils_model,), _ = join.call_args
    assert recipe_utensils_model.__dict__ == recipe_utensils_dict

    join = join.return_value.join
    assert join.call_count == 1
    (utensil_model,), _ = join.call_args
    assert utensil_model.__dict__ == utensil_dict

    where = join.return_value.where
    where_exp = peewee.Expression(db.models.Recipe.id, peewee.OP_EQ, 1)
    assert utils.expression_assert(where, where_exp)

    aggregate_rows = where.return_value.aggregate_rows
    assert aggregate_rows.call_args_list == [mock.call()]

    execute = aggregate_rows.return_value.execute
    assert execute.call_args_list == [mock.call()]

    assert utils.load(recipe_page) == {'recipe': recipe_dump_fixture}


def test_recipe_get_404(app, monkeypatch):
    """Test /recipes/<id> with recipe not found"""

    monkeypatch.setattr(
        'db.models.Recipe.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    recipe = app.get('/recipes/2')
    assert recipe.status_code == 404


# pylint: disable=too-many-statements, too-many-locals
def test_recipes_post(app, monkeypatch, post_recipe_fixture):
    """Test post /recipes/"""

    # prepare the returned object to check against the test
    recipe_mock = copy.deepcopy(post_recipe_fixture)
    recipe_mock['id'] = 1

    recipe_mock = utils.FakeModel(recipe_mock)
    ingredients, ingredients_mock, ingredients_select = initialize_nested(
        post_recipe_fixture['ingredients'], 'ingredient'
    )
    utensils, utensils_mock, utensils_select = initialize_nested(
        post_recipe_fixture['utensils'], 'utensil'
    )


    # prepare some mock for recipe workflow
    mock_execute_sql = mock.Mock()
    mock_recipe_create = mock.Mock()
    mock_recipe_select = mock.Mock()


    # the nested fields will use two requests, the first one for validation,
    # the second one to populate the created recipe

    ingredient_validate, ingredient_select = mock.Mock(), mock.Mock()
    utensil_validate, utensil_select = mock.Mock(), mock.Mock()

    (ingredient_validate.return_value
     .where.return_value
     .dicts.return_value) = ingredients_select
    (ingredient_select.return_value
     .where.return_value) = ingredients_mock

    (utensil_validate.return_value
     .where.return_value
     .dicts.return_value) = utensils_select
    (utensil_select.return_value
     .where.return_value) = utensils_mock


    mock_ingredient_select = mock.Mock(
        side_effect=iter([ingredient_validate(), ingredient_select()])
    )

    mock_utensil_select = mock.Mock(
        side_effect=iter([utensil_validate(), utensil_select()])
    )

    # mock the other methods
    mock_ingredient_insert = mock.Mock()
    mock_utensil_insert = mock.Mock()

    mock_recipe_utensils_insert = mock.Mock()
    mock_recipe_ingredients_insert = mock.Mock()

    # monkeypatch all the things! o/
    monkeypatch.setattr('db.connector.database.execute_sql', mock_execute_sql)
    monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)
    monkeypatch.setattr('db.models.Recipe.create', mock_recipe_create)

    monkeypatch.setattr('db.models.Ingredient.select', mock_ingredient_select)
    monkeypatch.setattr('db.models.Ingredient.insert_many',
                        mock_ingredient_insert)

    monkeypatch.setattr('db.models.Utensil.select', mock_utensil_select)
    monkeypatch.setattr('db.models.Utensil.insert_many',
                        mock_utensil_insert)

    monkeypatch.setattr('db.models.RecipeUtensils.insert_many',
                        mock_recipe_utensils_insert)
    monkeypatch.setattr('db.models.RecipeIngredients.insert_many',
                        mock_recipe_ingredients_insert)

    # mock the recipes methods
    mock_recipe_select.return_value.where.return_value.count.return_value = 0
    mock_recipe_create.return_value = recipe_mock


    # go, go, go
    recipes_create_page = app.post(
        '/recipes/', data=json.dumps(post_recipe_fixture),
        content_type='application/json'
    )
    # check if the tables are correctly locked
    lock_string = 'LOCK TABLE %s IN SHARE ROW EXCLUSIVE MODE'
    lock_utensil = lock_string % helpers.model_entity(db.models.Utensil)
    lock_ingredient = lock_string % helpers.model_entity(db.models.Ingredient)

    utensil_lock = mock.call(lock_utensil)
    ingredient_lock = mock.call(lock_ingredient)

    assert mock_execute_sql.call_args_list == [utensil_lock, ingredient_lock]

    # check if the recipes are checked to avoid conflict
    assert mock_recipe_select.call_count == 1
    assert utils.expression_assert(
        mock_recipe_select.return_value.where,
        peewee.Expression(db.models.Recipe.name, peewee.OP_EQ,
                          post_recipe_fixture.get('name'))
    )

    # check if the utensils or ingredients to update exists and if they are not
    # redundant in the same request

    # it has been called two times, one for the validation, one for the return
    assert mock_ingredient_select.call_count == 2
    assert utils.expression_assert(
        mock_ingredient_select, db.models.Ingredient.name
    )
    assert mock_ingredient_select.call_args_list[1] == mock.call()
    assert utils.expression_assert(
        ingredient_validate.return_value.where,
        peewee.Expression(db.models.Ingredient.id, peewee.OP_IN, [3, 4])
    )

    assert mock_utensil_select.call_count == 2
    assert utils.expression_assert(
        mock_utensil_select, db.models.Utensil.name
    )
    assert mock_utensil_select.call_args_list[1] == mock.call()
    assert utils.expression_assert(
        utensil_validate.return_value.where,
        peewee.Expression(db.models.Utensil.id, peewee.OP_IN, [3, 4])
    )

    # insertion into the tables of the nested fields
    execute = mock_ingredient_insert.return_value.execute
    assert mock_ingredient_insert.call_count == 1
    assert mock_ingredient_insert.call_args == mock.call(
        db.models.Ingredient.name, ingredients
    )
    assert execute.call_count == 1
    assert execute.call_args == mock.call()

    execute = mock_utensil_insert.return_value.execute
    assert mock_utensil_insert.call_count == 1
    assert mock_utensil_insert.call_args == mock.call(
        db.models.Utensil.name, utensils
    )
    assert execute.call_count == 1
    assert execute.call_args == mock.call

    post_recipe_fixture['id'] = 1

    # merge the fake model with the post fixture
    for index, ingredient in enumerate(ingredients_mock):
        post_recipe_fixture['ingredients'][index].update(ingredient.to_dict())

    post_recipe_fixture['utensils'] = [
        utensil.to_dict() for utensil in utensils_mock
    ]

    assert recipes_create_page.status_code == 201
    assert utils.load(recipes_create_page) == {'recipe': post_recipe_fixture}


def test_recipes_post_409(app, monkeypatch, post_recipe_fixture_no_id):
    """Test post conflict /recipes/"""

    mock_select = mock.Mock()
    mock_execute_sql = mock.Mock()

    monkeypatch.setattr('db.connector.database.execute_sql', mock_execute_sql)
    monkeypatch.setattr('db.models.Recipe.select', mock_select)

    mock_select.return_value.where.return_value.count.return_value = 1
    recipes_create_page = app.post(
        '/recipes/', data=json.dumps(post_recipe_fixture_no_id),
        content_type='application/json'
    )

    assert utils.expression_assert(
        mock_select.return_value.where,
        peewee.Expression(db.models.Recipe.name, peewee.OP_EQ,
                          post_recipe_fixture_no_id.get('name'))
    )
    assert recipes_create_page.status_code == 409
    assert utils.load(recipes_create_page) == (
        {'message': 'Recipe already exists.', 'status': 409}
    )


def test_recipes_post_400(app, monkeypatch, post_recipe_fixture):
    """Test http error 400 possibilities"""

    def post(data):
        """Simply post dumped data on /recipes/"""
        return app.post(
            '/recipes/', data=json.dumps(data), content_type='application/json'
        )

    def validate_unique_mock(mock_obj, return_value):
        """Simple alias for code simplification"""
        (mock_obj.return_value
         .where.return_value
         .dicts.return_value) = return_value

    mock_execute_sql = mock.Mock()
    mock_select_update_ingrs = mock.Mock()
    mock_select_update_utensils = mock.Mock()

    monkeypatch.setattr('db.connector.database.execute_sql', mock_execute_sql)
    monkeypatch.setattr('db.models.Ingredient.select',
                        mock_select_update_ingrs)
    monkeypatch.setattr('db.models.Utensil.select',
                        mock_select_update_utensils)

    error_message = {
        'errors': {'name': ['Missing data for required field.']},
        'message': 'Request malformed',
        'status': 400
    }

    validate_unique_mock(mock_select_update_ingrs,
                         [{'name': 'ingredient_3'}, {'name': 'ingredient_4'}])

    validate_unique_mock(mock_select_update_utensils,
                         [{'name': 'utensil_3'}, {'name': 'utensil_4'}])

    post_recipe_fixture.pop('name')
    recipes_create_page = post(post_recipe_fixture)
    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['difficulty'] = 0
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['difficulty'] = ['Must be between 1 and 5.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['difficulty'] = 6
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['difficulty'] = ['Must be between 1 and 5.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture.pop('difficulty')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['difficulty'] = [
        'Missing data for required field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture['people'] = 0
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['people'] = ['Must be between 1 and 12.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['people'] = 13
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['people'] = ['Must be between 1 and 12.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture.pop('people')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['people'] = ['Missing data for required field.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['duration'] = 'error'
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['duration'] = [
        '\'error\' is not a valid choice for this field.'
    ]
    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture.pop('duration')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['duration'] = ['Missing data for required field.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    error_message['errors']['ingredients'] = [
        'There is some entries to update which does not exist.'
    ]

    validate_unique_mock(mock_select_update_ingrs, [{'name': 'ingredient_3'}])

    recipes_create_page = post(post_recipe_fixture)
    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    validate_unique_mock(mock_select_update_ingrs,
                         [{'name': 'ingredient_1'}, {'name': 'ingredient_3'}])

    error_message['errors']['ingredients'] = [
        'There is multiple entries for the same entity.'
    ]

    recipes_create_page = post(post_recipe_fixture)

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['ingredients'][0]['measurement'] = 'error'
    recipes_create_page = post(post_recipe_fixture)

    error_message['errors']['ingredients'] = {}
    error_message['errors']['ingredients']['measurement'] = [
        '\'error\' is not a valid choice for this field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['ingredients'][0].pop('measurement')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['ingredients']['measurement'] = [
        'Missing data for required field.'
    ]
    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['ingredients'][0]['quantity'] = -1

    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['ingredients']['quantity'] = [
        'Must be at least 0.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['ingredients'][0].pop('quantity')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['ingredients']['quantity'] = [
        'Missing data for required field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture['ingredients'][0].pop('name')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['ingredients']['name'] = [
        'Missing data for required field if \'id\' field is not provided.'
    ]
    error_message['errors']['ingredients']['id'] = [
        'Missing data for required field if \'name\' field is not provided.'
    ]
    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    validate_unique_mock(mock_select_update_utensils, [{'name': 'utensil_3'}])

    error_message['errors']['utensils'] = [
        'There is some entries to update which does not exist.'
    ]

    recipes_create_page = post(post_recipe_fixture)

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    validate_unique_mock(mock_select_update_utensils,
                         [{'name': 'utensil_1'}, {'name': 'utensil_3'}])

    error_message['errors']['utensils'] = [
        'There is multiple entries for the same entity.'
    ]

    recipes_create_page = post(post_recipe_fixture)

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture['utensils'][0].pop('name')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['utensils'] = {}
    error_message['errors']['utensils']['name'] = [
        'Missing data for required field if \'id\' field is not provided.'
    ]
    error_message['errors']['utensils']['id'] = [
        'Missing data for required field if \'name\' field is not provided.'
    ]
    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture['category'] = 'error'
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['category'] = [
        '\'error\' is not a valid choice for this field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture.pop('category')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['category'] = ['Missing data for required field.']

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture.pop('directions')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['directions'] = [
        'Missing data for required field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message

    post_recipe_fixture.pop('utensils')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['utensils'] = [
        'Missing data for required field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


    post_recipe_fixture.pop('ingredients')
    recipes_create_page = post(post_recipe_fixture)
    error_message['errors']['ingredients'] = [
        'Missing data for required field.'
    ]

    assert recipes_create_page.status_code == 400
    assert utils.load(recipes_create_page) == error_message


# pylint: disable=unpacking-non-sequence
def test_recipes_put(app, monkeypatch, put_recipes_fixture):
    """Test put /recipes/"""
    put_recipe_1, put_recipe_2 = put_recipes_fixture

    ingredients, ingredients_mock, ingredients_select = initialize_nested(
        put_recipe_1['ingredients'], 'ingredient'
    )
    utensils, utensils_mock, utensils_select = initialize_nested(
        put_recipe_1['utensils'], 'utensil'
    )

    mock_recipe_1, mock_recipe_2 = copy.deepcopy(put_recipes_fixture)

    mock_recipe_1_ingrs = mock_recipe_1.pop('ingredients')
    mock_recipe_1.pop('utensils')

    mock_execute_sql = mock.Mock()
    mock_recipe_count = mock.Mock()

    mock_recipe_ingredients_delete = mock.Mock()
    mock_recipe_utensils_delete = mock.Mock()


    mock_recipe_count.return_value.where.return_value.count.return_value = 2

    # the nested fields will use two requests, the first one for validation,
    # the second one to populate the created recipe

    ingredient_validate = mock.Mock()
    ingredient_select = mock.Mock()

    utensil_validate = mock.Mock()
    utensil_select = mock.Mock()

    # mock db access for the update_recipe function
    recipe_ingredients_insert_many = mock.Mock()
    recipe_ingredients_select = mock.Mock()

    recipe_utensils_insert_many = mock.Mock()
    recipe_utensils_select = mock.Mock()

    (recipe_ingredients_select.return_value
     .join.return_value
     .where.return_value) = []
    (recipe_utensils_select.return_value
     .join.return_value
     .where.return_value) = []

    (ingredient_validate.return_value
     .where.return_value
     .dicts.return_value) = ingredients_select
    (ingredient_select.return_value
     .where.return_value) = ingredients_mock

    (utensil_validate.return_value
     .where.return_value
     .dicts.return_value) = utensils_select
    (utensil_select.return_value
     .where.return_value) = utensils_mock

    mock_ingredient_insert = mock.Mock()
    mock_ingredient_select = mock.Mock(
        side_effect=iter([ingredient_validate(), ingredient_select()])
    )

    mock_utensil_insert = mock.Mock()
    mock_utensil_select = mock.Mock(
        side_effect=iter([utensil_validate(), utensil_select(),
                          recipe_utensils_select()])
    )

    mock_update_recipe_1, mock_update_recipe_2 = mock.Mock(), mock.Mock()

    recipe_1_fake_model = utils.FakeModel(mock_recipe_1)
    (mock_update_recipe_1.return_value
     .where.return_value
     .returning.return_value
     .execute.return_value) = recipe_1_fake_model
    (mock_update_recipe_2.return_value
     .where.return_value
     .returning.return_value
     .execute.return_value) = utils.FakeModel(mock_recipe_2)

    mock_recipe_update = mock.Mock(
        side_effect=iter([mock_update_recipe_1(), mock_update_recipe_2()])
    )

    # monkeypatch all the things! o/
    monkeypatch.setattr('db.connector.database.execute_sql', mock_execute_sql)

    monkeypatch.setattr('db.models.Ingredient.select', mock_ingredient_select)
    monkeypatch.setattr('db.models.Ingredient.insert_many',
                        mock_ingredient_insert)

    monkeypatch.setattr('db.models.RecipeIngredients.delete',
                        mock_recipe_ingredients_delete)
    monkeypatch.setattr('db.models.RecipeIngredients.insert_many',
                        recipe_ingredients_insert_many)
    monkeypatch.setattr('db.models.RecipeIngredients.select',
                        recipe_ingredients_select)

    monkeypatch.setattr('db.models.Utensil.select', mock_utensil_select)
    monkeypatch.setattr('db.models.Utensil.insert_many', mock_utensil_insert)

    monkeypatch.setattr('db.models.RecipeUtensils.delete',
                        mock_recipe_utensils_delete)
    monkeypatch.setattr('db.models.RecipeUtensils.insert_many',
                        recipe_utensils_insert_many)

    monkeypatch.setattr('db.models.Recipe.select', mock_recipe_count)
    monkeypatch.setattr('db.models.Recipe.update', mock_recipe_update)

    # go, go, go
    recipes_create_page = app.put(
        '/recipes/', data=json.dumps({'recipes': put_recipes_fixture}),
        content_type='application/json'
    )

    # check if the tables are correctly locked
    lock_string = 'LOCK TABLE %s IN SHARE ROW EXCLUSIVE MODE'
    lock_utensil = lock_string % helpers.model_entity(db.models.Utensil)
    lock_ingredient = lock_string % helpers.model_entity(db.models.Ingredient)

    utensil_lock = mock.call(lock_utensil)
    ingredient_lock = mock.call(lock_ingredient)

    assert mock_execute_sql.call_args_list == [utensil_lock, ingredient_lock]

    # check if the utensils or ingredients to update exists and if they are not
    # redundant in the same request

    # it has been called two times, one for the validation, one for the return
    assert mock_ingredient_select.call_count == 2
    assert utils.expression_assert(
        mock_ingredient_select, db.models.Ingredient.name
    )
    assert mock_ingredient_select.call_args_list[1] == mock.call()
    assert utils.expression_assert(
        ingredient_validate.return_value.where,
        peewee.Expression(db.models.Ingredient.id, peewee.OP_IN, [3, 4])
    )

    assert mock_utensil_select.call_count == 3
    assert utils.expression_assert(
        mock_utensil_select, db.models.Utensil.name
    )
    assert mock_utensil_select.call_args_list[1:] == [mock.call(), mock.call()]
    assert utils.expression_assert(
        utensil_validate.return_value.where,
        peewee.Expression(db.models.Utensil.id, peewee.OP_IN, [3, 4])
    )

    # update of the recipes
    id_recipe_1 = mock_recipe_1.pop('id')
    id_recipe_2 = mock_recipe_2.pop('id')

    update_calls = [mock.call(**mock_recipe_1), mock.call(**mock_recipe_2)]
    assert mock_recipe_update.call_args_list == update_calls

    where = mock_update_recipe_1.return_value.where
    where_exp = peewee.Expression(db.models.Recipe.id, peewee.OP_EQ,
                                  id_recipe_1)

    assert utils.expression_assert(where, where_exp)
    returning = where.return_value.returning
    assert returning.call_args_list == [mock.call()]

    execute = returning.return_value.execute
    assert execute.call_args_list == [mock.call()]

    where = mock_update_recipe_2.return_value.where
    where_exp = peewee.Expression(db.models.Recipe.id, peewee.OP_EQ,
                                  id_recipe_2)

    assert utils.expression_assert(where, where_exp)
    returning = where.return_value.returning
    assert returning.call_args_list == [mock.call()]

    execute = returning.return_value.execute
    assert execute.call_args_list == [mock.call()]


    # deletion of the recipes ingredients and utensils for update
    # (called for the first recipe update)
    assert mock_recipe_utensils_delete.call_args_list == [mock.call()]
    where = mock_recipe_utensils_delete.return_value.where
    where_exp = peewee.Expression(db.models.RecipeUtensils.recipe,
                                  peewee.OP_EQ, id_recipe_1)
    assert utils.expression_assert(where, where_exp)
    execute = where.return_value.execute
    assert execute.call_args_list == [mock.call()]

    assert mock_recipe_ingredients_delete.call_args_list == [mock.call()]
    where = mock_recipe_ingredients_delete.return_value.where
    where_exp = peewee.Expression(db.models.RecipeIngredients.recipe,
                                  peewee.OP_EQ, id_recipe_1)
    assert utils.expression_assert(where, where_exp)
    execute = where.return_value.execute
    assert execute.call_args_list == [mock.call()]


    # insertion into the tables of the nested fields
    # (called for the first recipe update)
    execute = mock_ingredient_insert.return_value.execute
    assert mock_ingredient_insert.call_count == 1

    (rows, unique_field), _ = mock_ingredient_insert.call_args
    assert rows == ingredients
    assert unique_field.__dict__ == db.models.Ingredient.name.__dict__

    assert execute.call_count == 1
    assert execute.call_args == mock.call()

    execute = mock_utensil_insert.return_value.execute
    assert mock_utensil_insert.call_count == 1

    (rows, unique_field), _ = mock_utensil_insert.call_args
    assert rows == utensils
    assert unique_field.__dict__ == db.models.Utensil.name.__dict__

    assert execute.call_count == 1
    assert execute.call_args == mock.call()

    recipe_utensils_calls = [mock.call([
        {'recipe': recipe_1_fake_model, 'utensil': utensil}
        for utensil in utensils_mock
    ])]

    assert recipe_utensils_insert_many.call_args_list == recipe_utensils_calls

    recipe_ingrs_calls = []
    for ingr_model, recipe_ingr in zip(ingredients_mock, mock_recipe_1_ingrs):
        recipe_ingr = copy.deepcopy(recipe_ingr)
        recipe_ingr['ingredient'] = ingr_model
        recipe_ingr['recipe'] = recipe_1_fake_model
        recipe_ingr['id'] = ingr_model.id
        recipe_ingr['name'] = ingr_model.name
        recipe_ingrs_calls.append(recipe_ingr)

    recipe_ingrs_calls = [mock.call(recipe_ingrs_calls)]
    assert recipe_ingredients_insert_many.call_args_list == recipe_ingrs_calls

    # for the second recipe, the ingredients and utensils are selected from
    # the db
    assert recipe_ingredients_select.call_count == 1
    (recipe_ingrs_model, ingrs_model), _ = recipe_ingredients_select.call_args
    assert recipe_ingrs_model.__dict__ == db.models.RecipeIngredients.__dict__
    assert ingrs_model.__dict__ == db.models.Ingredient.__dict__

    join = recipe_ingredients_select.return_value.join
    assert join.call_count == 1
    (ingr_model,), _ = join.call_args
    assert ingr_model.__dict__ == db.models.Ingredient.__dict__

    where = join.return_value.where
    where_exp = peewee.Expression(db.models.RecipeIngredients.recipe,
                                  peewee.OP_EQ, id_recipe_2)
    assert where.call_count == 1
    assert utils.expression_assert(where, where_exp)


    assert recipe_utensils_select.call_args_list == [mock.call()]

    join = recipe_utensils_select.return_value.join
    (utensil_model,), _ = join.call_args
    assert utensil_model.__dict__ == db.models.RecipeUtensils.__dict__

    where = join.return_value.where
    where_exp = peewee.Expression(db.models.RecipeUtensils.recipe,
                                  peewee.OP_EQ, id_recipe_2)
    assert where.call_count == 1
    assert utils.expression_assert(where, where_exp)

    put_recipe_1['utensils'] = [schemas.utensil_schema.dump(utensil).data
                                for utensil in utensils_mock]

    put_recipe_1['ingredients'] = []
    for ingr_model, recipe_ingr in zip(ingredients_mock, mock_recipe_1_ingrs):
        recipe_ingr = copy.deepcopy(recipe_ingr)
        recipe_ingr.update(**schemas.ingredient_schema.dump(ingr_model).data)
        put_recipe_1['ingredients'].append(recipe_ingr)

    recipes = {'recipes': [put_recipe_1, put_recipe_2]}
    assert utils.load(recipes_create_page) == recipes


def test_recipe_get_ingredients(app, monkeypatch):
    """Test /recipes/<id>/ingredients"""

    ingredients = [{'ingredient_1' : 'ingredient_1_content'}]

    mock_recipe_get = mock.Mock()
    monkeypatch.setattr('db.models.Recipe.get', mock_recipe_get)

    mock_recipe_ingredients_select = mock.Mock()
    (mock_recipe_ingredients_select.return_value
     .join.return_value
     .where.return_value
     .dicts.return_value) = ingredients

    monkeypatch.setattr(
        'db.models.RecipeIngredients.select',
        mock_recipe_ingredients_select
    )

    ingredients_page = app.get('/recipes/1/ingredients')

    get_exp = peewee.Expression(db.models.Recipe.id, peewee.OP_EQ, 1)

    assert mock_recipe_get.call_count == 1
    assert utils.expression_assert(mock_recipe_get, get_exp)

    assert mock_recipe_ingredients_select.call_count == 1
    assert mock_recipe_ingredients_select.call_args == mock.call(
        db.models.RecipeIngredients.quantity,
        db.models.RecipeIngredients.measurement,
        db.models.Ingredient
    )

    join = mock_recipe_ingredients_select.return_value.join
    assert join.call_count == 1
    assert join.call_args == mock.call(db.models.Ingredient)

    where = join.return_value.where
    where_exp = peewee.Expression(db.models.RecipeIngredients.recipe,
                                  peewee.OP_EQ, 1)

    assert where.call_count == 1
    assert utils.expression_assert(where, where_exp)

    assert utils.load(ingredients_page) == {'ingredients': ingredients}


def test_recipe_get_ingredients_404(app, monkeypatch):
    """Test /recipes/<id>/ingredients with recipe not found"""

    monkeypatch.setattr(
        'db.models.Recipe.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    recipe = app.get('/recipes/2/ingredients')
    assert recipe.status_code == 404


def test_recipe_get_utensils(app, monkeypatch):
    """Test /recipes/<id>/utensils"""

    utensils = [{'utensil_1' : 'utensil_1_content'}]

    mock_recipe_get = mock.Mock()
    monkeypatch.setattr('db.models.Recipe.get', mock_recipe_get)

    mock_utensil_select = mock.Mock()
    (mock_utensil_select.return_value
     .join.return_value
     .where.return_value
     .dicts.return_value) = utensils

    monkeypatch.setattr('db.models.Utensil.select', mock_utensil_select)

    utensils_page = app.get('/recipes/1/utensils')

    get_exp = peewee.Expression(db.models.Recipe.id, peewee.OP_EQ, 1)
    assert mock_recipe_get.call_count == 1
    assert utils.expression_assert(mock_recipe_get, get_exp)

    assert mock_utensil_select.call_count == 1
    assert mock_utensil_select.call_args == mock.call()

    join = mock_utensil_select.return_value.join
    assert join.call_count == 1
    assert join.call_args == mock.call(db.models.RecipeUtensils)

    where = join.return_value.where
    where_exp = peewee.Expression(db.models.RecipeUtensils.recipe,
                                  peewee.OP_EQ, 1)

    assert where.call_count == 1
    assert utils.expression_assert(where, where_exp)

    assert utils.load(utensils_page) == {'utensils': utensils}


def test_recipe_get_utensils_404(app, monkeypatch):
    """Test /recipes/<id>/utensils with recipe not found"""

    monkeypatch.setattr(
        'db.models.Recipe.get',
        mock.Mock(side_effect=peewee.DoesNotExist())
    )
    recipe = app.get('/recipes/2/utensils')
    assert recipe.status_code == 404

