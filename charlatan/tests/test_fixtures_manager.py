from __future__ import absolute_import
from datetime import datetime

import pytest
import pytz
from freezegun import freeze_time

from charlatan import testing
from charlatan import depgraph
from charlatan import FixturesManager


def test_overrides_and_in_cache():
    manager = FixturesManager()
    manager.load('./docs/examples/simple_fixtures.yaml')
    # Add it to the cache
    manager.install_fixture("toaster")
    toaster = manager.install_fixture("toaster", overrides={"color": "blue"})
    assert toaster.color == 'blue'


class TestFixturesManager(testing.TestCase):

    def test_load_two_files(self):
        """Verify we can load two files."""
        manager = FixturesManager()
        manager.load(
            './charlatan/tests/data/relationships_without_models.yaml')
        manager.load(
            './charlatan/tests/data/simple.yaml')
        assert 'simple_dict' in manager.keys()

    def test_load_empty_file(self):
        """Verify we can load a emtpy file."""
        manager = FixturesManager()
        manager.load('./charlatan/tests/data/empty.yaml')
        self.assertEqual(list(manager.keys()), [])

    def test_install_fixture(self):
        """install_fixture should return the fixture."""
        manager = FixturesManager()
        manager.load(
            './charlatan/tests/data/relationships_without_models.yaml')

        fixture = manager.install_fixture('simple_dict')

        self.assertEqual(fixture, {
            'field1': 'lolin',
            'field2': 2,
        })

    def test_get_all_fixtures(self):
        manager = FixturesManager()
        manager.load('./charlatan/tests/data/simple.yaml')
        assert len(manager.get_all_fixtures()) == 1

    def test_uninstall_all_fixtures(self):
        manager = FixturesManager()
        manager.load('./charlatan/tests/data/simple.yaml')
        assert len(manager.install_all_fixtures()) == 1
        manager.uninstall_all_fixtures()
        assert len(manager.installed_keys) == 0

    @freeze_time("2014-12-31 11:00:00")
    def test_install_fixture_with_now(self):
        """Verify that we can install a fixture with !now tag."""
        manager = FixturesManager()
        manager.load('./charlatan/tests/data/simple.yaml')
        fixture = manager.install_fixture('fixture')
        self.assertEqual(fixture,
                         {'now': datetime(2014, 12, 30, 11, 0,
                                          tzinfo=pytz.utc)})

    def test_install_fixture_override(self):
        """Verify that we can override a fixture field."""
        manager = FixturesManager()
        manager.load('./charlatan/tests/data/simple.yaml')
        fixture = manager.install_fixture('fixture', overrides={'now': None})
        self.assertEqual(fixture, {'now': None})

    def test_uninstall_fixture(self):
        manager = FixturesManager()
        manager.load(
            './charlatan/tests/data/relationships_without_models.yaml')

        manager.install_fixture('simple_dict')
        manager.uninstall_fixture('simple_dict')

        # verify we are forgiving with list inputs
        manager.install_fixtures('simple_dict')
        manager.uninstall_fixtures('simple_dict')

    def test_uninstall_non_installed_fixture(self):
        manager = FixturesManager()
        manager.load(
            './charlatan/tests/data/relationships_without_models.yaml')
        manager.uninstall_fixture('simple_dict')

    def test_dependency_parsing(self):
        fm = FixturesManager()
        fm.load(
            './charlatan/tests/data/dependencies.yaml'
        )
        assert fm.depgraph.has_edge_between('fixture1', 'fixture2')
        assert fm.depgraph.has_edge_between('fixture1', 'fixture3')
        assert fm.depgraph.has_edge_between('fixture4', 'fixture3')
        assert fm.depgraph.has_edge_between('fixture2', 'fixture4')

    def test_notices_cyclic_dependencies(self):
        fm = FixturesManager()
        self.assertRaises(
            depgraph.HasACycle,
            fm.load,
            './charlatan/tests/data/cyclic_dependencies.yaml'
        )

    def test_constructs_ancestors(self):
        fm = FixturesManager()
        fm.load(
            './charlatan/tests/data/dependencies.yaml'
        )
        assert not fm.cache
        # loading fixture3 should load fixture1 and fixture2 also
        fm.get_fixture('fixture3')
        self.assertIn('fixture1', fm.cache)
        self.assertIn('fixture4', fm.cache)

    def test_invalid_hook(self):
        """Verify that can't set an invalid hook."""
        manager = FixturesManager()
        with pytest.raises(KeyError):
            manager.set_hook("invalid", lambda p: p)

    def test_set_hook(self):
        """Verify that we can set a hook."""
        manager = FixturesManager()
        manager.set_hook("before_save", lambda p: p)
