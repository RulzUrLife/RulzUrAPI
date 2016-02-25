import functools

import peewee

import db


def parse_entity(*path):
    entity = peewee.Entity(*path)
    return db.database.compiler()._parse_entity(entity, None, None)[0]

def model_entity(model):
    return parse_entity(model._meta.schema, model._meta.db_table)

def lock(*models):
    """Lock table to avoid race conditions"""

    lock_string = 'LOCK TABLE %s IN SHARE ROW EXCLUSIVE MODE'
    models = ', '.join([model_entity(model) for model in models])

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with db.database.atomic():
                db.database.execute_sql(lock_string % models)
                return func(*args, **kwargs)

        return wrapper

    return decorator
