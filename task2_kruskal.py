import csv
import heapq
import math
import os
import platform
import random
import time
from pathlib import Path
from statistics import mean


SIZES = (100, 500, 1000, 5000)
REPEATS = 5
SEED = 10


def read_buildings():
    with open("data/buildings.csv", newline="", encoding="utf-8-sig") as file:
        buildings = [
            (row["building"].strip(), float(row["latitude"]), float(row["longitude"]))
            for row in csv.DictReader(file)
        ]
    if len(buildings) < 2:
        raise ValueError("Enter at least two buildings in data/buildings.csv.")
    return buildings


def distance(a, b):
    lat1, lon1 = math.radians(a[1]), math.radians(a[2])
    lat2, lon2 = math.radians(b[1]), math.radians(b[2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    x = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return 6371000 * 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))


def campus_edges(buildings):
    """Build all possible cable routes in O(n²) time and space."""
    edges = []
    for i in range(len(buildings)):
        for j in range(i + 1, len(buildings)):
            edges.append((distance(buildings[i], buildings[j]), i, j))
    return edges


class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)

        if root_a == root_b:
            return False

        if self.rank[root_a] < self.rank[root_b]:
            self.parent[root_a] = root_b
        elif self.rank[root_a] > self.rank[root_b]:
            self.parent[root_b] = root_a
        else:
            self.parent[root_b] = root_a
            self.rank[root_a] += 1
        return True


# Kruskal takes O(V + E log E) time and O(V + E) space.
def kruskal(vertices, edges):
    sorted_edges = sorted(edges)
    dsu = DSU(vertices)
    mst = []
    total_cost = 0

    for weight, u, v in sorted_edges:
        if dsu.union(u, v):
            mst.append((u, v, weight))
            total_cost += weight
        if len(mst) == vertices - 1:
            break

    if len(mst) != vertices - 1:
        raise ValueError("Graph is disconnected.")
    return mst, total_cost


# Lazy heap Prim takes O(V + E log E) time and O(V + E) space.
def prim(vertices, edges):
    graph = [[] for _ in range(vertices)]
    for weight, u, v in edges:
        graph[u].append((weight, v))
        graph[v].append((weight, u))

    visited = [False] * vertices
    visited[0] = True
    heap = []
    for weight, v in graph[0]:
        heapq.heappush(heap, (weight, 0, v))

    mst = []
    total_cost = 0
    while heap and len(mst) < vertices - 1:
        weight, u, v = heapq.heappop(heap)
        if visited[v]:
            continue

        visited[v] = True
        mst.append((u, v, weight))
        total_cost += weight

        for next_weight, neighbour in graph[v]:
            if not visited[neighbour]:
                heapq.heappush(heap, (next_weight, v, neighbour))

    if len(mst) != vertices - 1:
        raise ValueError("Graph is disconnected.")
    return mst, total_cost


def run_campus(output):
    buildings = read_buildings()
    n = len(buildings)
    edges = campus_edges(buildings)
    kruskal_mst, kruskal_cost = kruskal(n, edges)
    _, prim_cost = prim(n, edges)

    print("\nCAMPUS MST RESULTS")
    print("Number of buildings:", n)
    print("Number of Kruskal edges:", len(kruskal_mst))
    print(f"Kruskal total cost: {kruskal_cost:.2f} metres")
    print(f"Prim total cost: {prim_cost:.2f} metres")

    if not math.isclose(kruskal_cost, prim_cost, rel_tol=1e-9):
        raise RuntimeError("Prim and Kruskal disagree on the campus MST cost.")
    print("Verification: Both algorithms give the same MST cost.")

    prim_csv = output / "mst_edges.csv"
    if prim_csv.exists():
        with prim_csv.open(newline="", encoding="utf-8") as file:
            task1_cost = math.fsum(
                float(row["distance_m"]) for row in csv.DictReader(file)
            )
        print(f"Saved Task 1 cost: {task1_cost:.2f} metres")
        print(f"Difference from Task 2: {abs(task1_cost - kruskal_cost):.2f} metres")

    with (output / "kruskal_mst_edges.csv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["source_building", "destination_building", "distance_m"])
        for u, v, weight in kruskal_mst:
            writer.writerow([buildings[u][0], buildings[v][0], weight])


def random_graph(points, dense=False):
    """Use Euclidean distances on a connected graph of seeded random points."""
    n = len(points)
    # A cyclic band ensures connectivity. The fixed width gives O(n) sparse
    # edges. The growing width gives O(n²) edges in the denser graph.
    width = max(3, n // 40) if dense else 2
    edges = []
    for u, point in enumerate(points):
        for offset in range(1, width + 1):
            v = (u + offset) % n
            edges.append((math.dist(point, points[v]), min(u, v), max(u, v)))
    return edges


def benchmark(n, edges):
    kruskal_times = []
    prim_times = []

    for trial in range(REPEATS):
        algorithms = [(kruskal, kruskal_times), (prim, prim_times)]
        if trial % 2:
            algorithms.reverse()

        costs = []
        for algorithm, timings in algorithms:
            start = time.perf_counter()
            _, cost = algorithm(n, edges)
            timings.append(time.perf_counter() - start)
            costs.append(cost)

        if not math.isclose(*costs, rel_tol=1e-9):
            raise RuntimeError("Prim and Kruskal disagree on a benchmark graph.")

    return mean(kruskal_times), mean(prim_times)


def run_benchmarks(output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    results = []
    for n in SIZES:
        rng = random.Random(SEED)
        points = [(rng.random(), rng.random()) for _ in range(n)]
        for graph_type in ("Sparse", "Dense"):
            edges = random_graph(points, dense=graph_type == "Dense")
            kruskal_s, prim_s = benchmark(n, edges)
            results.append((graph_type, n, len(edges), kruskal_s, prim_s, REPEATS, SEED))
            print(
                f"{graph_type:6} {n:5} vertices, {len(edges):7} edges | "
                f"Kruskal {kruskal_s:.6f} s | Prim {prim_s:.6f} s",
                flush=True,
            )

    with (output / "task2_benchmark.csv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
            "Graph Type", "Vertices", "Edges", "Kruskal Time (seconds)",
            "Prim Time (seconds)", "Repeats", "Seed",
        ])
        writer.writerows(results)

    (output / "task2_benchmark_machine.txt").write_text(
        f"{platform.platform()}\n"
        f"CPU: {platform.processor() or platform.machine()}\n"
        f"Logical CPUs: {os.cpu_count()}\n"
        f"Python: {platform.python_version()}\n",
        encoding="utf-8",
    )

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for axis, graph_type in zip(axes, ("Sparse", "Dense")):
        rows = [row for row in results if row[0] == graph_type]
        for index, name in ((3, "Kruskal"), (4, "Prim")):
            axis.plot(SIZES, [row[index] for row in rows], marker="o", label=name)
        axis.set(
            title=graph_type,
            xlabel="Vertices",
            ylabel="Mean runtime (seconds)",
            xscale="log",
            yscale="log",
            xticks=SIZES,
            xticklabels=SIZES,
        )
        axis.legend()
        axis.grid(alpha=0.25)

    fig.suptitle(f"Minimum spanning tree runtime ({REPEATS} runs per graph)")
    fig.savefig(output / "task2_benchmark.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    output = Path("outputs")
    output.mkdir(exist_ok=True)
    run_campus(output)
    run_benchmarks(output)