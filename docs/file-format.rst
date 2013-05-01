File format
===========

charlatan only supports YAML at time of writing.
Fixtures are defined using a YAML file. Here is its general structure:


.. include:: examples/fixtures.yaml
    :code: yaml


Post creation
-------------

For a given fixture, `post_creation` lets you change some attributes after
instantiation. Here's the pseudo-code:

.. code-block:: python

    instance = ObjectClass(**fields)
    for k, v in post_creation:
        setattr(instance, k, v)
