RulzUrAPI [![Build Status](https://travis-ci.org/RulzUrLife/RulzUrAPI.svg?branch=master)](https://travis-ci.org/RulzUrLife/RulzUrAPI)
=========

The application API, this API will be public and used by the frontend.

[API Specification](./API.md)

# Technologies

 * Flask: a python microframework for web application,
 [official website](http://flask.pocoo.org/).


# Running the application in dev mode

This application use docker as a development environment, so that nothing will
be installed on your system except docker itself. It also allow to develop on
every OS without troubles.

* Install docker on your distro https://docs.docker.com/
* Check if docker is correctly install by running: `docker run hello-world`
* Build the development container: `docker build -t rulzurapi .`
* Run it! `docker run -v $(pwd):/opt/rulzurapi -p 5000:5000
--link rulzurdb:rulzurdb -it rulzurapi`
(this command line can vary if it is not launched through an UNIX shell)

# Command lines

All the interaction with the application (except coding) will be done through
docker, so here is the bunch of commands

* `docker run -v $(pwd):/opt/rulzurapi -p 5000:5000 -it rulzurapi`:
run the container in development mode (autoreload on file changes)
* `docker run -v $(pwd):/opt/rulzurapi -it rulzurapi bash`:
open a bash into the container if you need to have the application
reachable in the browser add the following option `-p 5000:5000` before `-it`

to run tests, run the previous command then inside the container run: `py.test`

and for the lint tool: `source misc/pylint_files; pylint $PYLINT_FILES`

# Working on the REST API

It can be easier to work on the API by using some fixture, you can use the ones
provided in the [misc](./misc) folder.

You can use [jq](http://stedolan.github.io/jq/manual/) in addition,
for requesting on the returned json. Here is a cli exemple of how to use is:

```bash
curl -X POST -H "Content-Type: application/json" -s -d @misc/post_recipe_1.json localhost:5000/recipes/ | jq '.'
```

