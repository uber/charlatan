API Reference
=============

.. testsetup:: *

    import datetime
    from charlatan.utils import apply_delta, extended_timedelta


charlatan
---------

The module provides the following shortcuts:

* load
* install_all_fixtures
* set_hook
* ``fixtures_manager`` object.


.. autofunction:: charlatan.load

.. autofunction:: charlatan.install_all_fixtures

.. autofunction:: charlatan.set_hook

FixturesManager
---------------

.. autoclass:: charlatan.FixturesManager
    :members:


FixturesManagerMixin
--------------------

.. autoclass:: charlatan.FixturesManagerMixin
    :members:


Fixture
-------

.. autoclass:: charlatan.Fixture
    :members:


Utils
-----

.. automodule:: charlatan.utils
    :members:
