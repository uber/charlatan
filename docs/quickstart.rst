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
    ...     overrides={"color": "blue"})
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
class needs to inherit from :py:class:`charlatan.FixturesManagerMixin`.

`Charlatan` uses an internal cache to store fixtures instance (in particular to
create relationships). If you are resetting your database after each tests
(using transactions or by manually truncating all tables), you need to clean
the cache in :py:meth:`TestCase.setUp`, otherwise `Charlatan` will try
accessing objects that are not anymore in the sqlalchemy session.

.. literalinclude:: ../charlatan/tests/test_simple_testcase.py
    :language: python

Using fixtures
--------------

There are multiple ways to require and use fixtures. When you install a fixture
using the :py:class:`charlatan.FixturesManagerMixin`, it gets attached to the
instance and can be accessed as an instance attribute (e.g. ``self.toaster``).

For each tests, in setUp and tearDown
"""""""""""""""""""""""""""""""""""""

.. code-block:: python

    class MyTest(FixturesManagerMixin):

        def setUp(self):
            # This will create self.toaster and self.brioche
            self.install_fixtures(("toaster", "brioche"))

        def test_toaster(self):
            """Verify that a toaster toasts."""
            self.toaster.toast(self.brioche)

For a single test
"""""""""""""""""

.. code-block:: python

    class MyTest(FixturesMixin):

        def test_toaster(self):
            self.install_fixture("toaster")

With pytest
"""""""""""

It's extremely easy to use charlatan with pytest. There are multiple ways to
achieve nice readability, here's one possibility.

In ``conftest.py``:

.. code-block:: python

    import pytest


    @pytest.fixture
    def get_fixture(request):
        request.addfinalizer(fixtures_manager.clean_cache)
        return fixtures_manager.get_fixture

In your test file:

.. code-block:: python

    def test_toaster(get_fixture):
        """Verify that a toaster toasts."""
        toaster = get_fixture('toaster')
        toast = get_fixture('toast')
        ...

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

What happens when you install a fixture
"""""""""""""""""""""""""""""""""""""""

Here's the default process (you can modify part or all of it using :ref:`hooks`
or :ref:`builders`):

1. The fixture is instantiated: ``Model(**fields)``.
2. If there's any post creation hook, they are run (see :ref:`post_creation`
   for more information).
3. The fixture is then saved. If it's a sqlalchemy model, charlatan will detect
   it, add it to the session and commit it (``db_session.add(instance); db_session.commit()``).
   If it's not a sqlalchemy model, charlatan will try to call a `save` method
   on the instance. If there's no such method, charlatan will do nothing.

:ref:`hooks` are also supported.

Uninstalling fixtures
"""""""""""""""""""""

Because charlatan is not coupled with the persistence layer, it does not have
strong opinions about resetting the world after a test runs. There's multiple
ways to handle test tear down:

* Wrap test inside a transaction (if you're using sqlalchemy, its documentation
  has a `good
  explanation <http://docs.sqlalchemy.org/en/rel_0_9/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites>`_
  about how to achieve that).
* Drop and recreate the database (not really efficient).
* Install and uninstall fixtures explicitly (you have to keep track of them
  though, if you forget to uninstall one fixture it will leak in the other
  tests). See
  :py:meth:`charlatan.FixturesManager.uninstall_fixture`.
