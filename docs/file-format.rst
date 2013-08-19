File format
===========

.. testsetup:: *

    from charlatan import FixturesManager

charlatan only supports YAML at time of writing.
Fixtures are defined using a YAML file. Here is its general structure:

.. literalinclude:: examples/fixtures.yaml
    :language: yaml


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

    >>> manager = FixturesManager()
    >>> manager.load("./examples/fixtures_inheritance.yaml")
    >>> manager.get_fixture("first")
    {'foo': 'bar'}
    >>> manager.get_fixture("second")
    {'foo': 'bar'}
    >>> manager.get_fixture("third")
    {'foo': 'bar', 'toaster': 'toasted'}
    >>> fourth = manager.get_fixture("fourth")
    >>> fourth
    {'foo': 'bar'}
    >>> fourth.__class__.__name__
    'UserDict'
    >>> fifth = manager.get_fixture("fifth")
    >>> fifth
    {'foo': 'bar', 'toaster': 'toasted'}
    >>> fifth.__class__.__name__
    'UserDict'

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
    >>> manager.load("./examples/fixtures_dict.yaml")
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

.. code-block:: yaml

    user:
      fields:
        name: Michel Audiard
        favorite_toaster: !rel red_toaster
        toaster_id: !rel toaster.id
      model: User

To link to another object defined in the configuration file, use ``!rel``. You
can link to another objet (e.g. ``!rel red_toaster``) or to another object's
attribute (e.g. ``!rel toaster.id``).

.. versionadded:: 0.2.0
   It is now possible to link to another object' attribute.

Relative timestamps
-------------------

Use ``!now``:

* ``!now +1y`` returns the current datetime plus one year
* ``!now +5m`` returns the current datetime plus five months
* ``!now -10d`` returns the current datetime minus ten days
* ``!now +15M`` (note the case) returns the current datetime plus 15 minutes
* ``!now -30s`` returns the current datetime minus 30 seconds
