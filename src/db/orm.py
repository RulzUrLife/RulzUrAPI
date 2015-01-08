"""Enum related codebase

cloned and (not) adapted from
https://gist.github.com/b1naryth1ef/607e92dc8c1748a06b5d
"""
import peewee

# pylint: disable=too-few-public-methods, protected-access
class UpdateQuery(peewee.UpdateQuery):
    """Overrides peewee.UpdateQuery to add a returning feature"""

    def __init__(self, model_class, update=None, returning=False):
        super(UpdateQuery, self).__init__(model_class, update)

        def naive(self, naive=True):
            """Add a naive wrapper"""
            self._naive = naive

        def tuples(self, tuples=True):
            """Add a tuples wrapper"""
            self._tuples = tuples

        def dicts(self, dicts=True):
            """Add a dicts wrapper"""
            self._dicts = dicts

        self._returning = returning
        self._tuples = self._dicts = self._naive = False

        if self._returning:
            setattr(UpdateQuery, 'naive', peewee.returns_clone(naive))
            setattr(UpdateQuery, 'tuples', peewee.returns_clone(tuples))
            setattr(UpdateQuery, 'dicts', peewee.returns_clone(dicts))


    def _clone_attributes(self, query):
        query = super(UpdateQuery, self)._clone_attributes(query)
        query._returning = self._returning
        return query

    def execute(self):
        if not self._returning:
            return self.database.rows_affected(self._execute())

        if self._tuples:
            ResultWrapper = peewee.TuplesQueryResultWrapper
        elif self._dicts:
            ResultWrapper = peewee.DictQueryResultWrapper
        elif self._naive:
            ResultWrapper = peewee.NaiveQueryResultWrapper
        else:
            ResultWrapper = peewee.ModelQueryResultWrapper

        return ResultWrapper(self.model_class, self._execute(), None)

# pylint: disable=protected-access
class QueryCompiler(peewee.QueryCompiler):
    """Overrides peewee.QueryCompiler to add custom behavior"""

    def generate_update(self, query):
        """Generate a returning update statement"""

        sql, params = super(QueryCompiler, self).generate_update(query)
        if query._returning:
            sql = "%s RETURNING *" % sql
        return sql, params

