#!/usr/bin/env python

import os
import sys
import argparse
import subprocess
import errno

PROJECT = 'RulzUrAPI'
PYTHON_REQUIRED_VERSION = 3.4
VENV_NAME = '.venv'


TOP_DIR = os.path.dirname(os.path.realpath(__file__))
PYTHON_EXEC = sys.executable
PYTHON_VERSION = float('%s.%s' % tuple(sys.version_info[0:2]))

parser = argparse.ArgumentParser(
    description='Management of development environment for %s.' % PROJECT,
)


def check_python():
    if not os.path.exists(TOP_DIR + os.sep + VENV_NAME):
        parser.error('\x1b[0;31m'
                     'virtualenv is not installed, please install it with:\n'
                     '  ./manage.py  install venv'
                     '\x1b[0m')
    if not PYTHON_EXEC.strip(TOP_DIR).startswith('.venv'):
        parser.error('\x1b[0;31m'
                     'Python is not running from the virtualenv, to activate '
                     'the virtualenv just run:\n'
                     '  source .venv/bin/activate'
                     '\x1b[0m')
    if PYTHON_VERSION < PYTHON_REQUIRED_VERSION:
        parser.error('\x1b[0;31m'
                     'Your version of Python is too old please upgrade your '
                     'virtualenv with: ./manage.py install venv'
                     '\x1b[0m')


def install_venv():
    try:
        subprocess.call([
            'pyvenv-' + str(PYTHON_REQUIRED_VERSION), '.venv'
        ])
    except subprocess.CalledProcessError:
        parser.error('\x1b[0;31m'
                     'The needed version of pyvenv was not found on your '
                     'system, to run this script python ' +
                     str(PYTHON_REQUIRED_VERSION) +
                     ' is needed'
                     '\x1b[0m')


def install_requirements(f):
    pip = os.sep.join([
        TOP_DIR, VENV_NAME, 'bin', 'pip' + str(PYTHON_REQUIRED_VERSION)
    ])

    try:
        subprocess.call([
            pip, 'install', '-qv', '-r', f
        ])
    except OSError as err:
        if err.errno == errno.ENOENT:
            parser.error('\x1b[0;31m'
                         'The virtualenv is not installed or out of date, '
                         'please rerun this command with -v'
                         '\x1b[0m')


def install(options):
    if options['all'] or not any(options.values()):
        install_venv()
        options['venv'] = False
        install_requirements('requirements.txt')
        options['requirements'] = False
        install_requirements('requirements-tests.txt')
        options['tests'] = False

    if options['venv']:
        install_venv()
    if options['requirements']:
        install_requirements('requirements.txt')
    if options['tests']:
        install_requirements('requirements-tests.txt')

    if options['venv'] or options['all']:
        parser.exit(0, '\x1b[0;32m'
                       'A virtualenv has been installed in your environment '
                       'please activate it by running:\n'
                       '  source .venv/bin/activate\n'
                       '\x1b[0m')

if __name__ == '__main__':
    subparsers = parser.add_subparsers()

    # subparsers
    parser_install = subparsers.add_parser(
        'install',  help='Install the development environment of the project',
    )
    parser_install.set_defaults(func=install)

    # parser_install arguments
    parser_install.add_argument(
        '-v', '--venv',
        help='Install the python virtual environment of %s' % PROJECT,
        action='store_true'
    )

    parser_install.add_argument(
        '-r', '--requirements',
        help='Install the requirements of %s for development' % PROJECT,
        action='store_true'
    )

    parser_install.add_argument(
        '-t', '--tests',
        help='Install the requirements of %s for tests' % PROJECT,
        action='store_true'
    )

    parser_install.add_argument(
        '-a', '--all',
        help='Install all the development environment of %s' % PROJECT,
        action='store_true'
    )

    args = parser.parse_args()
    args.func(vars(args))
