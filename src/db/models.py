import peewee
import playhouse.postgres_ext

import db.connector
import db.enum


class BaseModel(peewee.Model):
    @classmethod
    def create_table(cls, *args, **kwargs):
        for field in cls._meta.get_fields():
            if hasattr(field, "pre_field_create"):
                field.pre_field_create(cls)

        cls._meta.database.create_table(cls)

        for field in cls._meta.get_fields():
            if hasattr(field, "post_field_create"):
                field.post_field_create(cls)

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
    duration = db.enum.EnumField(choices=[
        '0/5', '5/10', '10/15', '15/20', '20/25', '25/30', '30/45', '45/60',
        '60/75', '75/90', '90/120', '120/150'])
    people = peewee.IntegerField()
    type = db.enum.EnumField(choices=['starter', 'main', 'dessert'])


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
    measurement = db.enum.EnumField(choices=['L', 'g', 'oz', 'spoon'])

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

