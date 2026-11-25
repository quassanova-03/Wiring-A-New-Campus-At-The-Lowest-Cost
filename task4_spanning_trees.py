"""Enumerate campus layouts and verify their counts with Kirchhoff's theorem."""

import csv
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path


def spanning_trees(vertex_count, edges):
    """Yield each acyclic set of n-1 edges, which must span all n vertices."""
    for candidate in combinations(edges, vertex_count - 1):
        parent = list(range(vertex_count))

        def find(vertex):
            while parent[vertex] != vertex:
                vertex = parent[vertex]
            return vertex

        for u, v in candidate:
            root_u, root_v = find(u), find(v)
            if root_u == root_v:
                break
            parent[root_u] = root_v
        else:
            yield candidate


def determinant(matrix):
    """Compute a determinant by elimination using exact rational arithmetic."""
    rows = [[Fraction(value) for value in row] for row in matrix]
    result = Fraction(1)
    for column in range(len(rows)):
        pivot_row = next(
            (i for i in range(column, len(rows)) if rows[i][column]), None
        )
        if pivot_row is None:
            return 0
        if pivot_row != column:
            rows[column], rows[pivot_row] = rows[pivot_row], rows[column]
            result = -result

        pivot = rows[column][column]
        result *= pivot
        for i in range(column + 1, len(rows)):
            factor = rows[i][column] / pivot
            for j in range(column + 1, len(rows)):
                rows[i][j] -= factor * rows[column][j]
            rows[i][column] = 0

    return int(result)


def kirchhoff_count(vertex_count, edges):
    """Count layouts using a cofactor of the unweighted graph Laplacian."""
    laplacian = [[0] * vertex_count for _ in range(vertex_count)]
    for u, v in edges:
        laplacian[u][u] += 1
        laplacian[v][v] += 1
        laplacian[u][v] -= 1
        laplacian[v][u] -= 1

    return determinant([row[:-1] for row in laplacian[:-1]])


def main():
    with open("data/buildings.csv", newline="", encoding="utf-8-sig") as file:
        buildings = [row["building"].strip() for row in csv.DictReader(file)][:8]

    if len(buildings) < 2:
        raise ValueError("Enter at least two buildings in data/buildings.csv.")

    output = Path("outputs")
    output.mkdir(exist_ok=True)
    results_path = output / "task4_results.csv"
    layouts_path = output / "task4_spanning_trees.csv"
    with results_path.open("w", newline="", encoding="utf-8") as results_file, \
         layouts_path.open("w", newline="", encoding="utf-8") as layouts_file:
        results = csv.writer(results_file)
        layouts = csv.writer(layouts_file)
        results.writerow([
            "graph_type", "buildings", "possible_routes", "enumerated_count",
            "kirchhoff_count", "match",
        ])
        layouts.writerow(["graph_type", "buildings", "tree_id", "routes"])

        for n in range(2, len(buildings) + 1):
            complete = list(combinations(range(n), 2))
            # A ring is an illustrative sparse network in CSV building order.
            ring = [(i, i + 1) for i in range(n - 1)]
            if n > 2:
                ring.append((0, n - 1))

            for graph_type, edges in (("complete", complete), ("ring", ring)):
                expected = kirchhoff_count(n, edges)
                count = 0
                for count, tree in enumerate(spanning_trees(n, edges), start=1):
                    routes = [(buildings[u], buildings[v]) for u, v in tree]
                    layouts.writerow([graph_type, n, count, json.dumps(routes)])

                results.writerow([graph_type, n, len(edges), count, expected,
                                  count == expected])
                print(f"{graph_type:8} {n} buildings: {count:,} layouts "
                      f"(Kirchhoff: {expected:,})")
                if count != expected:
                    raise RuntimeError(f"Count mismatch for {graph_type}, n={n}")

    print(f"Counts saved to {results_path}")
    print(f"Every layout saved to {layouts_path}")


if __name__ == "__main__":
    main()