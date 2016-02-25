"""Database module, contains all the database related codebase
"""
import playhouse.pool
import db.orm

database = playhouse.pool.PooledPostgresqlExtDatabase(
    None, register_hstore=False
)

schema = 'rulzurkitchen'
