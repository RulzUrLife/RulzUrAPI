"""Helpers for rulzurapi"""
import collections
import itertools
import functools

import flask
import utils.exceptions as exc


Direction = collections.namedtuple('Direction', ['title', 'text'])

class JSONEncoder(flask.json.JSONEncoder):
    pass

def is_iterable(obj):
    return hasattr(obj, '__iter__') and not isinstance(obj, str)

def raise_or_return(schema, many=False):
    """Load the data in a dict, if errors are returned, an error is raised"""
    data = flask.request.get_json()
    if is_iterable(data):
        data, errors = schema.load(data, many)
    else:
        errors = 'JSON is incorrect'

    if errors:
        raise exc.APIException('request malformed', 400, {'errors': errors})

    return data

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

def dict_merge(*dict_list):
    '''recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and b have a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary.
    '''
    result = collections.defaultdict(dict)
    dicts_items = itertools.chain(*[d.items() for d in dict_list])

    for key, value in dicts_items:
        src = result[key]
        if isinstance(src, dict) and isinstance(value, dict):
            result[key] = dict_merge(src, value)
        elif isinstance(src, dict) or isinstance(src, str):
            result[key] = value
        elif is_iterable(src) and is_iterable(value):
            result[key] += value
        else:
            result[key] = value

    return dict(result)

