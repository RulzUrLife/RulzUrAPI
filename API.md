API methods
===========
API made according to: [apigee](https://pages.apigee.com/rs/apigee/images/api-design-ebook-2012-03.pdf)
## Recipes

* `recipes/`: List all the recipes
* `recipes/:id`: Get informations for a given recipe
* `recipes/:id/ingredients`: Get the ingredients for a given recipe
* `recipes/:id/utensils`: Get the utensils for a given recipe

## Utensils

* `utensils/`:
    * `GET` : List all utensils
    * `POST`: Create a new utensil

        | Parameter |  Type  | Description                    |
        | ----------|:------:| ------------------------------ |
        | name      | string | (optional) name of the utensil |

    * `PUT`: Update multiple utensils at a time

        | Parameter |  Type   | Description                                     |
        | ----------|:-------:| ----------------------------------------------- |
        | utensils  | list    | list of utensils (see utensils/:id for details) |

* `utensils/:id`:
    * `GET` : Get informations for a given utensil
    * `POST`: Not allowed
    * `PUT` : Update multiple utensils at a time

        | Parameter |  Type   | Description                    |
        | ----------|:-------:| ------------------------------ |
        | name      | string  | (optional) name of the utensil |

* `utensils/:id/recipes`: Get the recipes for a given utensil

## Ingredients

* `ingredients/`: List all ingredients
* `ingredients/:id`: Get informations for a given ingredient
* `ingredients/:id/recipes`: Get the recipes for a given utensil

