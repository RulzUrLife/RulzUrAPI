#!/bin/bash

PROJECT="RulzUrAPI"
TOP_DIR=$(cd $(dirname "$0") && pwd)

docker_create () {
  docker build -t="flask" -rm=true .
}

docker_run () {
  docker run -d -p 5000 flask
}

repository_initialization () {
  sudo apt-get install -y python-pip
  sudo pip install virtualenv
  sudo pip install virtualenvwrapper
  source "/usr/local/bin/virtualenvwrapper.sh"
	mkvirtualenv "$PROJECT"
	pip install -r "requirements.txt"
}

main () {
  repository_initialization
}

main
