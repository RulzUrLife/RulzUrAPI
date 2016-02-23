Helpers for querying the API through curl
=========================================

This directory contains a list of JSON files which can be used
to test the API through ``curl``

Requirements
------------

At least have ``curl`` installed and maybe ``jq`` if you want to manipulate
the returned JSON.

Knowing the basis of ``curl`` and ``jq`` is a good start in order to save time.
Look at the documentation for further informations:

* ``curl`` documentation available `here <https://curl.haxx.se/docs/>`__,
  manpage available `here <https://curl.haxx.se/docs/manpage.html>`__
* ``jq`` documentation available `here <https://stedolan.github.io/jq/>`__,
  manpage available `here <https://stedolan.github.io/jq/manual/>`__

Getting started
---------------

Just run the following command line by replacing <filepath>
by the path of the JSON

.. code-block:: bash

  $ curl -X POST -H "Content-Type: application/json" -s -d @<filepath> | jq '.'


