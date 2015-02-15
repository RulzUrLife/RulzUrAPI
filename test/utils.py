"""Utilities for testing"""

import json
import unittest.mock as mock

#pylint: disable=too-few-public-methods
class FakeModel(object):
    """FakeModel mocks BaseModel

    It only mocks the to_dict method to ease testing
    """
    def __init__(self, data):
        self.data = data
        for key, value in data.items():
            setattr(self, key, value)

    def to_dict(self):
        """Clone the to_dict function from db.models.BaseModel"""
        return self.data


def expression_assert(fn, expression, pos=0):
    """Compare the first argument with the expression __dict__"""
    (expression_arg,), _ = fn.call_args_list[pos]
    return expression_arg.__dict__ == expression.__dict__


def load(page):
    """Decode a page and load the nested json"""
    return json.loads(page.data.decode('utf-8'))


def update_mocking(rv):
    """Create a mock object for an update query and return it"""
    mock_returning_update = mock.Mock()

    mocking = (mock_returning_update.return_value
               .where.return_value
               .returning.return_value
               .dicts.return_value
               .execute)
    if hasattr(rv, '__call__') or hasattr(rv, '__next__'):
        mocking.side_effect = rv
    else:
        mocking.return_value = rv

    return mock_returning_update

