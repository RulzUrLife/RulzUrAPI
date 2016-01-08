"""Database module, contains all the database related codebase
"""
import playhouse.postgres_ext
import db.orm

database = playhouse.postgres_ext.PostgresqlExtDatabase(None, register_hstore=False)
database.compiler_class = db.orm.QueryCompiler

schema = 'rulzurkitchen'
