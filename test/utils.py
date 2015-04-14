"""Utilities for testing"""

import json
import unittest.mock as mock

import peewee

# pylint: disable=too-few-public-methods
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

def _extract_call_dict(name, args, kwargs=None):
    """utility function which extract the __dict__ attribute for comparison"""
    if kwargs is None:
        args, kwargs = name, args

    has_eq_overriden = lambda obj: (isinstance(obj, peewee.Model) or
                                    isinstance(obj, peewee.Expression))
    get_dict = lambda obj: obj.__dict__ if has_eq_overriden(obj) else obj

    args = [get_dict(arg) for arg in args]
    kwargs = {key: get_dict(value) for key, value in kwargs.items()}

    return mock.call(args, kwargs)

# pylint: disable=protected-access
class _Call(mock._Call):
    """Override mock.call in order to compare Expressions from peewee"""

    def __eq__(self, other):
        self_replacement = _extract_call_dict(*self)

        if isinstance(other, mock._Call):
            other = _extract_call_dict(*other)

        return super(_Call, self_replacement).__eq__(other)


class MagicMock(mock.MagicMock):
    """Override mock.MagicMock to support magic methods"""
    def __init__(self, *args, **kwargs):
        super(MagicMock, self).__init__(*args, **kwargs)
        wraps = kwargs.get('wraps')
        if wraps is None:
            return

        if isinstance(wraps, dict):
            self.__getitem__.side_effect = wraps.__getitem__


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


class MockEncoder(json.JSONEncoder):
    """Custom encoder which can dump Mock objects"""

    # pylint: disable=method-hidden
    def default(self, obj):
        if isinstance(obj, mock.Mock) and obj._mock_wraps:
            return obj._mock_wraps
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

def send(method, url, data=None):
    """Helper to send data from test to the application"""
    kwargs = {
        'content_type': 'application/json',
        'data': json.dumps(data, cls=MockEncoder) if data is not None else None
    }
    return method(url, **kwargs)

