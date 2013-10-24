from __future__ import absolute_import

from charlatan import testing
from charlatan.depgraph import DepGraph, HasACycle


class TestDepGraph(testing.TestCase):
    def test_topo_sort(self):
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
        d = DepGraph()
        d.add_edge('a', 'b')
        d.add_edge('b', 'c')
        d.add_edge('c', 'a')
        self.assertRaises(HasACycle, d.topo_sort)
        assert not d.acyclic
