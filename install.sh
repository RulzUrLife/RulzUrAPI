#!/bin/bash

PROJECT="RulzUrAPI"
TOP_DIR=$(cd $(dirname "$0") && pwd)
source "/usr/local/bin/virtualenvwrapper.sh"

repository_initialization () {
	mkvirtualenv "$PROJECT"
	pip install -r "requirements.txt"
	sudo docker build -t="flask" -rm=true .
	sudo docker run -d -p 5000 flask
}

main () {
  repository_initialization
}

main