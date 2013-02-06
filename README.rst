Charlatan: Fixtures Made Easy
=============================

`Charlatan` is a library that you can use in your tests to create database
fixtures. Its aim is to provide a pragmatic interface that focuses on making it
simple to define and install fixtures for your tests. It is also agnostic in so
far as even though it's designed to work out of the box with SQLAlchemy models,
it can work with pretty much anything else.


Getting started
^^^^^^^^^^^^^^^

.. code-block:: python

    from charlatan import FixtureManager

    fixture_manager = FixtureManager("./tests/data/fixtures.yaml")


    def run_test():
        """Verify that the toaster is working."""

        global fixture_manager
        toaster = fixture_manager.install_fixture("toaster")
        assert toaster.toast() == "toasting..."


Obviously, most of the time you would be wrapping your tests inside a
``TestCase`` class:


.. code-block:: python

    from charlatan import FixtureManager

    fixture_manager = FixtureManager("./tests/data/fixtures.yaml")


    def run_test():
        """Verify that the toaster is working."""

        global fixture_manager
        toaster = fixture_manager.install_fixture("toaster")
        assert toaster.toast() == "toasting..."


Installation
^^^^^^^^^^^^

For now, you need to install `charlatan` by adding the following to your
``requirements.txt``:

.. code


############################## RENDULA
