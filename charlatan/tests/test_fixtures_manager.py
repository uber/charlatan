from __future__ import absolute_import

import mock

from charlatan import testing
from charlatan import depgraph
from charlatan import Fixture
from charlatan import FixturesManager


class TestFixturesManager(testing.TestCase):

    def test_install_fixture(self):
        """install_fixture should return the fixture"""

        fixtures_manager = FixturesManager()
        fixtures_manager.load(
            './charlatan/tests/data/relationships_without_models.yaml')

        fixture = fixtures_manager.install_fixture('simple_dict')

        self.assertEqual(fixture, {
            'field1': 'lolin',
            'field2': 2,
        })

    def test_dependency_parsing(self):
        fixture_manager = FixturesManager()
        fixture_manager.load(
            './charlatan/tests/data/dependencies.yaml'
        )
        assert fixture_manager.depgraph.has_edge_between('fixture1', 'fixture2')
        assert fixture_manager.depgraph.has_edge_between('fixture1', 'fixture3')
        assert fixture_manager.depgraph.has_edge_between('fixture4', 'fixture3')
        assert fixture_manager.depgraph.has_edge_between('fixture2', 'fixture4')

    def test_notices_cyclic_dependencies(self):
        """Test that charlatan bails early if you created a cyclic dependency"""

        fixture_manager = FixturesManager()
        self.assertRaises(
            depgraph.HasACycle,
            fixture_manager.load,
            './charlatan/tests/data/cyclic_dependencies.yaml'
        )

    def test_constructs_ancestors(self):
        """Test that all ancestors (both depend_on and !rel) are constructed"""

        fixture_manager = FixturesManager()
        fixture_manager.load(
            './charlatan/tests/data/dependencies.yaml'
        )
        assert not fixture_manager.cache
        # loading fixture3 should load fixture1 and fixture2 also
        fixture_manager.get_fixture('fixture3')
        self.assertIn('fixture1', fixture_manager.cache)
        self.assertIn('fixture4', fixture_manager.cache)

    def test_depend_on_ancestors_are_saved(self):
        """Test that other fixtures explicitly dependend on with `depend_on` are saved"""

        fixture_manager = FixturesManager()
        mocks = {}

        def mock_get_class(other):
            if other.key not in mocks:
                mocks[other.key] = mock.Mock(name=other.key)
            return mocks[other.key]
        with mock.patch.object(Fixture, 'get_class', mock_get_class):
            fixture_manager.load(
                './charlatan/tests/data/saved_dependencies.yaml',
            )
            fixture_manager.install_fixture('fixture2')
            # all fixtures should have been initialized because they're dependencies of fixture2
            self.assertIn('fixture1', fixture_manager.cache)
            self.assertIn('fixture2', fixture_manager.cache)
            self.assertIn('fixture3', fixture_manager.cache)
            f1 = fixture_manager.get_fixture('fixture1')
            f2 = fixture_manager.get_fixture('fixture2')
            f3 = fixture_manager.get_fixture('fixture3')
            # fixtures 1 and 2 should be saved (2 because it's installed, 1 because it's a dep of 2)
            # fixture 3 should *not* be saved because it's a !rel and we don't save those implicitly
            f1.save.assert_called_once_with()
            f2.save.assert_called_once_with()
            self.assertEqual(f3.save.call_count, 0)
