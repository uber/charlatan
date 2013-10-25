from __future__ import absolute_import

import mock

from charlatan import testing
from charlatan import depgraph
from charlatan import Fixture
from charlatan import FixturesManager


class testFixturesManager(testing.TestCase):

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
        fm = FixturesManager()
        fm.load(
            './charlatan/tests/data/dependencies.yaml'
        )
        assert fm.depgraph.has_edge_between('fixture1', 'fixture2')
        assert fm.depgraph.has_edge_between('fixture1', 'fixture3')
        assert fm.depgraph.has_edge_between('fixture4', 'fixture3')
        assert fm.depgraph.has_edge_between('fixture2', 'fixture4')

    def test_notices_cyclic_dependencies(self):
        """test that charlatan bails early if you created a cyclic dependency"""

        fm = FixturesManager()
        self.assertRaises(
            depgraph.HasACycle,
            fm.load,
            './charlatan/tests/data/cyclic_dependencies.yaml'
        )

    def test_constructs_ancestors(self):
        """test that all ancestors (both depend_on and !rel) are constructed"""

        fm = FixturesManager()
        fm.load(
            './charlatan/tests/data/dependencies.yaml'
        )
        assert not fm.cache
        # loading fixture3 should load fixture1 and fixture2 also
        fm.get_fixture('fixture3')
        self.assertIn('fixture1', fm.cache)
        self.assertIn('fixture4', fm.cache)

    def test_depend_on_ancestors_are_saved(self):
        """test that other fixtures explicitly dependend on with `depend_on` are saved"""

        fm = FixturesManager()
        mocks = {}

        def mock_get_class(other):
            if other.key not in mocks:
                mocks[other.key] = mock.Mock(name=other.key)
            return mocks[other.key]
        with mock.patch.object(Fixture, 'get_class', mock_get_class):
            fm.load(
                './charlatan/tests/data/saved_dependencies.yaml',
            )
            fm.install_fixture('fixture2')
            # all fixtures should have been initialized because they're dependencies of fixture2
            self.assertIn('fixture1', fm.cache)
            self.assertIn('fixture2', fm.cache)
            self.assertIn('fixture3', fm.cache)
            f1 = fm.get_fixture('fixture1')
            f2 = fm.get_fixture('fixture2')
            f3 = fm.get_fixture('fixture3')
            # fixtures 1 and 2 should be saved (2 because it's installed, 1 because it's a dep of 2)
            # fixture 3 should *not* be saved because it's a !rel and we don't save those implicitly
            f1.save.assert_called_once_with()
            f2.save.assert_called_once_with()
            self.assertEqual(f3.save.call_count, 0)
