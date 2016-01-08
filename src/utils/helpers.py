"""Helpers for rulzurapi"""
import functools

import flask
import werkzeug.exceptions as werkzeug_exc
import marshmallow.exceptions as marshmallow_exc
import utils.exceptions as api_exc
import peewee



def raise_or_return(schema, many=False):
    """Load the data in a dict, if errors are returned, an error is raised"""
    try:
        data, errors = schema.load(flask.request.get_json(), many)
    except (werkzeug_exc.BadRequest, marshmallow_exc.ValidationError):
        raise api_exc.APIException(
            'request malformed', 400, {'errors': 'JSON might be incorrect'}
        )
    if errors:
        raise api_exc.APIException('request malformed', 400, {'errors': errors})

    return data

# pylint: disable=protected-access
def model_entity(model):
    """Retrieve the entity of a specific model

    ie: "schema"."table"
    """
    query_compiler = peewee.QueryCompiler()
    me, _ = query_compiler._parse_entity(model._as_entity(), None, None)
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
        def wrapper(*args, **kwargs):
            """Wrap the function call, attach the template if needed"""
            mimetype = flask.request.accept_mimetypes.best
            flask.request.tpl = mapping.get(mimetype)
            return func(*args, **kwargs)

        return wrapper

    return decorator
