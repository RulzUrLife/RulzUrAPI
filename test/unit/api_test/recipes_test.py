"""API endpoints testing"""
# pylint: disable=no-self-use, too-many-locals, too-many-statements
import unittest.mock as mock

import peewee
import pytest

import api.recipes
import db.models as models
import test.utils as utils
import utils.helpers as helpers
import utils.schemas as schemas


class TestUtilityFunctions(object):
    """Test suite for utility functions from the recipe endpoint"""

    @staticmethod
    @pytest.fixture
    def update_recipe_fixture_mocks(monkeypatch):
        """fixture for update_recipe function"""
        mocks = dict(
            mock_recipe_update=mock.Mock(),
            mock_ingrs_select=mock.Mock(),
            mock_ingrs_delete=mock.Mock(),
            mock_ingrs_insert=mock.Mock(),
            mock_ingrs_parsing=mock.Mock(),
            mock_utensils_select=mock.Mock(),
            mock_utensils_delete=mock.Mock(),
            mock_utensils_insert=mock.Mock(),
            mock_utensils_parsing=mock.Mock()
        )

        mocks = type('Mocks', (object,), mocks)

        # monkeypatch all the things o/
        monkeypatch.setattr('db.models.Recipe.update',
                            mocks.mock_recipe_update)
        monkeypatch.setattr('db.models.RecipeIngredients.select',
                            mocks.mock_ingrs_select)
        monkeypatch.setattr('db.models.RecipeIngredients.delete',
                            mocks.mock_ingrs_delete)
        monkeypatch.setattr('db.models.RecipeIngredients.insert_many',
                            mocks.mock_ingrs_insert)
        monkeypatch.setattr('api.recipes.ingredients_parsing',
                            mocks.mock_ingrs_parsing)

        monkeypatch.setattr('db.models.Utensil.select',
                            mocks.mock_utensils_select)
        monkeypatch.setattr('db.models.RecipeUtensils.delete',
                            mocks.mock_utensils_delete)
        monkeypatch.setattr('db.models.RecipeUtensils.insert_many',
                            mocks.mock_utensils_insert)
        monkeypatch.setattr('api.recipes.utensils_parsing',
                            mocks.mock_utensils_parsing)

        return mocks


    def test_get_recipe(self, monkeypatch):
        """Test the get_recipe method"""
        mock_recipe_get = mock.Mock(return_value=mock.sentinel.recipe)
        get_clause = peewee.Expression(models.Recipe.id, peewee.OP.EQ,
                                       mock.sentinel.recipe_id)
        monkeypatch.setattr('db.models.Recipe.get', mock_recipe_get)
        returned_recipe = api.recipes.get_recipe(mock.sentinel.recipe_id)

        assert returned_recipe == mock.sentinel.recipe
        assert mock_recipe_get.call_args_list == [mock.call(get_clause)]


    def test_get_recipe_404(self, monkeypatch):
        """Test the get_recipe method with a non existing recipe"""
        mock_recipe_get = mock.Mock(side_effect=peewee.DoesNotExist)

        monkeypatch.setattr('db.models.Recipe.get', mock_recipe_get)
        with pytest.raises(helpers.APIException) as excinfo:
            api.recipes.get_recipe(None)

        assert excinfo.value.args == ('Recipe not found', 404, None)


    def test_select_recipes(self, monkeypatch):
        """Test the select_recipes method"""
        mock_rcp_select = mock.Mock()
        join_rcp_ingrs = mock_rcp_select.return_value.join
        join_ingr = join_rcp_ingrs.return_value.join
        switch = join_ingr.return_value.switch
        join_rcp_utensils = switch.return_value.join
        join_utensil = join_rcp_utensils.return_value.join
        where = join_utensil.return_value.where
        aggregate_rows = where.return_value.aggregate_rows
        execute = aggregate_rows.return_value.execute
        execute.return_value = mock.sentinel.rcps

        monkeypatch.setattr('db.models.Recipe.select', mock_rcp_select)
        rcps = api.recipes.select_recipes(mock.sentinel.where_clause)

        select_calls = [mock.call(models.Recipe,
                                  models.RecipeIngredients, models.Ingredient,
                                  models.RecipeUtensils, models.Utensil)]
        join_rcp_ingrs_calls = [mock.call(models.RecipeIngredients)]
        join_rcp_utensils_calls = [mock.call(models.RecipeUtensils)]

        assert rcps == mock.sentinel.rcps
        assert mock_rcp_select.call_args_list == select_calls
        assert join_rcp_ingrs.call_args_list == join_rcp_ingrs_calls
        assert join_ingr.call_args_list == [mock.call(models.Ingredient)]
        assert switch.call_args_list == [mock.call(models.Recipe)]
        assert join_rcp_utensils.call_args_list == join_rcp_utensils_calls
        assert join_utensil.call_args_list == [mock.call(models.Utensil)]
        assert where.call_args_list == [mock.call(mock.sentinel.where_clause)]
        assert aggregate_rows.call_args_list == [mock.call()]
        assert execute.call_args_list == [mock.call()]


    def test_lock_table(self, monkeypatch):
        """Test the db lock_table feature"""
        mock_model_entity = mock.Mock(return_value=mock.sentinel.me)
        mock_execute_sql = mock.Mock()

        monkeypatch.setattr('utils.helpers.model_entity', mock_model_entity)
        monkeypatch.setattr('db.connector.database.execute_sql',
                            mock_execute_sql)

        api.recipes.lock_table(mock.sentinel.model)
        sql_str = ('LOCK TABLE %s IN SHARE ROW EXCLUSIVE MODE' %
                   str(mock.sentinel.me))
        model_entity_calls = [mock.call(mock.sentinel.model)]
        assert mock_model_entity.call_args_list == model_entity_calls
        assert mock_execute_sql.call_args_list == [mock.call(sql_str)]


    def test_get_or_insert(self, monkeypatch, model):
        """Test the get_or_insert function"""
        reset_mocks = lambda mocks: [mock.reset_mock() for mock in mocks]
        mock_model_insert_many = mock.Mock()
        insert_many_execute = mock_model_insert_many.return_value.execute

        mock_model_select = mock.Mock()
        model_select_where = mock_model_select.return_value.where
        model_select_where.return_value = [mock.sentinel.rv]

        mock_elt_insert = mock.MagicMock()
        mock_elt_insert.__getitem__.return_value = mock.sentinel.elt_insert

        mocks = [mock_model_insert_many, insert_many_execute, mock_elt_insert,
                 mock_model_select, model_select_where]

        monkeypatch.setattr(model, 'insert_many', mock_model_insert_many)
        monkeypatch.setattr(model, 'select', mock_model_select)

        elts_insert = [mock_elt_insert]
        elts_get = [mock.sentinel.elt_get]

        rv = api.recipes.get_or_insert(model, elts_insert, elts_get)

        where_exp_get = peewee.Expression(model.id, peewee.OP.IN,
                                          [mock.sentinel.elt_get])
        where_exp_insert = peewee.Expression(model.name, peewee.OP.IN,
                                             [mock.sentinel.elt_insert])
        where_exp = peewee.Expression(where_exp_get, peewee.OP.OR,
                                      where_exp_insert)

        insert_many_calls = [mock.call(elts_insert, model.name)]
        get_item_calls = [mock.call('name')]
        assert rv == [mock.sentinel.rv]
        assert mock_model_insert_many.call_args_list == insert_many_calls
        assert insert_many_execute.call_args_list == [mock.call()]
        assert mock_elt_insert.__getitem__.call_args_list == get_item_calls
        assert mock_model_select.call_args_list == [mock.call()]
        assert model_select_where.call_args_list == [mock.call(where_exp)]

        reset_mocks(mocks)
        rv = api.recipes.get_or_insert(model, elts_insert, None)

        assert rv == [mock.sentinel.rv]
        assert mock_model_insert_many.call_args_list == insert_many_calls
        assert insert_many_execute.call_args_list == [mock.call()]
        assert mock_elt_insert.__getitem__.call_args_list == get_item_calls
        assert mock_model_select.call_args_list == [mock.call()]
        assert model_select_where.call_args_list == [
            mock.call(where_exp_insert)
        ]

        reset_mocks(mocks)
        rv = api.recipes.get_or_insert(model, None, elts_get)

        assert rv == [mock.sentinel.rv]
        assert mock_model_insert_many.call_args_list == []
        assert insert_many_execute.call_args_list == []
        assert mock_elt_insert.__getitem__.call_args_list == []
        assert mock_model_select.call_args_list == [mock.call()]
        assert model_select_where.call_args_list == [mock.call(where_exp_get)]

        reset_mocks(mocks)
        rv = api.recipes.get_or_insert(model, None, None)

        assert rv == []
        assert mock_model_insert_many.call_args_list == []
        assert insert_many_execute.call_args_list == []
        assert mock_elt_insert.__getitem__.call_args_list == []
        assert mock_model_select.call_args_list == []
        assert model_select_where.call_args_list == []


    def test_ingredients_parsing(self, monkeypatch):
        """Test the ingredients_parsing function"""
        mock_get_or_insert = mock.Mock()
        mock_get = mock.MagicMock()
        mock_insert = mock.MagicMock()
        mock_db_get = mock.Mock()
        mock_db_insert = mock.Mock()

        get_id_sentinel = str(mock.sentinel.get_id)
        get_name_sentinel = str(mock.sentinel.get_name)
        insert_id_sentinel = str(mock.sentinel.insert_id)
        insert_name_sentinel = str(mock.sentinel.insert_name)

        mock_get_or_insert.return_value = [mock_db_get, mock_db_insert]

        mock_get.pop.side_effect = iter([get_id_sentinel, None])
        mock_db_get.configure_mock(id=get_id_sentinel, name=get_name_sentinel)

        mock_insert.pop.side_effect = iter([None, insert_name_sentinel])
        mock_db_insert.configure_mock(id=insert_id_sentinel,
                                      name=insert_name_sentinel)
        monkeypatch.setattr('api.recipes.get_or_insert', mock_get_or_insert)

        rv = api.recipes.ingredients_parsing([mock_get, mock_insert])

        pop_calls = [mock.call('id', None), mock.call('name', None)]
        get_or_insert_calls = [mock.call(models.Ingredient,
                                         [{'name': insert_name_sentinel}],
                                         [get_id_sentinel])]
        get_setitem_calls = [mock.call('ingredient', mock_db_get)]
        insert_setitem_calls = [mock.call('ingredient', mock_db_insert)]

        assert rv == [mock_get, mock_insert]
        assert mock_get.pop.call_args_list == pop_calls
        assert mock_insert.pop.call_args_list == pop_calls
        assert mock_get_or_insert.call_args_list == get_or_insert_calls
        assert mock_get.__setitem__.call_args_list == get_setitem_calls
        assert mock_insert.__setitem__.call_args_list == insert_setitem_calls


    def test_utensils_parsing(self, monkeypatch):
        """Test utensils_parsing function"""
        mock_get_or_insert = mock.Mock()
        mock_get = mock.MagicMock()
        mock_insert = mock.MagicMock()

        mock_get.get.return_value = mock.sentinel.get
        mock_get.__getitem__.return_value = mock.sentinel.get
        mock_insert.get.return_value = None
        mock_get_or_insert.return_value = mock.sentinel.get_or_insert_rv

        monkeypatch.setattr('api.recipes.get_or_insert', mock_get_or_insert)

        rv = api.recipes.utensils_parsing([mock_get, mock_insert])

        get_id_calls = [mock.call('id'), mock.call('id')]
        get_or_insert_calls = [
            mock.call(models.Utensil, [mock_insert], [mock.sentinel.get])
        ]

        assert rv == mock.sentinel.get_or_insert_rv
        assert mock_get.get.call_args_list == get_id_calls
        assert mock_insert.get.call_args_list == get_id_calls
        assert mock_get.__getitem__.call_args_list == [mock.call('id')]
        assert mock_get_or_insert.call_args_list == get_or_insert_calls


    def test_update_recipe(self, update_recipe_fixture_mocks):
        """Test update_recipe function"""
        recipe = {str(mock.sentinel.recipe_attr): mock.sentinel.recipe_attr}
        mocks = update_recipe_fixture_mocks
        mock_recipe = mock.MagicMock(wraps=recipe)
        mock_db_recipe = mock.Mock()
        mock_ingr = mock.MagicMock()
        mock_recipe.pop.side_effect = iter([mock.sentinel.recipe_id,
                                            mock.sentinel.ingrs,
                                            mock.sentinel.utensils])

        update_where = mocks.mock_recipe_update.return_value.where
        update_returning = update_where.return_value.returning
        update_execute = update_returning.return_value.execute
        update_execute.return_value = mock_db_recipe

        mocks.mock_ingrs_parsing.return_value = [mock_ingr]
        mocks.mock_utensils_parsing.return_value = [mock.sentinel.utensil]

        rv = api.recipes.update_recipe(mock_recipe)
        pop_calls = [mock.call('id'),
                     mock.call('ingredients', None),
                     mock.call('utensils', None)]

        where_exp = peewee.Expression(models.Recipe.id, peewee.OP.EQ,
                                      mock.sentinel.recipe_id)

        assert rv == mock_db_recipe
        assert rv.ingredients == [mock_ingr]
        assert rv.utensils == [mock.sentinel.utensil]

        assert mock_recipe.pop.call_args_list == pop_calls
        assert mocks.mock_recipe_update.call_args_list == [mock.call(**recipe)]
        assert update_where.call_args_list == [mock.call(where_exp)]
        assert update_returning.call_args_list == [mock.call()]
        assert update_execute.call_args_list == [mock.call()]

        # checks the replacement of old ingredients
        mock_ingrs_delete = mocks.mock_ingrs_delete
        ingrs_delete_where = mock_ingrs_delete.return_value.where
        ingrs_delete_execute = ingrs_delete_where.return_value.execute
        ingrs_insert_many = mocks.mock_ingrs_insert
        ingrs_insert_execute = ingrs_insert_many.return_value.execute

        ingrs_parsing_calls = [mock.call(mock.sentinel.ingrs)]
        ingr_setitem_calls = [mock.call('recipe', mock_db_recipe)]
        where_exp = peewee.Expression(models.RecipeIngredients.recipe,
                                      peewee.OP.EQ, mock.sentinel.recipe_id)

        assert mock_ingrs_delete.call_args_list == [mock.call()]
        assert mocks.mock_ingrs_parsing.call_args_list == ingrs_parsing_calls
        assert mock_ingr.__setitem__.call_args_list == ingr_setitem_calls

        assert ingrs_delete_where.call_args_list == [mock.call(where_exp)]
        assert ingrs_delete_execute.call_args_list == [mock.call()]
        assert ingrs_insert_many.call_args_list == [mock.call([mock_ingr])]
        assert ingrs_insert_execute.call_args_list == [mock.call()]

        # checks the replacement of old utensils
        mock_utensils_delete = mocks.mock_utensils_delete
        utensils_delete_where = mock_utensils_delete.return_value.where
        utensils_delete_execute = utensils_delete_where.return_value.execute
        utensils_insert_many = mocks.mock_utensils_insert
        utensils_insert_execute = utensils_insert_many.return_value.execute

        mock_utensils_parsing = mocks.mock_utensils_parsing
        utensils_parsing_calls = [mock.call(mock.sentinel.utensils)]
        where_exp = peewee.Expression(models.RecipeIngredients.recipe,
                                      peewee.OP.EQ, mock.sentinel.recipe_id)
        utensil_elts = [{'recipe': mock_db_recipe,
                         'utensil': mock.sentinel.utensil}]

        assert mock_utensils_delete.call_args_list == [mock.call()]
        assert mock_utensils_parsing.call_args_list == utensils_parsing_calls

        assert utensils_delete_where.call_args_list == [mock.call(where_exp)]
        assert utensils_delete_execute.call_args_list == [mock.call()]
        assert utensils_insert_many.call_args_list == [mock.call(utensil_elts)]
        assert utensils_insert_execute.call_args_list == [mock.call()]


    def test_update_recipe_no_foreign(self, update_recipe_fixture_mocks):
        """Test update_recipe function with no foreign key linking"""
        mocks = update_recipe_fixture_mocks
        mock_recipe = mock.MagicMock(wraps={})
        mock_db_recipe = mock.Mock()
        mock_recipe.pop.side_effect = iter([mock.sentinel.recipe_id,
                                            None, None])

        (mocks.mock_recipe_update.return_value
         .where.return_value
         .returning.return_value
         .execute.return_value) = mock_db_recipe

        ingrs_select = mocks.mock_ingrs_select
        ingrs_select_join = ingrs_select.return_value.join
        ingrs_select_where = ingrs_select_join.return_value.where
        ingrs_select_where.return_value = [mock.sentinel.ingr]

        utensils_select = mocks.mock_utensils_select
        utensils_select_join = utensils_select.return_value.join
        utensils_select_where = utensils_select_join.return_value.where
        utensils_select_where.return_value = [mock.sentinel.utensil]

        rv = api.recipes.update_recipe(mock_recipe)

        ingrs_select_calls = [mock.call(models.RecipeIngredients,
                                        models.Ingredient)]
        ingrs_select_join_calls = [mock.call(models.Ingredient)]
        ingrs_select_where_calls = [mock.call(
            peewee.Expression(models.RecipeIngredients.recipe, peewee.OP.EQ,
                              mock.sentinel.recipe_id)
        )]

        utensils_select_calls = [mock.call()]
        utensils_select_join_calls = [mock.call(models.RecipeUtensils)]
        utensils_select_where_calls = [mock.call(
            peewee.Expression(models.RecipeUtensils.recipe, peewee.OP.EQ,
                              mock.sentinel.recipe_id)
        )]

        assert rv == mock_db_recipe
        assert rv.ingredients == [mock.sentinel.ingr]
        assert rv.utensils == [mock.sentinel.utensil]

        assert ingrs_select.call_args_list == ingrs_select_calls
        assert ingrs_select_join.call_args_list == ingrs_select_join_calls
        assert ingrs_select_where.call_args_list == ingrs_select_where_calls


        assert utensils_select.call_args_list == utensils_select_calls
        assert utensils_select_join.call_args_list == (
            utensils_select_join_calls
        )
        assert utensils_select_where.call_args_list == (
            utensils_select_where_calls
        )

class TestRecipeAPI(object):
    """Test the /recipes endpoint"""

    def test_recipes_list(self, app, monkeypatch):
        """Test get /recipes/"""
        mock_recipes = [str(mock.sentinel.recipe)]
        mock_recipe_select = mock.Mock()

        dicts = mock_recipe_select.return_value.dicts
        dicts.return_value = mock_recipes

        monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)
        recipes_page = app.get('/recipes/')

        assert recipes_page.status_code == 200
        assert mock_recipe_select.call_args_list == [mock.call()]
        assert dicts.call_args_list == [mock.call()]
        assert utils.load(recipes_page) == {'recipes': mock_recipes}


    def test_recipes_post(self, app, monkeypatch):
        """Test post /recipes/"""
        schema = schemas.recipe_schema_post
        recipe = {
            str(mock.sentinel.recipe_key): str(mock.sentinel.recipe)
        }

        mock_recipe = mock.MagicMock(spec=dict)
        mock_lock_table = mock.Mock()
        mock_raise_or_return = mock.Mock(return_value=mock_recipe)

        mock_ingr = mock.MagicMock()
        mock_ingrs = [mock_ingr]
        mock_ingrs_parsing = mock.Mock(return_value=mock_ingrs)
        mock_ingrs_insert = mock.Mock()

        mock_utensils = [mock.sentinel.utensil]
        mock_utensils_parsing = mock.Mock(return_value=mock_utensils)
        mock_utensils_insert = mock.Mock()

        mock_recipe_create = mock.Mock(return_value=mock_recipe)
        mock_recipe_select = mock.Mock()
        mock_recipe_schema_dump = mock.Mock(
            return_value=mock.Mock(data=str(mock.sentinel.recipe))
        )

        monkeypatch.setattr('utils.helpers.raise_or_return',
                            mock_raise_or_return)
        monkeypatch.setattr('db.models.Recipe.create', mock_recipe_create)
        monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)

        monkeypatch.setattr('db.models.RecipeIngredients.insert_many',
                            mock_ingrs_insert)
        monkeypatch.setattr('db.models.RecipeUtensils.insert_many',
                            mock_utensils_insert)

        monkeypatch.setattr('api.recipes.ingredients_parsing',
                            mock_ingrs_parsing)
        monkeypatch.setattr('api.recipes.utensils_parsing',
                            mock_utensils_parsing)
        monkeypatch.setattr('api.recipes.lock_table', mock_lock_table)

        monkeypatch.setattr('utils.schemas.recipe_schema.dump',
                            mock_recipe_schema_dump)

        recipe_where = mock_recipe_select.return_value.where
        recipe_count = recipe_where.return_value.count
        recipe_count.return_value = 0


        recipes_create_page = app.post('/recipes/', data=recipe)

        lock_table_calls = [mock.call(models.Utensil),
                            mock.call(models.Ingredient)]
        raise_or_return_calls = [mock.call(schema)]
        recipe_where_exp = peewee.Expression(models.Recipe.name, peewee.OP.EQ,
                                             mock_recipe.get('name'))

        ingrs_parsing_calls = [mock.call(mock_recipe['ingredients'])]
        utensils_parsing_calls = [mock.call(mock_recipe['utensils'])]

        utensil_elts = [{'recipe': mock_recipe,
                         'utensil': mock.sentinel.utensil}]
        assert mock_lock_table.call_args_list == lock_table_calls
        assert mock_raise_or_return.call_args_list == raise_or_return_calls

        assert mock_recipe_select.call_args_list == [mock.call()]
        assert recipe_where.call_args_list == [mock.call(recipe_where_exp)]
        assert recipe_count.call_args_list == [mock.call()]

        assert mock_ingrs_parsing.call_args_list == ingrs_parsing_calls
        assert mock_utensils_parsing.call_args_list == utensils_parsing_calls

        assert mock_utensils_insert.call_args_list == [mock.call(utensil_elts)]
        assert mock_ingrs_insert.call_args_list == [mock.call(mock_ingrs)]

        assert recipes_create_page.status_code == 201
        assert utils.load(recipes_create_page) == {
            'recipe': str(mock.sentinel.recipe)
        }

    def test_utensils_post_409(self, app, monkeypatch):
        """Test post /recipes/ with a conflict"""
        mock_raise_or_return = mock.Mock(return_value=mock.Mock(spec=dict))
        mock_recipe_select = mock.Mock()

        (mock_recipe_select.return_value
         .where.return_value
         .count.return_value) = 1

        monkeypatch.setattr('utils.helpers.raise_or_return',
                            mock_raise_or_return)
        monkeypatch.setattr('db.models.Recipe.select', mock_recipe_select)

        recipes_create_page = app.post('/recipes/', data={})
        error_msg = {'message': 'Recipe already exists.', 'status_code': 409}

        assert recipes_create_page.status_code == 409
        assert utils.load(recipes_create_page) == error_msg


    def test_recipes_put(self, app, monkeypatch):
        """Test put /recipes/"""
        recipe = {str(mock.sentinel.recipe_key): str(mock.sentinel.recipe)}
        recipes = {'recipes': [recipe]}
        mock_recipes = mock.MagicMock(wraps=recipes, spec=dict)

        schema = schemas.recipe_schema_list

        mock_lock_table = mock.Mock()
        mock_raise_or_return = mock.Mock(return_value=recipes)
        mock_update_recipe = mock.Mock(return_value=mock.sentinel.recipe)
        mock_recipe_schema_dump = mock.Mock(
            return_value=mock.Mock(data=mock_recipes)
        )

        monkeypatch.setattr('api.recipes.lock_table', mock_lock_table)
        monkeypatch.setattr('utils.helpers.raise_or_return', mock_raise_or_return)
        monkeypatch.setattr('api.recipes.update_recipe', mock_update_recipe)
        monkeypatch.setattr(schema, 'dump', mock_recipe_schema_dump)

        lock_table_calls = [mock.call(models.Utensil),
                            mock.call(models.Ingredient)]
        schema_dump_calls = [mock.call({'recipes': [mock.sentinel.recipe]})]
        update_calls = [mock.call(recipe)]

        recipes_update_page = app.put('/recipes/', data={})

        assert recipes_update_page.status_code == 200
        assert utils.load(recipes_update_page) == recipes

        assert mock_lock_table.call_args_list == lock_table_calls
        assert mock_raise_or_return.call_args_list == [mock.call(schema)]
        assert mock_update_recipe.call_args_list == update_calls
        assert mock_recipe_schema_dump.call_args_list == schema_dump_calls


    def test_recipe_get(self, app, monkeypatch):
        """Test get /recipes/<id>"""
        recipe = mock.sentinel.recipe
        mock_select_recipes = mock.Mock(return_value=iter([recipe]))
        mock_recipe_schema_dump = mock.Mock(return_value=(str(recipe), None))

        monkeypatch.setattr('api.recipes.select_recipes', mock_select_recipes)
        monkeypatch.setattr('utils.schemas.recipe_schema.dump',
                            mock_recipe_schema_dump)

        recipe_get_page = app.get('/recipes/1/')

        select_recipes_calls = [mock.call(
            peewee.Expression(models.Recipe.id, peewee.OP.EQ, 1)
        )]

        assert recipe_get_page.status_code == 200
        assert utils.load(recipe_get_page) == {'recipe': str(recipe)}

        assert mock_select_recipes.call_args_list == select_recipes_calls
        assert mock_recipe_schema_dump.call_args_list == [mock.call(recipe)]


    def test_recipe_get_404(self, app, monkeypatch):
        """Test get /recipes/<id> with a non existing recipe"""
        mock_select_recipes = mock.Mock(side_effect=StopIteration)

        monkeypatch.setattr('api.recipes.select_recipes', mock_select_recipes)

        recipe_get_page = app.get('/recipes/1/')

        assert recipe_get_page.status_code == 404
        assert utils.load(recipe_get_page) == {'status_code': 404,
                                               'message': 'Recipe not found'}


    def test_recipe_get_ingredients(self, app, monkeypatch):
        """Test /recipes/<id>/ingredients"""
        ingrs = [str(mock.sentinel.ingredients)]

        mock_get_recipe = mock.Mock()
        mock_ingrs_select = mock.Mock()

        monkeypatch.setattr('api.recipes.get_recipe', mock_get_recipe)
        monkeypatch.setattr('db.models.RecipeIngredients.select',
                            mock_ingrs_select)

        ingrs_join = mock_ingrs_select.return_value.join
        ingrs_where = ingrs_join.return_value.where
        ingrs_dicts = ingrs_where.return_value.dicts
        ingrs_dicts.return_value = ingrs

        recipe_ingrs_page = app.get('/recipes/1/ingredients/')

        ingrs_select_calls = [mock.call(models.RecipeIngredients.quantity,
                                        models.RecipeIngredients.measurement,
                                        models.Ingredient)]
        ingrs_join_calls = [mock.call(models.Ingredient)]
        ingrs_where_calls = [mock.call(
            peewee.Expression(models.RecipeIngredients.recipe, peewee.OP.EQ, 1)
        )]
        ingrs_dicts_calls = [mock.call()]

        assert recipe_ingrs_page.status_code == 200
        assert utils.load(recipe_ingrs_page) == {'ingredients': ingrs}

        assert mock_get_recipe.call_args_list == [mock.call(1)]
        assert mock_ingrs_select.call_args_list == ingrs_select_calls
        assert ingrs_join.call_args_list == ingrs_join_calls
        assert ingrs_where.call_args_list == ingrs_where_calls
        assert ingrs_dicts.call_args_list == ingrs_dicts_calls


    def test_recipe_get_utensils(self, app, monkeypatch):
        """Test /recipes/<id>/utensils"""
        utensils = [str(mock.sentinel.utensils)]

        mock_get_recipe = mock.Mock()
        mock_utensils_select = mock.Mock()

        monkeypatch.setattr('api.recipes.get_recipe', mock_get_recipe)
        monkeypatch.setattr('db.models.Utensil.select', mock_utensils_select)

        utensils_join = mock_utensils_select.return_value.join
        utensils_where = utensils_join.return_value.where
        utensils_dicts = utensils_where.return_value.dicts
        utensils_dicts.return_value = utensils

        recipe_utensils_page = app.get('/recipes/1/utensils/')

        utensils_select_calls = [mock.call()]
        utensils_join_calls = [mock.call(models.RecipeUtensils)]
        utensils_where_calls = [mock.call(
            peewee.Expression(models.RecipeUtensils.recipe, peewee.OP.EQ, 1)
        )]
        utensils_dicts_calls = [mock.call()]

        assert recipe_utensils_page.status_code == 200
        assert utils.load(recipe_utensils_page) == {'utensils': utensils}

        assert mock_get_recipe.call_args_list == [mock.call(1)]
        assert mock_utensils_select.call_args_list == utensils_select_calls
        assert utensils_join.call_args_list == utensils_join_calls
        assert utensils_where.call_args_list == utensils_where_calls
        assert utensils_dicts.call_args_list == utensils_dicts_calls


