#!/usr/bin/env python

import os
import sys

PROJECT = 'RulzUrAPI'
PYTHON_REQUIRED_VERSION = 3.4
VENV_NAME = '.venv'


TOP_DIR = os.path.dirname(os.path.realpath(__file__))
PYTHON_EXEC = sys.executable
PYTHON_VERSION = float('%s.%s' % tuple(sys.version_info[0:2]))


def check_python():
    if not os.path.exists(TOP_DIR + os.sep + VENV_NAME):
        print('virtualenv is not installed, please install it with: ./manage.py'
              ' install venv')
        exit(1)
    if not PYTHON_EXEC.strip(TOP_DIR).startswith('.venv'):
        print('Python is not running from the virtualenv, to activate the'
              'virtualenv just run: source .venv/bin/activate')
        exit(1)
    if PYTHON_VERSION < PYTHON_REQUIRED_VERSION:
        print('Your version of Python is too old please upgrade your virtualenv'
              'with: ./manage.py install venv')
        exit(1)


if __name__ == '__main__':
    check_python()
