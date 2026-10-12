from pathlib import Path
import json
import streamlit as st
import pandas as pd
import networkx as nx
from maxcut_benchmark.graph_builder import parse_edge_list, validate_graph
from maxcut_benchmark.objective import exact_maxcut
from maxcut_benchmark.benchmark import run_one, save_result
from maxcut_benchmark.visualization import graph_figure, comparison_dataframe, comparison_figure

ROOT = Path(__file__).resolve().parent
CONFIGS = ROOT / "configs"
st.set_page_config(page_title="Qiskit O1 Max-Cut Prototype", page_icon="⚛️", layout="wide")
st.title("⚛️ Qiskit Fall Fest 2026 — O1 Max-Cut")
st.caption("Architecture-aware QAOA prototype | Synthetic processor topologies + local simulator")

st.warning("Research prototype only: Processor A/B are synthetic example topologies, not official challenge processors. Results are local simulator outputs, not hardware measurements.")

with st.sidebar:
    st.header("Experiment settings")
    edge_text = st.text_area("Graph edges (u-v, comma-separated)", "0-1, 1-2, 2-3, 3-4, 4-5, 5-0, 0-3, 1-4, 2-5", height=100)
    p = st.slider("QAOA depth p", 1, 3, 1)
    shots = st.select_slider("Measurement shots", options=[256, 512, 1024, 2048, 4096], value=1024)
    maxiter = st.slider("Optimizer iterations", 20, 200, 60, step=10)
    seed = st.number_input("Random seed", min_value=0, max_value=999999, value=42)
    opt_level = st.selectbox("Transpiler optimization level", [0, 1, 2, 3], index=1)
    run_button = st.button("Run A/B benchmark", type="primary", use_container_width=True)

try:
    graph = parse_edge_list(edge_text)
    validate_graph(graph)
    if graph.number_of_nodes() > 8:
        st.info("The sample processor fixtures have 8 qubits. Use graphs with at most 8 vertices for this demo.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Vertices / qubits", graph.number_of_nodes())
    col2.metric("Edges", graph.number_of_edges())
    if graph.number_of_nodes() <= 20:
        opt, bits = exact_maxcut(graph)
        col3.metric("Exact classical optimum", f"{opt:g}")
        st.caption(f"One exact optimum (vertex 0 first): `{bits}`")
    else:
        st.info("Exact optimum disabled for graphs larger than 20 vertices.")
    st.pyplot(graph_figure(graph), use_container_width=True)
except Exception as exc:
    graph = None
    st.error(f"Graph input error: {exc}")

if run_button:
    if graph is None:
        st.error("Fix the graph input before running.")
    elif graph.number_of_nodes() > 8:
        st.error("The current synthetic processor fixtures contain 8 qubits. Reduce the graph to 8 vertices or fewer.")
    else:
        results = []
        progress = st.progress(0, text="Starting benchmark...")
        processor_paths = [CONFIGS / "processor_A.json", CONFIGS / "processor_B.json"]
        try:
            for idx, path in enumerate(processor_paths):
                progress.progress(idx / 2, text=f"Running {path.stem}...")
                result = run_one(graph, path, p=p, shots=shots, maxiter=maxiter, seed=int(seed), optimization_level=opt_level)
                save_result(result, ROOT / "results" / "raw")
                results.append(result)
            progress.progress(1.0, text="Benchmark complete.")
            st.session_state["benchmark_results"] = results
            st.session_state["benchmark_graph_edges"] = edge_text
        except Exception as exc:
            st.exception(exc)
            st.error("Check that dependencies are installed and both processor configuration files are valid.")

results = st.session_state.get("benchmark_results")
if not results:
    raw_a = ROOT / "results" / "raw" / "synthetic_a_result.json"
    raw_b = ROOT / "results" / "raw" / "synthetic_b_result.json"
    if raw_a.exists() and raw_b.exists():
        try:
            with open(raw_a, "r", encoding="utf-8") as f:
                res_a = json.load(f)
            with open(raw_b, "r", encoding="utf-8") as f:
                res_b = json.load(f)
            results = [res_a, res_b]
            st.session_state["benchmark_results"] = results
        except Exception:
            pass

if results:
    st.subheader("Processor A vs Processor B")
    st.caption("Both rows use the same logical graph and experiment settings. Topology fixtures are synthetic; measurements come from the local Aer simulator.")
    df = comparison_dataframe(results)
    st.dataframe(df, use_container_width=True, hide_index=True)
    m1, m2 = st.columns(2)
    with m1:
        st.pyplot(comparison_figure(df, "Expected cut", "Expected Max-Cut value", "Expected cut"), use_container_width=True)
    with m2:
        st.pyplot(comparison_figure(df, "Circuit depth", "Transpiled circuit depth", "Depth"), use_container_width=True)
    m3, m4 = st.columns(2)
    with m3:
        st.pyplot(comparison_figure(df, "Two-qubit gates", "Two-qubit gate count", "Gate count"), use_container_width=True)
    with m4:
        st.pyplot(comparison_figure(df, "Routing overhead proxy", "Routing overhead proxy", "Additional two-qubit gates vs all-to-all"), use_container_width=True)
    st.subheader("Run details")
    for result in results:
        with st.expander(result["processor_label"]):
            st.json({k: v for k, v in result.items() if k != "raw_counts"})
            st.write("Raw measurement counts")
            st.json(result["raw_counts"])
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download comparison CSV", csv, "processor_ab_comparison.csv", "text/csv")
    json_bytes = json.dumps(results, indent=2).encode("utf-8")
    st.download_button("Download full raw results JSON", json_bytes, "processor_ab_results.json", "application/json")
else:
    st.info("Enter a graph and click **Run A/B benchmark**. The first run may take a little while because QAOA parameters are optimized before each processor experiment.")

st.divider()
st.caption("Prototype limitations: synthetic connectivity, local simulation, no hardware calibration/noise model. Verify official Phase 1 rules before interpreting or submitting results.")
