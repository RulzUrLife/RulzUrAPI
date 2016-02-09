"""Helpers for rulzurapi"""
import functools

import flask
import marshmallow.exceptions as marshmallow_exc
import utils.exceptions as api_exc
import peewee


class JSONEncoder(flask.json.JSONEncoder):

    def default(self, obj):
        return super(JSONEncoder, self).default(obj)

def raise_or_return(schema, many=False):
    """Load the data in a dict, if errors are returned, an error is raised"""
    data, errors = schema.load(flask.request.get_json(), many)
    if errors:
        raise api_exc.APIException('request malformed', 400, {'errors': errors})

    return data

def model_entity(model):
    """Retrieve the entity of a specific model

    ie: "schema"."table"
    """
    query_compiler = peewee.QueryCompiler()
    me, _ = query_compiler._parse_entity(model.as_entity(), None, None)
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


