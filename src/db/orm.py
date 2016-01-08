"""Enum related codebase

cloned and (not) adapted from
https://gist.github.com/b1naryth1ef/607e92dc8c1748a06b5d
"""
import operator
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

    def __ddl_column__(self, toto):
        import ipdb; ipdb.set_trace()
        return peewee.SQL("e_%s" % self.name)


# pylint: disable=abstract-method
class InsertQuery(peewee.InsertQuery):
    """Overrides peewee.InsertQuery to add a unique feature"""

    def __init__(self, model_class, unique=None, **kwargs):
        self._unique = unique
        super(InsertQuery, self).__init__(model_class, **kwargs)

    def sql(self):
        if self._unique:
            return self.compiler().generate_unique_insert(self)
        else:
            return self.compiler().generate_insert(self)

    def execute(self):
        if self._rows and len(self._rows):
            return self.database.rows_affected(self._execute())

# pylint: disable=protected-access, too-few-public-methods
class QueryCompiler(peewee.QueryCompiler):
    """Overrides peewee.QueryCompiler to add custom behavior"""

    def generate_unique_insert(self, query):
        """Generate an insert SQL statement which check an unique field"""

        model = query.model_class
        unique_entity = query._unique
        alias_map = self.alias_map_class()
        alias_map.add(model, model._meta.db_table)
        clauses = [peewee.SQL('INSERT INTO'), model._as_entity()]

        fields, value_clauses = [], []
        have_fields = False

        for row_dict in query._iter_rows():
            if not have_fields:
                fields = sorted(
                    row_dict.keys(), key=operator.attrgetter('_sort_key'))
                have_fields = True

            values = []
            for field in fields:
                value = row_dict[field]
                if not isinstance(value, (peewee.Node, peewee.Model)):
                    value = peewee.Param(value, conv=field.db_value)
                values.append(value)

            value_clauses.append(peewee.EnclosedClause(*values))

        clauses.extend([
            self._get_field_clause(fields),
            peewee.SQL('SELECT * FROM'),
            peewee.EnclosedClause(
                peewee.Clause(
                    peewee.SQL('VALUES'), peewee.CommaClause(*value_clauses)
                )
            ),
            peewee.SQL('AS var'),
            self._get_field_clause(fields),
            peewee.SQL('WHERE var.%s NOT IN' % unique_entity.name),
            peewee.EnclosedClause(
                peewee.Clause(
                    peewee.SQL('SELECT %s FROM' % unique_entity.name),
                    model._as_entity()
                )
            )
        ])

        return self.build_query(clauses, alias_map)

