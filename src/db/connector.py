import os
import peewee

try:
    with open('password') as f:
        password = f.readline()
except:
    password = 'password'

# Connect to the database URL defined in the environment with docker
config = {
    'database': 'rulzurdb',
    'user': 'rulzurdb',
    'host': os.environ.get('RULZURDB_PORT_5432_TCP_ADDR'),
    'port': os.environ.get('RULZURDB_PORT_5432_TCP_PORT'),
    'password': password.rstrip('\n'),
}

database = peewee.PostgresqlDatabase(None)
