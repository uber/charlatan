File format
===========

.. testsetup:: *

    from charlatan import FixturesManager

charlatan only supports YAML at time of writing.

Fixtures are defined in a YAML file. Here is its general structure:

.. literalinclude:: examples/fixtures.yaml
    :language: yaml

In this example:

* ``toaster``, ``toast1`` and ``toast2`` are the fixture keys.
* ``model`` is where to get the model. Both relative and absolute addressing are supported
* ``fields`` are provided as argument when instantiating the class:
  ``Toaster(**fields)``.
* ``!rel`` lets you create relationships by pointing to another fixture key.
* ``!now`` lets you enter timestamps. It supports basic operations
  (adding/subtracting days, months, years). It is evaluated when the fixture
  is instantiated.
* ``!epoch_now`` generates epoch timestamps and supports the same operations as
  ``!now``.

.. NOTE::
  Inside ``fields``, ``!now`` is supported only as a first level list item,
  or as a dictionary value.


Defining a fixture
------------------

A fixture has an identifier (in the example above, ``toaster`` is one of
the fixture identifiers), as well as the following configuration:

* ``fields``: a dictionary for which keys are attribute, and values are their
  values
* ``model`` gives information about how to retrieve the model
* ``post_creation`` lets you have some attribute values be assigned after
  instantiation.

Inheritance
-----------

Fixtures can inherit from other fixtures.

.. literalinclude:: examples/fixtures_inheritance.yaml
    :language: yaml

.. doctest::

    >>> import pprint
    >>> from charlatan import FixturesManager
    >>> manager = FixturesManager()
    >>> manager.load("docs/examples/fixtures_inheritance.yaml")
    >>> manager.get_fixture("first")
    {'foo': 'bar'}
    >>> manager.get_fixture("second")
    {'foo': 'bar'}
    >>> pprint.pprint(manager.get_fixture("third"))
    {'foo': 'bar', 'toaster': 'toasted'}
    >>> fourth = manager.get_fixture("fourth")
    >>> fourth
    Counter({'foo': 'bar'})
    >>> fourth.__class__.__name__
    'Counter'
    >>> fifth = manager.get_fixture("fifth")
    >>> fifth
    Counter({'toaster': 'toasted', 'foo': 'bar'})
    >>> fifth.__class__.__name__
    'Counter'

If your fields are dict, then the first-level key will override everything,
unless you use ``deep_inherit``:

.. literalinclude:: ../charlatan/tests/example/data/deep_inherit.yaml
    :language: yaml

Example test:

.. literalinclude:: ../charlatan/tests/example/test_deep_inherit.py

.. versionadded:: 0.4.5
    You can use ``deep_inherit`` to trigger nested inheritance for dicts.

.. versionadded:: 0.2.4
    Fixtures can now inherits from other fixtures.

Having dictionaries as fixtures
-------------------------------

If you don't specify the model, the content of ``fields`` will be returned as
is. This is useful if you want to enter a dictionary or a list directly.

.. literalinclude:: examples/fixtures_dict.yaml
    :language: yaml

.. doctest::

    >>> manager = FixturesManager()
    >>> manager.load("docs/examples/fixtures_dict.yaml")
    >>> manager.get_fixture("fixture_name")
    {'foo': 'bar'}
    >>> manager.get_fixture("fixture_list")
    ['foo', 'bar']

.. versionadded:: 0.2.4
    Empty models are allowed so that dict ands lists can be used as fixtures.

Getting an already existing fixture from the database
-----------------------------------------------------

You can also get a fixture directly from the database (it uses ``sqlalchemy``):
in this case, you just need to specify the ``model`` and an ``id``.

.. literalinclude:: examples/fixtures_id.yaml
    :language: yaml

Dependencies
------------

If a fixture depends on some side effect of another fixture, you can mark
that dependency (and, necessarily, ordering) by using the ``depend_on``
section.

.. literalinclude:: examples/dependencies.yaml
    :language: yaml

.. versionadded:: 0.2.7

.. _post_creation:

Post creation
-------------

Example:

.. code-block:: yaml

    user:
      fields:
        name: Michel Audiard
      model: User
      post_creation:
        has_used_toaster: true
        # Note that rel are allowed in post_creation
        new_toaster: !rel blue_toaster

For a given fixture, ``post_creation`` lets you change some attributes after
instantiation. Here's the pseudo-code:

.. code-block:: python

    instance = ObjectClass(**fields)
    for k, v in post_creation:
        setattr(instance, k, v)

.. versionadded:: 0.2.0
    It is now possible to use ``rel`` in post_creation.

Linking to other objects
------------------------

Example:

.. literalinclude:: examples/relationships.yaml
    :language: yaml
    :lines: 1-16

To link to another object defined in the configuration file, use ``!rel``. You
can link to another objet (e.g. ``!rel toaster``) or to another object's
attribute (e.g. ``!rel toaster.color``).

.. doctest::

    >>> manager = FixturesManager()
    >>> manager.load("docs/examples/relationships.yaml",
    ...     models_package="charlatan.tests.fixtures.simple_models")
    >>> manager.get_fixture("user").toasters
    [<Toaster 'red'>]
    >>> manager.get_fixture("toaster_colors")
    {'color': 'red'}

You can also link to specific attributes of collection's item (see
:ref:`collection` for more information about collections).

.. literalinclude:: examples/relationships.yaml
    :language: yaml
    :lines: 18-

.. doctest::

    >>> manager.get_fixture("toaster_from_collection")
    <Toaster 'red'>

.. versionadded:: 0.2.0
   It is now possible to link to another object' attribute.

.. _collection:

Collections of Fixtures
-----------------------

Charlatan also provides more efficient way to define variations of fixtures.
The basic idea is to define the model and the default fields, then use the
``objects`` key to define related fixtures. There's two ways to define those
fixtures in the ``objects`` key:

* Use a list. You will then be able to access those fixtures via their index,
  e.g. ``toaster.0`` for the first item.
* Use a dict. The key will be the name of the fixture, the value a dict of
  fields. You can access them via their namespace: e.g. ``toaster.blue``.

You can also install all of them by installing the name of the collection.

.. literalinclude:: examples/collection.yaml
    :language: yaml

Here's how you would use this fixture file to access specific fixtures:

.. doctest::

    >>> manager = FixturesManager()
    >>> manager.load("docs/examples/collection.yaml")
    >>> manager.get_fixture("toasters.green")
    <Toaster 'green'>
    >>> manager.get_fixture("anonymous_toasters.0")
    <Toaster 'yellow'>

You can also access the whole collection:

.. doctest::

    >>> pprint.pprint(manager.get_fixture("toasters"))
    {'blue': <Toaster 'blue'>, 'green': <Toaster 'green'>}
    >>> manager.get_fixture("anonymous_toasters")
    [<Toaster 'yellow'>, <Toaster 'black'>]

Like any fixture, this collection can be linked to in a relationship using the
``!rel`` keyword in an intuitive way.

.. doctest::

    >>> pprint.pprint(manager.get_fixture("collection"))
    {'things': {'blue': <Toaster 'blue'>, 'green': <Toaster 'green'>}}
    >>> user1 = manager.get_fixture("users.1")
    >>> user1.toasters
    [<Toaster 'yellow'>, <Toaster 'black'>]
    >>> manager.get_fixture("users.2").toasters
    [<Toaster 'green'>]
    >>> manager.get_fixture("users.3").toasters
    [<Toaster 'yellow'>]

.. versionchanged:: 0.3.4
    Access to unnamed fixture by using a ``.{index}`` notation instead of
    ``_{index}``.

.. versionadded:: 0.3.4
    You can now have list of named fixtures.

.. versionadded:: 0.2.8
    It is now possible to retrieve lists of fixtures and link to them with
    ``!rel``

Loading Fixtures from Multiple Files
------------------------------------

Loading fixtures from multiple files works similarly to loading collections. In
this case, every fixture in a single file is preceded by a namespace taken from
the name of that file. Relationships between fixtures in different files
specified using the ``!rel`` keyword may be specified by prefixing the desired
target fixture with its file namespace.

.. literalinclude:: examples/relationships.yaml
    :language: yaml

.. literalinclude:: examples/files.yaml
    :language: yaml

.. doctest::

    >>> manager = FixturesManager()
    >>> manager.load(["docs/examples/relationships.yaml",
    ...     "docs/examples/files.yaml"],
    ...     models_package="charlatan.tests.fixtures.simple_models")
    >>> manager.get_fixture("files.toaster")
    <Toaster 'red'>

.. versionadded:: 0.3.7
    It is now possible to load multiple fixtures files with ``FixturesManager``

Datetime and timestamps
-----------------------

Use ``!now``, which returns timezone-aware datetime. You can use modifiers, for
instance:

* ``!now +1y`` returns the current datetime plus one year
* ``!now +5m`` returns the current datetime plus five months
* ``!now -10d`` returns the current datetime minus ten days
* ``!now +15M`` (note the case) returns the current datetime plus 15 minutes
* ``!now -30s`` returns the current datetime minus 30 seconds

For naive datetime (see the definition in Python's `datetime
<https://docs.python.org/2/library/datetime.html>`_ module documentation), use
``!now_naive``. It also supports deltas.

For Unix timestamps (seconds since the epoch) you can use ``!epoch_now``:

* ``!epoch_now +1d`` returns the current datetime plus one year in seconds
  since the epoch
* ``!epoch_now_in_ms`` returns the current timestamp in milliseconds

All the same time deltas work.

.. versionadded:: 0.4.6
    ``!epoch_now_in_ms`` was added.

.. versionadded:: 0.4.4
    ``!now_naive`` was added.

.. versionadded:: 0.2.9
    It is now possible to use times in seconds since the epoch

Unicode Strings
---------------

.. versionadded:: 0.3.5

In python 2 strings are not, by default, loaded as unicode.  To load all the
strings from the yaml files as unicode strings, pass the option
`use_unicode` as `True` when you instantiate your fixture manager.
