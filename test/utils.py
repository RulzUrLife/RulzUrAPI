"""Utilities for testing"""

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


def expression_assert(fn, expression):
    """Compare the first argument with the expression __dict__"""
    (expression_arg,), _ = fn.call_args
    return expression_arg.__dict__ == expression.__dict__
