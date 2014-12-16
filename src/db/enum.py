"""Enum related codebase

cloned and (not) adapted from
https://gist.github.com/b1naryth1ef/607e92dc8c1748a06b5d
"""
import peewee

class EnumField(peewee.Field):
    """Enum field

    define an enum field in your model like this:
    EnumField(choices=["a", "b", "c"])
    """
    db_field = "enum"

    def coerce(self, value):
        if value not in self.choices:
            raise Exception("Invalid Enum Value `%s`", value)
        return str(value)

    def get_column_type(self):
        return "enum"

    def __ddl_column__(self, _):
        return peewee.SQL("e_%s" % self.name)

