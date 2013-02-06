Quickstart
==========


Setting up your tests
---------------------

There are two steps:

1. Making sure your test class inherits from :py:class:`charlatan.FixturesManagerMixin`.
2. Calling :py:meth:`charlatan.FixturesManagerMixin.load_fixtures` with the right arguments.

.. include:: examples/testcase_with_fixtures.py
    :code: python


Defining fixtures
-----------------

Fixtures are defined using a YAML file. Here is its general structure:


.. include:: examples/fixtures.yaml
    :code: yaml


In this example: 

* ``toaster``, ``toast1`` and ``toast2`` are the fixture keys.
* ``model`` is where to get the model. Both relative and absolute addressing are supported
* ``fields`` are provided as argument when instantiating the class:
  ``Toaster(**fields)``.
* ``!rel`` lets you create relationships by pointing to another fixture key.
* ``!now`` lets you enter timestamps. It supports basic operations
  (adding/subtracting days, months, years). **Note** that ``!now`` is evaluated when
  the fixture file is read, not when the test is run.


Using fixtures
--------------

There are multiple ways to require and use fixtures.

For each tests, in class attribute
""""""""""""""""""""""""""""""""""

.. code-block:: python

    class MyTest(FixturesMixin):
        fixtures = ("toaster", )

        def test_stuff(self):
            self.toaster.toast()
            ...


For each tests, in setUp
""""""""""""""""""""""""

.. code-block:: python

    class MyTest(FixturesMixin):

        def setUp(self):
            self.install_fixtures(("client", "driver"))

For a single test
"""""""""""""""""

.. code-block:: python

  class MyTest(FixturesMixin):

      def test_toaster(self):
          self.install_fixtures("toaster")


Getting a fixture without saving it
"""""""""""""""""""""""""""""""""""

If you want to have complete control over the fixture, you can also get it
without saving it nor attaching it to the test class:


.. code-block:: python

    class MyTest(FixturesMixin):

        def test_toaster(self):
            self.toaster = self.get_fixture("toaster")
            self.toaster.brand = "Flying"
            ...
            self.toaster.save()


What happens when you install a fixture
"""""""""""""""""""""""""""""""""""""""

Here is the simplified workflow:

.. code-block:: python

    Model, fields = get_fixture_for_key("toaster")
    instance = Model(**fields)
    session.add(instance)
    session.commit()

Fixtures are then attached to your test class, you can access them as instance
attributes:

.. code-block:: python

    class MyTest(FixturesMixin):

        fixtures = ("toaster", "toast1", "toast2")

        def test_toaster(self):
            self.toaster.toast(self.toast1, self.toast2)
