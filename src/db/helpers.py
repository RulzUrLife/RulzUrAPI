import collections
import functools

import db.models

import utils.helpers

MULTIPLE = 'Multiple entries for the same element.'
CORRESPONDING = 'No corresponding id in database.'

def _multiple_entries_error(errors, elts, msg):
    for elt in elts:
        i, elt = elt['index'], elt['elt']
        errors[i]['id' if 'id' in elt else 'name'].append(msg)


def _get(model, elts):
    dd = lambda default: collections.defaultdict(default)
    dm = lambda *args: utils.helpers.dict_merge(*args)

    ids, names, errors = dd(list), dd(list), dd(lambda: dd(list))

    for i, elt in enumerate(elts):
        key, struct = (elt['id'], ids) if 'id' in elt else (elt['name'], names)
        struct[key].append({'index': i, 'elt': elt})

    id_keys, name_keys = list(ids.keys()), list(names.keys())

    if id_keys and name_keys:
        where_clause = (model.id << id_keys) | (model.name << name_keys)
    elif names:
        where_clause = (model.name << name_keys)
    elif ids:
        where_clause = (model.id << id_keys)

    for obj in model.select().where(where_clause):

        if obj.id in ids and obj.name in names:
            err_msg = {'msg': MULTIPLE, 'id': obj.id, 'name': obj.name}
            for elt in ids.pop(obj.id):
                errors[elt['index']]['id'].append(err_msg)
            for elt in names.pop(obj.name):
                errors[elt['index']]['name'].append(err_msg)

            continue

        elt = ids.pop(obj.id, []) or names.pop(obj.name, [])

        if len(elt) > 1:
            _multiple_entries_error(errors, elt, MULTIPLE)
            continue

        elt = elt.pop()
        elts[elt['index']] = dm(obj._data, elt['elt'])


    for v in ids.values():
        if len(v) > 1:
            _multiple_entries_error(errors, v, MULTIPLE)
        _multiple_entries_error(errors, v, CORRESPONDING)

    for k, v in names.items():
        if len(v) > 1:
            _multiple_entries_error(errors, v, MULTIPLE)
        else:
            names[k] = v[0]

    return names, errors

def _insert(model, elts, names):
    req = (model
           .insert_many([elt['elt'] for elt in names.values()])
           .returning())

    for obj in req.execute():
        elts[names[obj.name]['index']] = obj._data


def get_or_insert(model, elts):
    """Get the elements from a model or create them if they not exist"""
    names, errors = {}, {}

    if elts:
        names, errors = _get(model, elts)

    if names and not errors:
        _insert(model, elts, names)

    return elts, errors


get_or_insert_utensils = functools.partial(get_or_insert, db.models.Utensil)
get_or_insert_ingrs = functools.partial(get_or_insert, db.models.Ingredient)
