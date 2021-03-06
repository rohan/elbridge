from typing import Set

from elbridge.utilities.types import Edge


class HypotheticalSet:
    def __init__(self, edge_set: Set[Edge]):
        self.edges = set()
        for edge in edge_set:
            self.add_edge(edge)

    def __hash__(self):
        return frozenset(self.edges).__hash__()

    def __eq__(self, other):
        return self.edges == other.edges

    def __repr__(self):
        return repr(self.edges)

    def __contains__(self, edge: Edge):
        i, j = edge
        return (i, j) in self.edges or (j, i) in self.edges

    def add_edge(self, edge: Edge):
        i, j = edge
        self.edges.add((i, j))
        if (j, i) not in self.edges:
            self.edges.add((j, i))
