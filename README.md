# Graph Algorithms Project 06
## Wiring a New Campus at the Lowest Cost

## About the Project

The goal is to connect all the buildings on a campus using as little cable as possible. We use **36 buildings at IIT Bombay** as our campus dataset.

Each building is a vertex, and each pair of buildings represents a possible cable route. The weight of each edge is the Haversine distance between the two buildings in metres. We assume cable cost is proportional to this distance.

## Tasks

### 1. Prim's Algorithm

- Build the weighted graph from the building coordinates.
- Use a min-heap to find the minimum spanning tree (MST).
- Draw the selected cable routes on an interactive campus map.

### 2. Kruskal's Algorithm

- Find the MST using Kruskal's algorithm and union–find.
- Compare the total cable length with Prim's result.
- Time both algorithms on sparse and dense random graphs. The current benchmark uses **100 vertices** for each graph type.

### 3. Network Constraints

- Include a mandatory cable, exclude a forbidden cable, and limit each building to three connections.
- Apply all three rules together using a greedy approach.
- Compare the resulting cable length with the unrestricted MST.

### 4. Spanning Tree Enumeration

- Generate and count all spanning trees on complete and ring graphs with **2–8 vertices**.
- Verify the counts using Kirchhoff's Matrix–Tree Theorem.
- Save both the count comparison and the full list of layouts.

## Technologies Used

| Tool | Purpose |
|---|---|
| Python | Graph construction and algorithms |
| `heapq` | Min-heap for Prim's algorithm |
| `fractions.Fraction` | Exact arithmetic for the determinant in Task 4 |
| Folium | Interactive campus map |
| CSV | Building coordinates and tabular outputs |

## Project Structure

```text
├── data/
│   ├── buildings.csv           # IIT Bombay coordinates used by Tasks 1–4
│   ├── buildings_template.csv  # CSV header for a new dataset
│   └── demo_buildings.csv       # Synthetic data for the separate walkthrough
├── .gitignore
├── README.md
├── requirements.txt
├── task1_prim_project.py       # Prim's MST and campus map
├── task2_kruskal.py            # Kruskal's MST and timing comparison
├── task3_constraints.py        # Greedy layout with cable constraints
└── task4_spanning_trees.py     # Enumeration and Kirchhoff verification
```

## Input Data

[`data/buildings.csv`](data/buildings.csv) contains the names and coordinates of **36 buildings at IIT Bombay**. The coordinates were calculated from mapped building footprints inside the [IIT Bombay campus boundary](https://www.openstreetmap.org/relation/8546708). Data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).

```csv
building,latitude,longitude
Nandan Nilekani Main Building,19.1329094,72.9152559
Central Library,19.1340744,72.9151056
```

[`data/demo_buildings.csv`](data/demo_buildings.csv) contains the synthetic coordinates used for the separate Prim and Kruskal walkthrough. The four Python scripts use `data/buildings.csv`.

## How to Run

Run these commands from the repository folder. Create `outputs/` before running Task 1 on a fresh checkout.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
New-Item -ItemType Directory -Force outputs | Out-Null

.\.venv\Scripts\python.exe task1_prim_project.py
.\.venv\Scripts\python.exe task2_kruskal.py
.\.venv\Scripts\python.exe task3_constraints.py
.\.venv\Scripts\python.exe task4_spanning_trees.py
```

### macOS, Linux, or WSL

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
mkdir -p outputs

./.venv/bin/python task1_prim_project.py
./.venv/bin/python task2_kruskal.py
./.venv/bin/python task3_constraints.py
./.venv/bin/python task4_spanning_trees.py
```

## Output Files

The scripts generate these files in `outputs/`. Open `outputs/campus_mst_map.html` in a browser to view the campus network.

| Task | File | Contents |
|---|---|---|
| 1 | `campus_mst_map.html` | Interactive map of the MST |
| 1 | `mst_edges.csv` | Cable routes selected by Prim |
| 1 | `mst_summary.txt` | Building count, cable count, and total length |
| 2 | `kruskal_mst_edges.csv` | Cable routes selected by Kruskal |
| 2 | `task2_benchmark.csv` | Prim and Kruskal timings |
| 3 | `task3_constrained_edges.csv` | Cable routes selected with all three constraints |
| 3 | `task3_summary.txt` | Baseline length, constrained length, and extra cable required |
| 4 | `task4_results.csv` | Enumeration and Kirchhoff counts by graph type and size |
| 4 | `task4_spanning_trees.csv` | One row per spanning tree, including its cable routes |

## Results

- **Task 1:** Prim connected **36 buildings** using **35 cables**, with a total cable length of **3,319.18 m**.
- **Task 2:** Kruskal produced the same total MST length as Prim.
- **Task 3:** The greedy layout with all three constraints used **3,321.87 m** of cable. The script reports **2.68 m** of extra cable, calculated before rounding the displayed totals.
- **Task 4:** Enumeration and Kirchhoff's theorem agreed in all **14 cases**. With eight buildings, the complete graph had **262,144** spanning trees and the ring had **8**.

## Conclusion

Prim and Kruskal found the same minimum cable length for the IIT Bombay dataset. The constrained run shows how adding wiring rules can increase the amount of cable needed. The spanning tree counts show how much the number of possible layouts can change when more routes are available between the same buildings.
