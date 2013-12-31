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

venv_install () {
  cd "$TOP_DIR"
  [[ -a ".venv" ]] && rm -rf ".venv"
	virtualenv .venv
	.venv/bin/pip install -r "requirements.txt"
	.venv/bin/pip install -r "requirements-tests.txt"
}

repository_initialization () {
  cd "$TOP_DIR"
  sudo apt-get install -y python-pip
  sudo pip install virtualenv
  venv_install
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
  "venv_install")
    venv_install
    ;;
  *)
    echo "Command not found"
    ;;
  esac
}

main "$@"
