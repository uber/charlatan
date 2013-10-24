from __future__ import absolute_import

from charlatan import testing
from charlatan import depgraph
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
