Changelog for Charlatan
=======================

0.2.9 (unreleased)
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
