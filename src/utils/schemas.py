"""Schemas for dumping and loading datas of RulzUrAPI"""
import marshmallow

# pylint: disable=too-few-public-methods
class UtensilSchema(marshmallow.Schema):
    """Schema representation of an Utensil"""
    id = marshmallow.fields.Integer()
    name = marshmallow.fields.String()

# pylint: disable=too-few-public-methods
class UtensilListSchema(marshmallow.Schema):
    """Schema representation of a list of Utensils"""
    utensils = marshmallow.fields.List(
        marshmallow.fields.Nested(UtensilSchema()),
    )

def post_utensils_schema():
    """Build a post_utensils request parser"""
    utensil_schema = UtensilSchema(exclude=('id',))
    utensil_schema.fields['name'].required = True

    return utensil_schema

def put_utensils_schema():
    """Build a put_utensils request parser"""
    utensil_list_schema = UtensilListSchema()

    utensils_field = utensil_list_schema.fields['utensils']
    utensil_schema = utensils_field.container.nested

    utensils_field.required = True
    utensil_schema.fields['id'].required = True

    return utensil_list_schema

post_utensils_parser = post_utensils_schema()
put_utensils_parser = put_utensils_schema()
utensil_parser = UtensilSchema()
