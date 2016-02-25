import peewee
import pytest

import db.orm

def test_enum(gen_table):
    class TestTable(peewee.Model):
        enum = db.orm.EnumField(choices=['foo', 'bar'])

    test_table = gen_table(TestTable)
    test_table.create(enum='foo')
    res = test_table.select(test_table).execute().next()

    assert res.enum == 'foo'


def test_invalid_enum(gen_table):
    class TestTable(peewee.Model):
        enum = db.orm.EnumField(choices=['foo', 'bar'])

    test_table = gen_table(TestTable)

    with pytest.raises(ValueError) as exc:
        test_table.create(enum='baz')

    assert exc.value.args[0] == 'Invalid Enum Value "baz"'


def test_direction(gen_table):
    class TestTable(peewee.Model):
        direction = db.orm.DirectionField()

    test_table = gen_table(TestTable)
    test_table.create(direction=('title', 'text'))
    res = test_table.select(test_table).execute().next()

    assert res.direction == ('title', 'text')
    assert res.direction.title == 'title'
    assert res.direction.text == 'text'


def test_array_of_directions(gen_table):
    class TestTable(peewee.Model):
        directions = db.orm.ArrayField(db.orm.DirectionField)

    test_table = gen_table(TestTable)

    directions = [('title 1', 'text 1'), ('title 2', 'text 2')]
    test_table.create(directions=directions)
    res = test_table.select(test_table).execute().next()

    assert res.directions[0].title == directions[0][0]
    assert res.directions[0].text == directions[0][1]
    assert res.directions[1].title == directions[1][0]
    assert res.directions[1].text == directions[1][1]


def test_array_of_ints(gen_table):
    class TestTable(peewee.Model):
        integers = db.orm.ArrayField(peewee.IntegerField)


    test_table = gen_table(TestTable)

    test_table.create(integers=[1, 2, 3])
    res = test_table.select(test_table).execute().next()

    assert res.integers == [1, 2, 3]


def test_array_of_chars(gen_table):
    class TestTable(peewee.Model):
        chars = db.orm.ArrayField(peewee.CharField)


    test_table = gen_table(TestTable)

    test_table.create(chars=['foo', 'bar'])
    res = test_table.select(test_table).execute().next()

    assert res.chars == ['foo', 'bar']

