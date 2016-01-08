import flask

blueprint = flask.Blueprint(
    'base', __name__, template_folder='templates', static_folder='static'
)

@blueprint.route('/')
def index():
    """Display the index page"""
    return flask.render_template('index.html')
