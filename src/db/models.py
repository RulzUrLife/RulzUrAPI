"""Database models

Models from the database adapted to python through peewee ORM

Due to non compliance with pylint we have a lot of exception in this file
"""
import peewee
import playhouse.postgres_ext

import db.connector
import db.enum

#pylint: disable=too-few-public-methods, no-init, old-style-class
class BaseModel(peewee.Model):
    """Define the common model configuration"""

    def to_dict(self):
        """Return the private attribute _data"""
        return self._data

    class Meta:
        """Define the common database configuration for the models

        All the configuration is loaded from db.connector,
        this is just a linking to have this in a dedicated file and share it to
        the models
        """
        database = db.connector.database
        schema = db.connector.schema

#pylint: disable=too-few-public-methods
class Ingredient(BaseModel):
    """database's ingredient table"""
    id = peewee.PrimaryKeyField()
    name = peewee.CharField()


#pylint: disable=too-few-public-methods
class Utensil(BaseModel):
    """database's utensil table"""
    id = peewee.PrimaryKeyField()
    name = peewee.CharField()


#pylint: disable=too-few-public-methods
class Recipe(BaseModel):
    """database's recipe table"""
    id = peewee.PrimaryKeyField()
    name = peewee.CharField()
    directions = playhouse.postgres_ext.JSONField()
    difficulty = peewee.IntegerField()
    duration = db.enum.EnumField(choices=[
        '0/5', '5/10', '10/15', '15/20', '20/25', '25/30', '30/45', '45/60',
        '60/75', '75/90', '90/120', '120/150'])
    people = peewee.IntegerField()
    type = db.enum.EnumField(choices=['starter', 'main', 'dessert'])

    #Foreign keys linking
    utensils = None
    ingredients = None


#pylint: disable=too-few-public-methods
class RecipeIngredients(BaseModel):
    """database's recipe_ingredients table"""
    recipe = peewee.ForeignKeyField(
        Recipe,
        related_name='ingredients',
        db_column='fk_recipe'
    )
    ingredient = peewee.ForeignKeyField(
        Ingredient,
        related_name='recipes',
        db_column='fk_ingredient'
    )
    quantity = peewee.IntegerField()
    measurement = db.enum.EnumField(choices=['L', 'g', 'oz', 'spoon'])

    #pylint: disable=no-init, old-style-class
    class Meta:
        """ManyToMany relationship for recipe_ingredients

        primary_key need to be specified here

        peewee does not handle the tables creation, so we have to make the name
        linking by hand (db_tables)
        """
        primary_key = peewee.CompositeKey('recipe', 'ingredient')
        db_table = 'recipe_ingredients'


#pylint: disable=too-few-public-methods
class RecipeUtensils(BaseModel):
    """database's recipe_utensils table"""
    recipe = peewee.ForeignKeyField(
        Recipe,
        related_name='utensils',
        db_column='fk_recipe'
    )
    utensil = peewee.ForeignKeyField(
        Utensil,
        related_name='recipes',
        db_column='fk_utensil'
    )

    #pylint: disable=no-init, old-style-class
    class Meta:
        """ManyToMany relationship for recipe_utensils

        primary_key need to be specified here

        peewee does not handle the tables creation, so we have to make the name
        linking by hand (db_tables)
        """
        primary_key = peewee.CompositeKey('recipe', 'utensil')
        db_table = 'recipe_utensils'

