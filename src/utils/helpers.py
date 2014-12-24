"""Helpers for rulzurapi"""
import flask

def optimized_update(model, fields, model_id=None):
    """Optimize the update function

    Postgres have a custom RETURNING keyword on update statement, this function
    add it in an UpdateQuery in order to save requests
    """
    if model_id is None:
        model_id = fields['id']

    query = model.update(**fields).where(
        model.id == model_id
    ).sql()
    #request optimization, perform only one request and return result
    query = (model
             .raw('%s RETURNING *' % query[0], *query[1])
             .dicts())
    return query

class NestedRequest(flask.Request):
    def __init__(self, json=None, req=flask.request):
        super(NestedRequest, self).__init__(req.environ, False, req.shallow)
        self.nested_json = json

    @property
    def json(self):
        return self.nested_json

