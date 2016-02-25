RulzUrAPI [![Build Status](https://travis-ci.org/RulzUrLife/RulzUrAPI.svg?branch=master)](https://travis-ci.org/RulzUrLife/RulzUrAPI)
=========

The application API, this API will be public and used by the frontend.

[API Specification](./API.md)

# Technologies

 * Flask: a python microframework for web application,
 [official website](http://flask.pocoo.org/).


# Running tests

`py.test -vvv --tb=line --cov=src/`
`py.test -vvv --tb=line --cov=src/ --cov-report=html`

## Evaluate test running time

`python3 -m cProfile -o profile $(which py.test) test/others/`

```python

import pstats
p = pstats.Stats('profile')
p.strip_dirs()
p.sort_stats('cumtime')
p.print_stats(50)

```
