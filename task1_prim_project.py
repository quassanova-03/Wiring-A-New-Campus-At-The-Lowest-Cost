import csv
import heapq
import math
from pathlib import Path

import folium


buildings = []
with open("data/buildings.csv", newline="", encoding="utf-8-sig") as file:
    for row in csv.DictReader(file):
        buildings.append((
            row["building"].strip(),
            float(row["latitude"]),
            float(row["longitude"]),
        ))

if len(buildings) < 2:
    raise ValueError("Enter at least two buildings in data/buildings.csv.")


def distance(a, b):
    lat1, lon1 = math.radians(a[1]), math.radians(a[2])
    lat2, lon2 = math.radians(b[1]), math.radians(b[2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    x = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return 6371000 * 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))


# The complete campus graph takes O(n²) time and space to build.
n = len(buildings)
graph = [[] for _ in range(n)]
for i in range(n):
    for j in range(i + 1, n):
        weight = distance(buildings[i], buildings[j])
        graph[i].append((weight, j))
        graph[j].append((weight, i))

# Lazy heap Prim takes O(V + E log E) time and O(V + E) space.
visited = [False] * n
visited[0] = True
heap = []
for weight, neighbour in graph[0]:
    heapq.heappush(heap, (weight, 0, neighbour))

mst = []
total_cost = 0
while heap and len(mst) < n - 1:
    weight, u, v = heapq.heappop(heap)
    if visited[v]:
        continue

    visited[v] = True
    mst.append((u, v, weight))
    total_cost += weight

    for next_weight, neighbour in graph[v]:
        if not visited[neighbour]:
            heapq.heappush(heap, (next_weight, v, neighbour))

if len(mst) != n - 1:
    raise ValueError("The graph is disconnected; an MST could not be formed.")

output = Path("outputs")
output.mkdir(exist_ok=True)
with (output / "mst_edges.csv").open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["source_building", "destination_building", "distance_m"])
    for u, v, weight in mst:
        writer.writerow([buildings[u][0], buildings[v][0], weight])

center = [
    sum(building[1] for building in buildings) / n,
    sum(building[2] for building in buildings) / n,
]
campus_map = folium.Map(location=center, zoom_start=17, tiles=None)
campus_map.get_root().header.add_child(
    folium.Element("<style>.leaflet-container { background: white !important; }</style>")
)

for u, v, weight in mst:
    a, b = buildings[u], buildings[v]
    folium.PolyLine(
        [(a[1], a[2]), (b[1], b[2])],
        color="blue",
        weight=4,
        tooltip=f"{a[0]} to {b[0]}: {weight:.2f} m",
    ).add_to(campus_map)

for name, lat, lon in buildings:
    folium.Marker([lat, lon], tooltip=name).add_to(campus_map)

campus_map.save(str(output / "campus_mst_map.html"))

with (output / "mst_summary.txt").open("w", encoding="utf-8") as file:
    file.write(f"Number of buildings: {n}\n")
    file.write(f"Number of MST cables: {len(mst)}\n")
    file.write(f"Total cable length: {total_cost:.2f} metres\n")

print("Task 1 completed!")
print("Number of buildings:", n)
print("Number of MST cables:", len(mst))
print(f"Total cable length: {total_cost:.2f} metres")
print("Open outputs/campus_mst_map.html to see the campus network.")