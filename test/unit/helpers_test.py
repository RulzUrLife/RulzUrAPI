""""Test rulzurapi helpers"""

import unittest.mock as mock

import flask
import pytest

import utils.helpers as helpers
import test.utils as utils

def test_api_exception():
    """Test APIException"""
    api_exception = helpers.APIException('Error Message')
    assert api_exception.args == ('Error Message', 400, None)

    api_exception = helpers.APIException('Error Message', 500)
    assert api_exception.args == ('Error Message', 500, None)

    api_exception = helpers.APIException('Error Message', 500, {'foo': 'bar'})
    assert api_exception.args == ('Error Message', 500, {'foo': 'bar'})

@pytest.mark.usefixtures('request_context')
def test_jsonify_api_exception():
    """Test the jsonify result of APIException"""
    error_msg = {'message': 'Error Message', 'status_code': 400}
    api_exception = helpers.APIException('Error Message')

    response, status_code = helpers.jsonify_api_exception(api_exception)
    assert status_code == 400
    assert utils.load(response) == error_msg

    error_msg = {'message': 'Error Message', 'status_code': 500, 'foo': 'bar'}
    api_exception = helpers.APIException('Error Message', 500, {'foo': 'bar'})

    response, status_code = helpers.jsonify_api_exception(api_exception)
    assert status_code == 500
    assert utils.load(response) == error_msg


def test_raise_or_return(monkeypatch):
    """Test the raise_or_return function without error"""

    mock_schema_load = mock.Mock(return_value=(mock.sentinel.rv, None))
    mock_schema = mock.Mock(load=mock_schema_load)
    mock_flask_request = mock.Mock(json=mock.sentinel.request_json)

    schema_load_calls = [mock.call(mock.sentinel.request_json)]
    monkeypatch.setattr('flask.request', mock_flask_request)
    rv = helpers.raise_or_return(mock_schema)

    assert mock_schema_load.call_args_list == schema_load_calls
    assert rv == mock.sentinel.rv


@pytest.mark.usefixtures('request_context')
def test_raise_or_return_error():
    """Test the raise_or_return function with error"""

    mock_schema_load = mock.Mock(side_effect=AttributeError)
    mock_schema = mock.Mock(load=mock_schema_load)
    api_exc = ('Request malformed', 400, {'errors': 'JSON might be incorrect'})

    with pytest.raises(helpers.APIException) as excinfo:
        helpers.raise_or_return(mock_schema)

    assert excinfo.value.args == api_exc

    mock_schema_load = mock.Mock(return_value=(None, mock.sentinel.errors))
    mock_schema = mock.Mock(load=mock_schema_load)
    api_exc = ('Request malformed', 400, {'errors': mock.sentinel.errors})

    with pytest.raises(helpers.APIException) as excinfo:
        helpers.raise_or_return(mock_schema)

    assert excinfo.value.args == api_exc


def test_model_entity(monkeypatch):
    """Test the model_entity helper"""

    mock_model_as_entity = mock.Mock(return_value=mock.sentinel.entity)
    mock_model = mock.Mock(_as_entity=mock_model_as_entity)

    mock_query_compiler = mock.Mock()

    # pylint: disable=protected-access
    mock_parse_entity = mock_query_compiler.return_value._parse_entity
    mock_parse_entity.return_value = (mock.sentinel.model_entity, None)

    monkeypatch.setattr('peewee.QueryCompiler', mock_query_compiler)

    me = helpers.model_entity(mock_model)

    parse_entity_calls = [mock.call(mock.sentinel.entity, None, None)]

    assert mock_query_compiler.call_args_list == [mock.call()]
    assert mock_model_as_entity.call_args_list == [mock.call()]
    assert mock_parse_entity.call_args_list == parse_entity_calls
    assert me == mock.sentinel.model_entity


def test_unpack():
    """Test the unpack function

    Here are the return value possibilities:

    data               : must return data, 200, {}
    data, code         : must return data, code, {}
    data, code, headers: must return data, code, headers

    """
    rv = helpers.unpack(mock.sentinel.data)
    assert rv == (mock.sentinel.data, 200, {})

    rv = helpers.unpack((mock.sentinel.data,))
    assert rv == ((mock.sentinel.data,), 200, {})

    rv = helpers.unpack((mock.sentinel.data, mock.sentinel.code))
    assert rv == (mock.sentinel.data, mock.sentinel.code, {})

    rv = helpers.unpack(
        (mock.sentinel.data, mock.sentinel.code, mock.sentinel.headers)
    )
    assert rv == (mock.sentinel.data, mock.sentinel.code,
                  mock.sentinel.headers)


def test_template(monkeypatch):
    """Test the template decorator

    attach a template to the request if mimetype match mapping
    """
    mapping = {'html/text': mock.sentinel.tpl}
    mock_mapping = mock.MagicMock(wraps=mapping)

    mock_req = mock.Mock(accept_mimetypes=mock.Mock(best='html/text'))

    monkeypatch.setattr('flask.request', mock_req)

    decorator = helpers.template(mock_mapping)

    func = decorator(lambda: mock.sentinel.rv)
    rv = func()

    assert rv == mock.sentinel.rv
    assert flask.request.tpl == mock.sentinel.tpl
    assert mock_mapping.get.call_args_list == [mock.call('html/text')]

