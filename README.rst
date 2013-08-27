Charlatan: Fixtures Made Easy
=============================

.. image:: https://travis-ci.org/uber/charlatan.png?branch=master
    :target: https://travis-ci.org/uber/charlatan

**Efficiently manage and install data fixtures**

`Charlatan` is a library that you can use in your tests to create database
fixtures. Its aim is to provide a pragmatic interface that focuses on making it
simple to define and install fixtures for your tests. It is also agnostic in so
far as even though it's designed to work out of the box with SQLAlchemy models,
it can work with pretty much anything else.

Documentation
-------------

Latest documentation:
`charlatan.readthedocs.org/en/latest/ <https://charlatan.readthedocs.org/en/latest/>`_

Getting started
---------------

.. code-block:: python

    import unittest

    from toaster.models import db_session

    import charlatan

    charlatan.load("./tests/data/fixtures.yaml",
                   models_package="toaster.models",
                   db_session=db_session)


    class TestToaster(unittest.TestCase, charlatan.FixturesManagerMixin):

        def setUp(self):
            self.clean_fixtures_cache()
            self.install_fixtures(("toaster", "user"))

        def test_toaster(self):
            """Verify that toaster can toast."""

            self.toaster.toast()

Installation
------------

Using `pip`::

    pip install charlatan

License
-------

charlatan is available under the MIT License.

Copyright Uber 2013, Charles-Axel Dein <charles@uber.com>

Authors
-------

Charles-Axel Dein <charles@uber.com>
Erik Formella <erik@uber.com>
