Quickstart
==========

A simple example
----------------

Let's say we have the following model:

.. literalinclude:: ../charlatan/tests/fixtures/simple_models.py
    :language: python

Let's define a very simple fixtures YAML file:

.. literalinclude:: examples/simple_fixtures.yaml
    :language: yaml

In this example:

* ``toaster`` and ``toasts`` are the fixture keys.
* ``fields`` is provided as argument when instantiating the class:
  ``Toaster(**fields)``.
* ``model`` is the path to the model that we defined.
* ``!rel`` lets you create relationships by pointing to another fixture key.

You first need to load a fixtures file (do it once for the whole test suite)
with :py:meth:`charlatan.FixturesManager.load`:

.. doctest::

    >>> import charlatan
    >>> fixtures_manager = charlatan.FixturesManager()
    >>> fixtures_manager.load("./docs/examples/simple_fixtures.yaml",
    ...     models_package="toaster.models")
    >>> toaster = fixtures_manager.install_fixture("toaster")
    >>> toaster.color
    'red'
    >>> toaster.slots
    5
    >>> toaster.content
    ['Toast 1', 'Toast 2']

Voila!

Factory features
----------------

`Charlatan` provides you with factory features. In particular, you can override
a fixture's defined attributes:

.. doctest::

    >>> toaster = fixtures_manager.install_fixture("toaster",
    ...     attrs={"color": "blue"})
    >>> toaster.color
    'blue'

You can also use inheritance:

.. doctest::

    >>> toaster = fixtures_manager.install_fixture("toaster_green")
    >>> toaster.color
    'green'

Using charlatan in test cases
-----------------------------

`Charlatan` works best when used with :py:class:`unittest.TestCase`. Your test
class needs to inherits from :py:class:`charlatan.FixturesManagerMixin`.

`Charlatan` uses an internal cache to store fixtures instance (in particular to
create relationships). If you are resetting your database after each tests
(using transactions or by manually truncating all tables), you need to clean
the cache either in :py:meth:`TestCase.setUp`, otherwise `Charlatan` will try
accessing objects that are not anymore in the sqlalchemy session.

.. literalinclude:: ../charlatan/tests/test_simple_testcase.py
    :language: python

Using fixtures
--------------

There are multiple ways to require and use fixtures.

For each tests, in setUp and tearDown
"""""""""""""""""""""""""""""""""""""

.. code-block:: python

    class MyTest(FixturesManagerMixin):

        def setUp(self):
            # This will create self.client and self.driver
            self.install_fixtures(("client", "driver"))

        def tearDown(self):
            # This will delete self.client and self.driver
            self.uninstall_fixtures(("client", "driver"))

For a single test
"""""""""""""""""

.. code-block:: python

    class MyTest(FixturesMixin):

        def test_toaster(self):
            self.install_fixture("toaster")
            # do things... and optionally uninstall it once you're done
            self.uninstall_fixture("toaster")

Getting a fixture without saving it
"""""""""""""""""""""""""""""""""""

If you want to have complete control over the fixture, you can also get it
without saving it nor attaching it to the test class:


.. code-block:: python

    class MyTest(FixturesManagerMixin):

        def test_toaster(self):
            self.toaster = self.get_fixture("toaster")
            self.toaster.brand = "Flying"
            self.toaster.save()

Overriding fixture fields
"""""""""""""""""""""""""

You can override a fixture's parameters when getting or installing it.

.. code-block:: python

    manager = FixturesManager()
    manager.load("./examples/fixtures.yaml")
    manager.get_fixture("toaster", attrs={"brand": "Flying"})


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

    class MyTest(FixturesManagerMixin):

        fixtures = ("toaster", "toast1", "toast2")

        def test_toaster(self):
            self.toaster.toast(self.toast1, self.toast2)

:ref:`hooks` are also supported.
