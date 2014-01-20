from __future__ import absolute_import

import pytest

from charlatan import testing
from charlatan import depgraph
from charlatan import FixturesManager


class TestFixturesManager(testing.TestCase):

    def test_install_fixture(self):
        """install_fixture should return the fixture."""

        fixtures_manager = FixturesManager()
        fixtures_manager.load(
            './charlatan/tests/data/relationships_without_models.yaml')

        fixture = fixtures_manager.install_fixture('simple_dict')

        self.assertEqual(fixture, {
            'field1': 'lolin',
            'field2': 2,
        })

    def test_uninstall_fixture(self):
        """uninstall_fixture should return the fixture."""

        fixtures_manager = FixturesManager()
        fixtures_manager.load(
            './charlatan/tests/data/relationships_without_models.yaml')

        fixtures_manager.install_fixture('simple_dict')
        fixture = fixtures_manager.uninstall_fixture('simple_dict')
        self.assertEqual(fixture, {
            'field1': 'lolin',
            'field2': 2,
        })

        # verify we are forgiving with list inputs
        fixtures = fixtures_manager.install_fixtures('simple_dict')
        self.assertEqual(len(fixtures), 1)

        fixtures = fixtures_manager.uninstall_fixtures('simple_dict')
        self.assertEqual(len(fixtures), 1)
        self.assertEqual(fixtures[0], {
            'field1': 'lolin',
            'field2': 2,
        })

    def test_uninstall_non_installed_fixture(self):
        """uninstall_fixture should return None.

        The method returns None since the fixture has not been previously
        installed.
        """

        fixtures_manager = FixturesManager()
        fixtures_manager.load(
            './charlatan/tests/data/relationships_without_models.yaml')

        fixture = fixtures_manager.uninstall_fixture('simple_dict')
        self.assertEqual(fixture, None)

    def test_uninstall_fixtures(self):
        """uninstall_fixtures should return the list of installed fixtures."""
        fixtures_manager = FixturesManager()
        fixtures_manager.load(
            './charlatan/tests/data/relationships_without_models.yaml')

        fixture_keys = ('simple_dict', 'dict_with_nest')

        fixtures_manager.install_fixtures(fixture_keys)
        self.assertEqual(len(fixtures_manager.cache.keys()), 2)

        fixtures = fixtures_manager.uninstall_fixtures(fixture_keys)
        self.assertEqual(len(fixtures), 2)
        self.assertEqual(len(fixtures_manager.cache.keys()), 0)

        # uninstalling non-exiting fixtures should not raise an exception
        fixtures = fixtures_manager.uninstall_fixtures(fixture_keys)
        self.assertEqual(len(fixtures), 0)
        self.assertEqual(len(fixtures_manager.cache.keys()), 0)

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
