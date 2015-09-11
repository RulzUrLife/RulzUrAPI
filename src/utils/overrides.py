"""Override Flask to add some helpers to fit our workflow
"""

import flask
import utils.helpers

# pylint: disable=too-few-public-methods
class Flask(flask.Flask):
    """RulzUrKitchen specific Flask app"""

    def make_response(self, rv):
        data, code, headers = utils.helpers.unpack(rv)
        tpl = getattr(flask.request, 'tpl', None)
        if tpl is not None:
            rv = flask.render_template(tpl, **data), code, headers
        elif isinstance(data, dict):
            rv = flask.jsonify(data), code, headers

        return super(Flask, self).make_response(rv)



class Blueprint(flask.Blueprint):
    """RulzUrKitchen specific blueprint"""

    def templates_mapping(self, mapping):
        """Template decorator

        This decorator is used to attach a templates mapping to the request.
        The template will then be evaluated according to headers
        """
        def decorator(func):
            """Take the function to decorate and return a wrapper"""

            def wrapper(*args):
                """Wrap the function call, attach the template if needed"""
                flask.request.tpl = mapping.get(flask.request.accept_mimetypes.best)
                return func(*args)

            return wrapper

        return decorator

