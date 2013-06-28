File format
===========

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
