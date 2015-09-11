"""Helpers for rulzurapi"""
import functools

import flask
import peewee

class APIException(Exception):
    """Exception for the API, customize error output"""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super(APIException, self).__init__(
            message, status_code or self.status_code, payload
        )

def jsonify_api_exception(api_exception):
    """Return an http response wrapping an APIException"""
    message, status_code, payload = api_exception.args

    response_dict = {'message': message, 'status_code': status_code}
    response_dict.update(dict(payload or ()))
    return flask.jsonify(response_dict), status_code

def raise_or_return(schema):
    """Load the data in a dict, if errors are returned, an error is raised"""
    try:
        data, errors = schema.load(flask.request.json)
    except AttributeError:
        raise APIException('Request malformed', 400,
                           {'errors': 'JSON might be incorrect'})
    if errors:
        raise APIException('Request malformed', 400, {'errors': errors})

    return data

# pylint: disable=protected-access
def model_entity(model):
    """Retrieve the entity of a specific model

    ie: "schema"."table"
    """
    query_compiler = peewee.QueryCompiler()
    me, _ = query_compiler._parse_entity(
        model._as_entity(), None, None
    )
    return me

def unpack(value):
    """Return a three tuple of data, code, and headers"""
    if not isinstance(value, tuple):
        return value, 200, {}
    try:
        data, code, headers = value
        return data, code, headers
    except ValueError:
        pass

    try:
        data, code = value
        return data, code, {}
    except ValueError:
        pass

    return value, 200, {}

def template(mapping):
    """Template decorator

    This decorator is used to attach a templates mapping to the request.
    The template will then be evaluated according to headers
    """
    def decorator(func):
        """Take the function to decorate and return a wrapper"""

        @functools.wraps(func)
        def wrapper(*args):
            """Wrap the function call, attach the template if needed"""
            mimetype = flask.request.accept_mimetypes.best
            flask.request.tpl = mapping.get(mimetype)
            return func(*args)

        return wrapper

    return decorator
