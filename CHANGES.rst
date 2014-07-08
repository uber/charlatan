Changelog for Charlatan
=======================

0.3.7 (2014-07-07)
------------------

- Support loading of multiple fixtures files
- Remove include_relationships option in instance creation

0.3.6 (2014-06-02)
------------------

- Update PYYaml

0.3.5 (2014-06-02)
------------------

- Support loading all strings as unicode

0.3.4 (2014-01-21)
------------------

- Fix getting attribute from relationships

0.3.3 (2014-01-18)
------------------

- Add support for Python 3

0.3.2 (2014-01-16)
------------------

- Add ability to uninstall fixtures (thanks to @JordanB)

0.3.1 (2014-01-10)
------------------

- Numerous tests added, a lot of cleanup.
- Clarification in documentation.
- Remove ``load``, ``set_hook`` and ``install_all_fixtures`` shortcuts from
  charlatan package.
- Remove ``FIXTURES_MANAGER`` singleton. Remove ``charlatan.fixtures_manager``
  shortcut.
- Remove ``db_session`` argument to ``FixturesManager.load``.
- Add ``db_session`` argument to ``FixturesManager`` constructor.
- Remove ``charlatan.fixtures_manager.FixturesMixin``. Replaced by
  ``charlatan.testcase.FixturesManagerMixin``.
- ``FixturesManagerMixin`` now exposes pretty much the same method as
  ``FixturesManager``.
- ``FixturesManagerMixin``'s ``use_fixtures_manager`` was renamed
  ``init_fixtures``.

0.2.9 (2013-11-20)
------------------

- Add ``!epoch_now`` for Unix timestamps (thanks to @erikformella)

0.2.8 (2013-11-12)
------------------

- Add ability to point to a list fixture (thanks to @erikformella)

0.2.7 (2013-10-24)
------------------

- Add ability to define dependencies outside of fields through the `depend_on`
  key in the yaml file (thanks to @Roguelazer)

0.2.6 (2013-09-06)
------------------

- Fix regression that broke API. install_fixture started returning the fixture
  as well as its name. (thanks to @erikformella)

0.2.5 (2013-09-06)
------------------

- Allow relationships to be used in dicts and lists. (thanks to @erikformella)
- Allow for seconds and minutes in relative timestamps (thanks to @kmnovak)

0.2.4 (2013-08-08)
------------------

- Empty models are allowed so that dict ands lists can be used as fixtures.
- Fixtures can now inherits from other fixtures.

0.2.3 (2013-06-28)
------------------

- Added ability to link to a relationship's attribute in YAML file.
- Added ability to use ``!rel`` in ``post_creation``.

0.1.2 (2013-04-01)
------------------

- Started tracking changes
