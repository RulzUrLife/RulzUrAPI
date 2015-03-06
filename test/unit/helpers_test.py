""""Test rulzurapi helpers"""

import json
import unittest.mock as mock

import pytest

import utils.helpers as helpers
import test.utils as utils

def test_api_exception():
    api_exception = helpers.APIException('Error Message')
    assert api_exception.args == ('Error Message', 400, None)

    api_exception = helpers.APIException('Error Message', 500)
    assert api_exception.args == ('Error Message', 500, None)

    api_exception = helpers.APIException('Error Message', 500, {'foo': 'bar'})
    assert api_exception.args == ('Error Message', 500, {'foo': 'bar'})


def test_jsonify_api_exception(app):
    error_msg = {'message': 'Error Message', 'status_code': 400}
    api_exception = helpers.APIException('Error Message')

    with app.application.test_request_context():
        response = helpers.jsonify_api_exception(api_exception)
        assert response.status_code == 400
        assert utils.load(response) == error_msg

    error_msg = {'message': 'Error Message', 'status_code': 500, 'foo': 'bar'}
    api_exception = helpers.APIException('Error Message', 500, {'foo': 'bar'})

    with app.application.test_request_context():
        response = helpers.jsonify_api_exception(api_exception)
        assert response.status_code == 500
        assert utils.load(response) == error_msg


def test_raise_or_return(app, monkeypatch):
    mock_schema_load = mock.Mock(return_value=(mock.sentinel.rv, None))
    mock_schema = mock.Mock(load=mock_schema_load)
    mock_flask_request = mock.Mock(json=mock.sentinel.request_json)

    schema_load_calls = [mock.call(mock.sentinel.request_json)]
    with app.application.test_request_context() as request_context:
        monkeypatch.setattr('flask.request', mock_flask_request)
        rv = helpers.raise_or_return(mock_schema)

        assert mock_schema_load.call_args_list == schema_load_calls
        assert rv == mock.sentinel.rv


def test_raise_or_return_error(app):
    mock_schema_load = mock.Mock(side_effect=AttributeError)
    mock_schema = mock.Mock(load=mock_schema_load)
    api_exc = ('Request malformed', 400, {'errors': 'JSON might be incorrect'})

    with app.application.test_request_context() as request_context:
        with pytest.raises(helpers.APIException) as excinfo:
            helpers.raise_or_return(mock_schema)

    assert excinfo.value.args == api_exc

    mock_schema_load = mock.Mock(return_value=(None, mock.sentinel.errors))
    mock_schema = mock.Mock(load=mock_schema_load)
    api_exc = ('Request malformed', 400, {'errors': mock.sentinel.errors})

    with app.application.test_request_context() as request_context:
        with pytest.raises(helpers.APIException) as excinfo:
            helpers.raise_or_return(mock_schema)

    assert excinfo.value.args == api_exc


def test_model_entity(monkeypatch):
    mock_model_as_entity = mock.Mock(return_value=mock.sentinel.entity)
    mock_model = mock.Mock(_as_entity=mock_model_as_entity)

    mock_query_compiler = mock.Mock()
    mock_parse_entity = mock_query_compiler.return_value._parse_entity
    mock_parse_entity.return_value = (mock.sentinel.model_entity, None)

    monkeypatch.setattr('peewee.QueryCompiler', mock_query_compiler)

    me = helpers.model_entity(mock_model)

    parse_entity_calls = [mock.call(mock.sentinel.entity, None, None)]

    assert mock_query_compiler.call_args_list == [mock.call()]
    assert mock_model_as_entity.call_args_list == [mock.call()]
    assert mock_parse_entity.call_args_list == parse_entity_calls
    assert me == mock.sentinel.model_entity

