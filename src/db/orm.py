"""

"""
import collections
import operator
import re

import peewee
import playhouse

import utils.helpers

class EnumField(peewee.Field):
    """Enum field

    define an enum field in your model like this:
    EnumField(choices=['a', 'b', 'c'])
    """
    db_field = 'enum'

    def pre_field_create(self, model):
        field = 'e_%s' % self.name

        self.get_database().get_conn().cursor().execute(
            'DROP TYPE IF EXISTS %s;' % field
        )

        query = self.get_database().get_conn().cursor()
        tail = ', '.join(["'%s'"] * len(self.choices)) % tuple(self.choices)
        q = 'CREATE TYPE %s AS ENUM (%s);' % (field, tail)
        query.execute(q)

    def post_field_create(self, model):
        self.db_field = 'e_%s' % self.name

    def __ddl_column__(self, name):
        return peewee.SQL('e_%s' % self.name)

    def db_value(self, value):
        if value not in self.choices:
            raise ValueError('Invalid Enum Value "%s"' % value)
        return str(value)


class DirectionField(peewee.Field):
    db_field = 'direction'

    def db_value(self, value):
        return '("%s", "%s")' % (value[0], value[1])

    def python_value(self, value):
        title, text = value.strip('()').split(',')

        title = title.strip('"')
        text = text.strip('"')[1:]
        return utils.helpers.Direction(title, text)


class ArrayField(playhouse.postgres_ext.ArrayField):
    parser = re.compile("\(.*?\)")
    default_index_type = None

    def db_value(self, value):
        def stringify(elt):
            if utils.helpers.is_iterable(elt):
                return '"(%s)"' % ', '.join(elt)
            else:
                return str(elt)

        return '{%s}' % ', '.join(
            stringify(elt) for elt in super(ArrayField, self).db_value(value)
        )

    def python_value(self, value):
        if isinstance(value, str):
            values = [value.replace('\\"', '"')
                      for value in self.parser.findall(value)]
        else:
            values = value

        return [self.__field.python_value(value) for value in values]
