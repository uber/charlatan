Quickstart
==========


Setting up your tests
---------------------


You first need to load a fixtures file (do it once for the whole test suite)
with :py:meth:`charlatan.FixturesManager.load`:

.. code-block:: python

    import charlatan
    charlatan.load("./tests/data/fixtures.yaml"
                   db_session=Session,
                   models_package="toaster.models")


`Charlatan` works best when used with :py:class:`unittest.TestCase`. Your test
class needs to inherits from :py:class:`charlatan.FixturesManagerMixin`.

`Charlatan` uses an internal cache to store fixtures instance (in particular to
create relationships). If you are resetting your database after each tests
(using transactions or by manually truncating all tables), you need to clean
the cache either in :py:meth:`TestCase.setUp`, otherwise `Charlatan` will try
accessing objects that are not anymore in the sqlalchemy session.

.. code-block:: python

    class TestToaster(unittest.TestCase, charlatan.FixturesManagerMixin):

        def setUp(self):
            self.clean_fixtures_cache()


Defining fixtures
-----------------

Fixtures are defined using a YAML file. Here is its general structure:


.. literalinclude:: examples/fixtures.yaml
    :language: yaml


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
            self.toaster.save()


What happens when you install a fixture
"""""""""""""""""""""""""""""""""""""""

Here's the general process:

1. The fixture is instantiated: ``Model(**fields)``.
2. If there's any post creation hook, they are run (see :ref:`post_creation`
   for more information).
3. The fixture is then saved. If it's a sqlalchemy model, charlatan will detect
   it, add it to the session and commit it (``db_session.add(instance); db_session.commit()``).
   If it's not a sqlalchemy model, charlatan will try to call a `save` method
   on the instance. If there's no such method, charlatan will do nothing.

Fixtures are then attached to your test class, you can access them as instance
attributes:

.. code-block:: python

    class MyTest(FixturesMixin):

        fixtures = ("toaster", "toast1", "toast2")

        def test_toaster(self):
            self.toaster.toast(self.toast1, self.toast2)

:ref:`hooks` are also supported.
