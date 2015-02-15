"""Helpers for rulzurapi"""
import flask
import peewee

class APIException(Exception):
    """Exception for the API, customize error output"""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super(APIException, self).__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

        self.payload = payload

    def to_dict(self):
        """This method dump the exception into a dict for jsonify"""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = self.status_code
        return rv

def jsonify_api_exception(api_exception):
    """Return an http response wrapping an APIException"""
    response = flask.jsonify(api_exception.to_dict())
    response.status_code = api_exception.status_code
    return response

def raise_or_return(schema, data):
    """Load the data in a dict, if errors are returned, an error is raised"""
    data, errors = schema.load(data)
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


