"""Hand-worked results and independent NetworkX checks."""

import unittest
from itertools import combinations

import networkx as nx

from task2_kruskal import kruskal, prim, random_graph
from task3_constraints import constrained_tree
from task4_spanning_trees import kirchhoff_count, spanning_trees


class CampusAlgorithmTests(unittest.TestCase):
    def test_minimum_spanning_trees(self):
        graphs = [
            (3, [(1, 0, 1), (2, 1, 2), (4, 0, 2)], 3),
            (4, [(1, 0, 1), (1, 0, 2), (1, 0, 3), (5, 1, 2)], 3),
            (3, [(0, 0, 1), (2, 1, 2), (3, 0, 2)], 2),
        ]
        for n, edges, expected in graphs:
            with self.subTest(edges=edges):
                graph = nx.Graph()
                graph.add_nodes_from(range(n))
                graph.add_weighted_edges_from((u, v, w) for w, u, v in edges)
                self.assertEqual(nx.minimum_spanning_tree(graph).size(weight="weight"), expected)
                for algorithm in (prim, kruskal):
                    self.assertEqual(algorithm(n, edges)[1], expected)

    def test_individual_constraints(self):
        edges = [
            (1, 0, 1), (2, 0, 2), (3, 0, 3), (4, 0, 4),
            (6, 1, 4), (7, 2, 3), (8, 3, 4),
        ]
        cases = [
            ({"mandatory": (6, 1, 4)}, 12),
            ({"forbidden": (0, 4)}, 12),
            ({"max_degree": 3}, 12),
            ({"forbidden": (0, 4), "mandatory": (8, 3, 4), "max_degree": 3}, 14),
        ]
        for rules, expected in cases:
            with self.subTest(rules=rules):
                tree = constrained_tree(5, edges, **rules)
                self.assertEqual(sum(w for _, _, w in tree), expected)
                graph = nx.Graph()
                graph.add_nodes_from(range(5))
                graph.add_edges_from((u, v) for u, v, _ in tree)
                self.assertTrue(nx.is_tree(graph))
                if "max_degree" in rules:
                    self.assertLessEqual(max(dict(graph.degree()).values()), rules["max_degree"])

    def test_spanning_tree_counts(self):
        cases = [
            (1, [], 1),
            (3, [(0, 1)], 0),
            (3, [(0, 1), (1, 2)], 1),
            (3, [(0, 1), (1, 2), (0, 2)], 3),
            (4, list(combinations(range(4), 2)), 16),
        ]
        for n, edges, expected in cases:
            with self.subTest(n=n, edges=edges):
                self.assertEqual(sum(1 for _ in spanning_trees(n, edges)), expected)
                self.assertEqual(kirchhoff_count(n, edges), expected)
                graph = nx.Graph()
                graph.add_nodes_from(range(n))
                graph.add_edges_from(edges)
                if nx.is_connected(graph):
                    self.assertEqual(sum(1 for _ in nx.SpanningTreeIterator(graph)), expected)

    def test_benchmark_graphs(self):
        points = [(i, 0) for i in range(100)]
        for dense, expected in ((False, 200), (True, 300)):
            edges = random_graph(points, dense)
            self.assertEqual(len(edges), expected)
            self.assertEqual(len({(u, v) for _, u, v in edges}), expected)
            self.assertEqual(kruskal(100, edges)[1], 99)


if __name__ == "__main__":
    unittest.main()