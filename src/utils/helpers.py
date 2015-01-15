"""Helpers for rulzurapi"""
import flask
import flask_restful
import flask_restful.fields
import db.models

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

# pylint: disable=too-many-ancestors, too-few-public-methods
class NestedRequest(flask.Request):
    """Allow flask_restful.reqparse to inspect nested json"""

    def __init__(self, json=None, req=flask.request):
        super(NestedRequest, self).__init__(req.environ, False, req.shallow)
        self.nested_json = json

    @property
    def json(self):
        return self.nested_json

class ModelItem(flask_restful.fields.Raw):
    """Base formatter class for models

    Extend this class by adding the formatter for each field, the format method
    will automatically marshal the Model with its to_dict method
    """
    fields = {}

    def format(self, value):
        return flask_restful.marshal(value.to_dict(), self.fields)

class IngredientItem(ModelItem):
    """Ingredient formatter"""
    fields = {
        'id': flask_restful.fields.Integer,
        'name': flask_restful.fields.String
    }

class UtensilItem(ModelItem):
    """Utensil formatter"""
    fields = {
        'id': flask_restful.fields.Integer,
        'name': flask_restful.fields.String
    }

ingredient_marshal = {
    'ingredient': IngredientItem,
    'quantity': flask_restful.fields.Integer,
    'measurement': flask_restful.fields.String
}

utensil_marshal = {
    'utensil': UtensilItem
}

recipe_marshal = {
    'name': flask_restful.fields.String,
    'people': flask_restful.fields.Integer,
    'directions': flask_restful.fields.Raw,
    'difficulty': flask_restful.fields.Integer,
    'duration': flask_restful.fields.String,
    'type': flask_restful.fields.String,
    'ingredients': flask_restful.fields.List(
        flask_restful.fields.Nested(ingredient_marshal)
    ),
    'utensils': flask_restful.fields.List(
        flask_restful.fields.Nested(utensil_marshal)
    )
}

reqparse = {
    'recipe': {
        'name': {
            'type': str, 'help': 'no recipe name provided'
        },
        'directions': {
            'type': dict, 'help': 'no recipe directions provided'
        },
        'difficulty': {
            'type': int, 'help': 'no recipe difficulty provided',
            'choices': range(1, 6)
        },
        'duration': {
            'type': str, 'help': 'recipe duration not set properly',
            'choices': db.models.Recipe.duration.choices
        },
        'people': {
            'type': int, 'help': 'recipe people not set properly',
            'choices': range(1, 13)
        },
        'type': {
            'type': str, 'help': 'irecipe type not set properly',
            'choices': db.models.Recipe.type.choices
        },
        'ingredients': {
            'type': list, 'help': 'no recipe ingredients provided'
        },
        'utensils': {
            'type': list, 'help': 'no recipe utensils provided'
        }
    },
    'ingredient': {
        'name': {
            'type': str, 'help': 'name not provided for all ingredients'
        },
        'quantity': {
            'type': int,
            'help': 'quantity not provided for all ingredients'
        },
        'measurement': {
            'type': str,
            'help': 'measurement not provided for all ingredients'
        }
    },
    'utensil': {
        'name': {
            'type': str, 'help': 'name not provided for all utensils'
        }
    }
}
