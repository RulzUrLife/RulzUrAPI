"""Connection to database

Handle the config constants
Load the password from a file if possible
Set the database variable for deferred connection
Set the schema for database models
"""
import peewee
import db.orm

try:
    with open('password') as f:
        password = f.readline()

except Exception: # pylint: disable=broad-except
    password = 'password'

# Connect to the database URL defined in the environment with docker
config = {
    'database': 'rulzurdb',
    'user': 'rulzurdb',
    'host': 'rulzurdb',
    'port': 5432,
    'password': password.rstrip('\n'),
}

schema = 'rulzurkitchen'

database = peewee.PostgresqlDatabase(None)
database.compiler_class = db.orm.QueryCompiler

