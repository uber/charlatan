from __future__ import absolute_import
from __future__ import print_function

import collections
import copy

from ._compat import itervalues


class HasACycle(Exception):
    pass


class DepGraph(object):
    """A simple directed graph, suitable for doing dependency management"""

    def __init__(self):
        self.nodes = set([])
        self.rtl_edges = collections.defaultdict(list)
        self.ltr_edges = collections.defaultdict(list)
        self._topo_sort_cache = None
        self.dirty = True

    def has_edge_between(self, lhs, rhs):
        return rhs in self.ltr_edges[lhs]

    def add_node(self, node):
        self.nodes.add(node)
        self.dirty = True

    def add_edge(self, lhs, rhs):
        self.add_node(lhs)
        self.add_node(rhs)
        self.rtl_edges[rhs].append(lhs)
        self.ltr_edges[lhs].append(rhs)
        self.dirty = True

    @property
    def acyclic(self):
        try:
            self.topo_sort()
        except HasACycle:
            return False
        return True

    def _topo_sort(self):
        root_nodes = []
        for node in self.nodes:
            if not self.rtl_edges[node]:
                root_nodes.append(node)
        sorted_list = []
        edges = copy.deepcopy(self.ltr_edges)
        back_edges = copy.deepcopy(self.rtl_edges)
        while root_nodes:
            node = root_nodes.pop(0)
            sorted_list.append(node)
            for target in edges[node][:]:
                edges[node].remove(target)
                back_edges[target].remove(node)
                if not back_edges[target]:
                    root_nodes.append(target)
        if any(v for v in itervalues(edges)):
            raise HasACycle()
        return sorted_list

    def topo_sort(self):
        if not self._topo_sort_cache or self.dirty:
            self._topo_sort_cache = self._topo_sort()
            self.dirty = False
        return self._topo_sort_cache

    def ancestors_of(self, node):
        """Return a list of ancestors of given node, in topological order."""
        parents = []
        work_queue = [node]
        while work_queue:
            node = work_queue.pop(0)
            for parent in self.rtl_edges[node]:
                parents.append(parent)
                work_queue.append(parent)
        topo_order = self.topo_sort()
        return sorted(parents, key=lambda i: topo_order.index(i))
