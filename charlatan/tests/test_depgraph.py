from __future__ import absolute_import

from charlatan import testing
from charlatan.depgraph import DepGraph, HasACycle


class TestDepGraph(testing.TestCase):

    def test_topo_sort(self):
        """Test the topo_sort function of DepGraph"""
        d = DepGraph()
        #
        #      a    b
        #       \  /
        #        c
        #        |
        #        d
        #       /  \
        #      e    f
        d.add_edge('a', 'c')
        d.add_edge('b', 'c')
        d.add_edge('c', 'd')
        d.add_edge('d', 'e')
        d.add_edge('d', 'f')
        l = d.topo_sort()
        self.assertEqual(l, ['a', 'b', 'c', 'd', 'e', 'f'])
        assert d.acyclic

    def test_topo_sort_knows_what_cycles_are(self):
        """Test that topo_sort fails on cyclic graphs"""
        d = DepGraph()
        d.add_edge('a', 'b')
        d.add_edge('b', 'c')
        d.add_edge('c', 'a')
        self.assertRaises(HasACycle, d.topo_sort)
        assert not d.acyclic

    def test_ancestors_of(self):
        """Test the ancestors_of function in DepGraph"""
        d = DepGraph()
        #
        #   a    b
        #    \  /
        #     c
        #    / \
        #   d   e
        #   |
        #   f
        d.add_edge('a', 'c')
        d.add_edge('b', 'c')
        d.add_edge('c', 'd')
        d.add_edge('c', 'e')
        d.add_edge('d', 'f')
        l = d.ancestors_of('d')
        self.assertEqual(l, ['a', 'b', 'c'])

    def test_has_edge_between(self):
        """Test the has_edge_between function"""
        d = DepGraph()
        #
        #  a    b
        #  |    |
        #  c -- d    e
        d.add_edge('a', 'c')
        d.add_edge('b', 'd')
        d.add_edge('c', 'd')
        d.add_node('e')
        assert d.has_edge_between('a', 'c')
        assert not d.has_edge_between('c', 'a'), 'has_edge_between should not be commutative'
        assert not d.has_edge_between('a', 'b'), 'has_edge_between should be edges, not paths'
        assert not d.has_edge_between('e', 'd')
