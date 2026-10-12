# Qiskit Fall Fest 2026 — O1 Max-Cut Prototype

An interactive Streamlit prototype for QAOA-based Max-Cut and architecture-aware Processor A/B comparisons.

> **Prototype status:** Processor A and B are synthetic example topologies, not official Qiskit Fall Fest processor definitions. Results from the local simulator are simulation results, not quantum-hardware measurements. Replace the example topology files with official Challenge Kit specifications before submitting benchmark claims.

## Features
- Interactive graph input (edge list) and graph visualization
- QAOA circuit with a configurable depth `p`
- Classical exact baseline for small graphs
- Local statevector optimization and shot-based Aer sampling
- Transpilation against two synthetic coupling maps
- Depth, gate counts, two-qubit counts, routing-overhead proxy, cut quality, approximation ratio
- CSV/JSON output and comparison charts
- Explicit labels for synthetic configurations and simulator data

## Setup (Python 3.11 recommended)

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
streamlit run app.py
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.\.venv\Scripts\streamlit.exe run app.py`.

## Run tests

```bash
python -m pytest -q
```

## Run the benchmark from the command line

```bash
python scripts/run_benchmark.py --graph "0-1,1-2,2-3,3-4,4-5,5-0,0-3,1-4,2-5" --p 1 --shots 1024
```

Outputs are written under `results/`. The CLI run uses the same synthetic processor configurations as the dashboard.

## Graph input format

Enter comma-separated edges such as:

```text
0-1, 1-2, 2-3, 3-4, 4-5, 5-0, 0-3, 1-4, 2-5
```

Weighted edges are supported in the Python API using `(u, v, weight)` tuples, though the first dashboard version accepts unweighted edges.

## Scientific caveats
- The example Processor A is a linear chain; Processor B is a ring-like topology. These are **synthetic teaching fixtures**, not official processor properties.
- Statevector simulation is used to evaluate the QAOA objective during classical parameter optimization. Final measurement sampling uses Qiskit Aer.
- “Routing overhead proxy” is derived from the two-qubit gate-count difference between constrained-topology and all-to-all transpilation. It is not a guaranteed count of inserted SWAP gates. Exact routing-SWAP reporting depends on transpiler version and stage configuration.
- Exact Max-Cut enumeration is only used for small graphs (up to 20 vertices by default).
- This is a prototype, not a claim of challenge compliance. Confirm all metrics, processor definitions, allowed simulators, and submission constraints against the official Challenge Kit.
