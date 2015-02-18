.. _builders:

Builders
========

Builders provide a powerful way to customize getting fixture. You can define
your own builders and provide them as arguments when you instantiate
:py:class:`charlatan.FixturesManager`.

Example
-------

Here's an example inspired by the schematics library, which expects a dict of
attributes as a single instantiation argument:

.. literalinclude:: ../charlatan/tests/example/test_custom_builder.py

YAML file:

.. literalinclude:: ../charlatan/tests/example/data/custom_builder.yaml


API
---

.. automodule:: charlatan.builder
    :members:
    :undoc-members:
    :special-members: __call__
