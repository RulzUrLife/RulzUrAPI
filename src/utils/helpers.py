"""Helpers for rulzurapi"""
import flask

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
        return rv

def parse_args(loader_fn, json, message=None):
    """Helpers for parsing args

    Raise an APIException if parsing errors are detected
    """
    if message is None:
        message = 'Request malformed'

    data, errors = loader_fn.load(json)
    if len(errors):
        raise APIException(message, payload={'errors': errors})

    return data


def jsonify_api_exception(api_exception):
    """Return an http response wrapping an APIException"""
    response = flask.jsonify(api_exception.to_dict())
    response.status_code = api_exception.status_code
    return response

