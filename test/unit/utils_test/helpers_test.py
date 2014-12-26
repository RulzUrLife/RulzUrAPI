"""Helpers unit testing"""
import utils.helpers
import mock
import db.models
import re

# pylint: disable=too-few-public-methods
class RegexComparer(object):
    """Provide a comparer for regex"""

    def __init__(self, pattern):
        self.pattern = re.compile(pattern)

    def __eq__(self, other):
        return self.pattern.match(other)

def test_optimized_update(monkeypatch):
    """Test if optimized_update generates the correct request"""
    update = {'name': 'test_name'}


    utensil_raw_mock = mock.Mock()
    utensil_raw_mock.return_value.dicts.return_value = (
        mock.sentinel.return_value
    )
    monkeypatch.setattr('db.models.Utensil.raw', utensil_raw_mock)
    return_value = utils.helpers.optimized_update(db.models.Utensil, update, 1)

    # pylint: disable=anomalous-backslash-in-string
    pattern = ' '.join([
        'UPDATE .*? SET \"name\" = \%s',
        'WHERE \(\"utensil\"\.\"id\" = \%s\) RETURNING \*'
    ])
    utensil_raw_mock.assert_called_once_with(
        RegexComparer(pattern), update['name'], 1
    )
    assert return_value is mock.sentinel.return_value

def test_optimized_update_without_id(monkeypatch):
    """Test if optimized_update generates the correct request

    If not id provided
    """
    update = {'id': 1, 'name': 'test_name'}
    utensil_raw_mock = mock.Mock()

    monkeypatch.setattr('db.models.Utensil.raw', utensil_raw_mock)
    utils.helpers.optimized_update(db.models.Utensil, update)

    # pylint: disable=anomalous-backslash-in-string
    pattern = ' '.join([
        'UPDATE .*? SET \"id\" = \%s, \"name\" = \%s',
        'WHERE \(\"utensil\"\.\"id\" = \%s\) RETURNING \*'
    ])

    utensil_raw_mock.assert_called_once_with(
        RegexComparer(pattern), update['id'], update['name'], update['id']
    )

