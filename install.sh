#!/bin/bash

PROJECT="RulzUrAPI"
TOP_DIR=$(cd $(dirname "$0") && pwd)

docker_create () {
  docker build -t="$PROJECT" -rm=true .
}

docker_run () {
  docker run -d -p 80 "$PROJECT"
}

docker_clean () {
  docker stop $(docker ps -a -q)
  docker rm $(docker ps -a -q)
}

repository_initialization () {
  cd "$TOP_DIR"
  sudo apt-get install -y python-pip
  sudo pip install virtualenv
  sudo pip install virtualenvwrapper
  source "/usr/local/bin/virtualenvwrapper.sh"
	mkvirtualenv "$PROJECT"
	pip install -r "requirements.txt"
}

main () {
  [[ -z "$1" ]] && repository_initialization && return

  case "$1" in
  "init")
    repository_initialization
    ;;
  "docker_create")
    docker_create
    ;;
  "docker_run")
    docker_run
    ;;
  "docker_clean")
    docker_clean
    ;;
  esac
}

main "$@"
