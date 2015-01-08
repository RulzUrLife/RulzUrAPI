"""Helpers for rulzurapi"""
import flask

# pylint: disable=too-many-ancestors, too-few-public-methods
class NestedRequest(flask.Request):
    """Allow flask_restful.reqparse to inspect nested json"""

    def __init__(self, json=None, req=flask.request):
        super(NestedRequest, self).__init__(req.environ, False, req.shallow)
        self.nested_json = json

    @property
    def json(self):
        return self.nested_json

