import peewee
import playhouse.postgres_ext

import db.connector


class BaseModel(peewee.Model):

    class Meta:
        database = db.connector.database
        schema = db.connector.schema


class Ingredient(BaseModel):
    id = peewee.PrimaryKeyField()
    name = peewee.CharField()


class Utensil(BaseModel):
    id = peewee.PrimaryKeyField()
    name = peewee.CharField()


class Recipe(BaseModel):
    id = peewee.PrimaryKeyField()
    name = peewee.CharField()
    directions = playhouse.postgres_ext.JSONField()
    difficulty = peewee.IntegerField()
    duration = peewee.CharField()
    people = peewee.IntegerField()
    type = peewee.CharField()


class RecipeIngredients(BaseModel):
    recipe = peewee.ForeignKeyField(
            Recipe,
            related_name='ingredients',
            db_column='fk_recipe')
    ingredient = peewee.ForeignKeyField(
            Ingredient,
            related_name='recipes',
            db_column='fk_ingredient')
    quantity = peewee.IntegerField()
    measurement = peewee.CharField()

    class Meta:
        primary_key = peewee.CompositeKey('recipe', 'ingredient')
        db_table = 'recipe_ingredients'


class RecipeUtensils(BaseModel):
    recipe = peewee.ForeignKeyField(
            Recipe,
            related_name='utensils',
            db_column='fk_recipe'
            )
    utensil = peewee.ForeignKeyField(
            Utensil,
            related_name='recipes',
            db_column='fk_utensil')

    class Meta:
        primary_key = peewee.CompositeKey('recipe', 'utensil')
        db_table = 'recipe_utensils'

