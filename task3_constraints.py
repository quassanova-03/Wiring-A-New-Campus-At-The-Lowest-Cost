"""Measure the extra cable length for individual and combined wiring rules."""

import csv
import math
from pathlib import Path

from task2_kruskal import DSU, campus_edges, kruskal, read_buildings


# Hypothetical campus rules for the assignment.
MANDATORY_EDGE = ("Nandan Nilekani Main Building", "Central Library")
FORBIDDEN_EDGE = ("Nandan Nilekani Main Building", "Convocation Hall")
MAX_DEGREE = 3


def constrained_tree(n, edges, mandatory=None, forbidden=None, max_degree=None):
    """Apply Kruskal's rule with optional route and degree restrictions.

    Edges are already sorted. This takes O(V + E α(V)) time and O(V) space.
    With a degree cap, a greedy run can fail or return a nonoptimal tree.
    """
    dsu = DSU(n)
    degree = [0] * n
    tree = []

    if mandatory is not None:
        weight, u, v = mandatory
        dsu.union(u, v)
        degree[u] += 1
        degree[v] += 1
        tree.append((u, v, weight))

    for weight, u, v in edges:
        if len(tree) == n - 1:
            break
        if (u, v) == forbidden:
            continue
        if max_degree is not None and max(degree[u], degree[v]) >= max_degree:
            continue
        if dsu.union(u, v):
            degree[u] += 1
            degree[v] += 1
            tree.append((u, v, weight))

    return tree if len(tree) == n - 1 else None


def get_route(names, name_to_index):
    try:
        return tuple(sorted(name_to_index[name] for name in names))
    except KeyError as error:
        raise ValueError(
            f"Unknown building {error.args[0]!r}. Set the route names "
            "at the top of task3_constraints.py for your campus."
        ) from error


def main():
    buildings = read_buildings()
    n = len(buildings)
    names = [building[0] for building in buildings]
    if len(set(names)) != n:
        raise ValueError("Building names must be unique.")

    name_to_index = {name: i for i, name in enumerate(names)}
    mandatory = get_route(MANDATORY_EDGE, name_to_index)
    forbidden = get_route(FORBIDDEN_EDGE, name_to_index)
    if mandatory[0] == mandatory[1] or forbidden[0] == forbidden[1]:
        raise ValueError("Each route must connect two different buildings.")
    if mandatory == forbidden:
        raise ValueError("The same cable cannot be both mandatory and forbidden.")

    edges = sorted(campus_edges(buildings))
    mandatory_edge = next(edge for edge in edges if edge[1:] == mandatory)
    baseline, _ = kruskal(n, edges)
    baseline_cost = math.fsum(w for _, _, w in baseline)

    cases = {
        "Unrestricted MST": baseline,
        "Mandatory cable": constrained_tree(n, edges, mandatory=mandatory_edge),
        "Forbidden cable": constrained_tree(n, edges, forbidden=forbidden),
        "Degree limit": constrained_tree(n, edges, max_degree=MAX_DEGREE),
        "All three rules": constrained_tree(
            n, edges, mandatory_edge, forbidden, MAX_DEGREE
        ),
    }

    output = Path("outputs")
    output.mkdir(exist_ok=True)
    summary = [
        f"Mandatory cable: {' to '.join(MANDATORY_EDGE)}",
        f"Forbidden cable: {' to '.join(FORBIDDEN_EDGE)}",
        f"Maximum degree: {MAX_DEGREE}",
        "",
    ]

    with (output / "task3_costs.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["scenario", "status", "cables", "total_length_m", "extra_length_m"])
        for label, tree in cases.items():
            if tree is None:
                writer.writerow([label, "No tree found by greedy scan", "", "", ""])
                summary.append(f"{label}: no tree found by greedy scan")
                continue

            cost = math.fsum(w for _, _, w in tree)
            extra = cost - baseline_cost
            writer.writerow([label, "Tree found", len(tree), f"{cost:.2f}", f"{extra:.2f}"])
            summary.append(f"{label}: {cost:.2f} m ({extra:+.2f} m vs. baseline)")

    with (output / "task3_constrained_edges.csv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["source_building", "destination_building", "distance_m"])
        for u, v, weight in cases["All three rules"] or []:
            writer.writerow([names[u], names[v], weight])

    (output / "task3_summary.txt").write_text(
        "\n".join(summary) + "\n", encoding="utf-8"
    )
    print("\n".join(summary))


if __name__ == "__main__":
    main()