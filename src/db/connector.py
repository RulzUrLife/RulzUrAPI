import os

import peewee
from playhouse.db_url import connect

with open('password') as f:
    password = f.readline()

# Connect to the database URL defined in the environment with docker
db = connect(
    'postgresql://rulzurdb:%(password)s@%(host)s:%(port)s/rulzurdb' % {
        'host': os.environ['RULZURDB_PORT_5432_TCP_ADDR'],
        'port': os.environ['RULZURDB_PORT_5432_TCP_PORT'],
        'password': password.rstrip('\n'),
    })
