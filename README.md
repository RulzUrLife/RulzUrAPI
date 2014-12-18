RulzUrAPI
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
* `docker run -v $(pwd):/opt/rulzurapi -it rulzurapi --banner`:
open an ipython shell into the container if you need to have the application
reachable in the browser add the following option `-p 5000:5000` before `-it`
* `docker run -v $(pwd):/opt/rulzurapi -it rulzurapi -c '!py.test'`:
run the tests for the application

