RulzUrAPI
=========

The application API, this API will be public and used by the frontend.


# Technologies

 * Flask: a python microframework for web application,
 [official website](http://flask.pocoo.org/).

# Management script
Usage: `./manage.py [task [task options]]` help is available with
`./manage.py -h`.

## install
Usage `./manage.py install [options]`, options can be combined.

* -a: install all
* -t: install tests requirements
* -r: install dev requirements
* -v: install python virtualenv

If no option is specified, the install will perform a `-a` by default.

Help is available with `./manage.py install -h`.
