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

    * `PUT`: Update multiple utensils at a time, the id of the utensil must be 
provided for each utensil updated

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

* `ingredients/`:
    * `GET` : List all ingredients
    * `POST`: Create a new ingredient

        | Parameter |  Type  | Description                       |
        | ----------|:------:| --------------------------------- |
        | name      | string | (optional) name of the ingredient |

    * `PUT`: Update multiple ingredients at a time, the id of the ingredient must be 
provided for each ingredient updated

        | Parameter |  Type   | Description                                              |
        | ----------|:-------:| -------------------------------------------------------- |
        | ingredients  | list    | list of ingredients (see ingredients/:id for details) |

* `ingredients/:id`:
    * `GET` : Get informations for a given ingredient
    * `POST`: Not allowed
    * `PUT` : Update multiple ingredients at a time

        | Parameter |  Type   | Description                       |
        | ----------|:-------:| --------------------------------- |
        | name      | string  | (optional) name of the ingredient |

* `ingredients/:id/recipes`: Get the recipes for a given utensil

