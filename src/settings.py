"""Configuration file
"""

DEBUG = False

DATABASE = {
    'database': 'rulzurdb',
    'user': 'rulzurdb',
    'host': 'localhost',
    'port': 5432,
    'password': 'some_password',
}

# Logging related parameters
PROD_LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
DEBUG_LOG_FORMAT = (
    '-' * 80 + '\n' +
    '%(levelname)s at %(asctime)s in %(name)s:\n' +
    '%(message)s\n' +
    '-' * 80
)

LOG_FILE = '/dev/null'
