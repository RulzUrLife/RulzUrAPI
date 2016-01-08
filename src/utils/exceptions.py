

class APIException(Exception):
    """Exception for the API, customize error output"""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        status = status_code or self.status_code
        super(APIException, self).__init__(message, status, payload)


    def to_json(self):
        """Return an http response wrapping an APIException"""
        message, status_code, payload = self.args

        response_dict = {'message': message, 'status_code': status_code}
        response_dict.update(dict(payload or ()))

        return response_dict, status_code


def dump_api_exc(api_exception):
    return api_exception.to_json()
