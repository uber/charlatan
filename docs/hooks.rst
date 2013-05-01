.. _hooks:

Hooks
=====


The following hooks are available:

* ``before_install``: called before doing anything. The callback takes no
  argument.
* ``before_save``: called before saving an instance using the SQLAlchemy
  session. The callback takes a single argument which is the instance being
  saved.
* ``after_save``: called after saving an instance using the SQLAlchemy session.
  The callback takes a single argument which is the instance that was saved.
* ``after_install``: called after doing anything. The callback must accept a
  single argument that will be the exception that may have been raised during
  the whole process. This function is guaranteed to be called.


You can register them using :meth:`charlatan.set_hook`.

.. automethod:: charlatan.FixturesManager.set_hook
    :noindex:
