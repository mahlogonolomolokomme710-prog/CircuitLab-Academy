"""Release 3.1 — Interactive Engineering Studio.

A transparent, local DC resistive-network editor and modified-nodal-analysis solver.
Supported elements: ideal DC voltage sources (V) and resistors (R).
This is an educational solver, not a SPICE replacement or safety certification.
"""
from __future__ import annotations

import math
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


STARTER = [
    {"Ref": "V1", "Type": "V", "Node1": "N1", "Node2": "0", "Value": 10.0},
    {"Ref": "R1", "Type": "R", "Node1": "N1", "Node2": "N2", "Value": 1000.0},
    {"Ref": "R2", "Type": "R", "Node1": "N2", "Node2": "0", "Value": 1000.0},
]
COLUMNS = ["Ref", "Type", "Node1", "Node2", "Value"]


def _solve_linear(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    """Solve Ax=b using partial-pivot Gaussian elimination."""
    n = len(rhs)
    a = [list(map(float, row)) + [float(rhs[i])] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(a[row][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("The circuit equations are singular. Check for floating nodes, missing ground, or an ideal-source conflict.")
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        for j in range(col, n + 1):
            a[col][j] /= scale
        for row in range(n):
            if row == col:
                continue
            factor = a[row][col]
            if factor:
                for j in range(col, n + 1):
                    a[row][j] -= factor * a[col][j]
    return [a[i][n] for i in range(n)]


def solve_dc_network(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Solve a DC network containing ideal voltage sources and resistors."""
    clean = []
    refs = set()
    nodes = set()
    for raw in records:
        ref = str(raw.get("Ref", "")).strip()
        kind = str(raw.get("Type", "")).strip().upper()
        n1 = str(raw.get("Node1", "")).strip()
        n2 = str(raw.get("Node2", "")).strip()
        try:
            value = float(raw.get("Value"))
        except (TypeError, ValueError):
            raise ValueError(f"{ref or 'A component'} has a non-numeric value.")
        if not ref or not n1 or not n2:
            raise ValueError("Every component needs a reference, Node1 and Node2.")
        if ref in refs:
            raise ValueError(f"Duplicate component reference: {ref}.")
        if kind not in {"R", "V"}:
            raise ValueError(f"{ref}: unsupported type '{kind}'. Use R or V.")
        if n1 == n2:
            raise ValueError(f"{ref}: both terminals use the same node.")
        if not math.isfinite(value):
            raise ValueError(f"{ref}: value must be finite.")
        if kind == "R" and value <= 0:
            raise ValueError(f"{ref}: resistance must be greater than zero.")
        refs.add(ref)
        nodes.update([n1, n2])
        clean.append({"Ref": ref, "Type": kind, "Node1": n1, "Node2": n2, "Value": value})
    if not clean:
        raise ValueError("Add at least one component.")
    if "0" not in nodes:
        raise ValueError("The circuit must include node 0 as ground.")
    sources = [c for c in clean if c["Type"] == "V"]
    if not sources:
        raise ValueError("Add at least one ideal DC voltage source (Type V).")
    non_ground = sorted(nodes - {"0"})
    node_index = {node: i for i, node in enumerate(non_ground)}
    n = len(non_ground)
    m = len(sources)
    size = n + m
    matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    rhs = [0.0 for _ in range(size)]

    def stamp_node(row: int, node: str, value: float) -> None:
        if node != "0":
            matrix[row][node_index[node]] += value

    for comp in clean:
        a, b, value = comp["Node1"], comp["Node2"], comp["Value"]
        if comp["Type"] == "R":
            g = 1.0 / value
            if a != "0":
                ia = node_index[a]
                matrix[ia][ia] += g
            if b != "0":
                ib = node_index[b]
                matrix[ib][ib] += g
            if a != "0" and b != "0":
                ia, ib = node_index[a], node_index[b]
                matrix[ia][ib] -= g
                matrix[ib][ia] -= g

    for k, source in enumerate(sources):
        branch = n + k
        a, b = source["Node1"], source["Node2"]
        if a != "0":
            ia = node_index[a]
            matrix[ia][branch] += 1.0
            matrix[branch][ia] += 1.0
        if b != "0":
            ib = node_index[b]
            matrix[ib][branch] -= 1.0
            matrix[branch][ib] -= 1.0
        rhs[branch] = source["Value"]

    solution = _solve_linear(matrix, rhs)
    voltages = {"0": 0.0}
    voltages.update({node: solution[index] for node, index in node_index.items()})
    source_currents = {source["Ref"]: solution[n + k] for k, source in enumerate(sources)}
    results = []
    for comp in clean:
        va, vb = voltages[comp["Node1"]], voltages[comp["Node2"]]
        if comp["Type"] == "R":
            current = (va - vb) / comp["Value"]
            power = (va - vb) ** 2 / comp["Value"]
        else:
            current = source_currents[comp["Ref"]]
            power = (va - vb) * current
        results.append({
            "Reference": comp["Ref"], "Type": comp["Type"],
            "Node1": comp["Node1"], "Node2": comp["Node2"],
            "Value": comp["Value"], "Voltage (V)": va - vb,
            "Current (A)": current, "Power (W)": power,
        })
    return {"node_voltages": voltages, "components": results, "netlist": clean}


def _draw_network(records: list[dict[str, Any]]) -> plt.Figure:
    nodes = sorted({str(r[k]).strip() for r in records for k in ("Node1", "Node2")})
    if not nodes:
        nodes = ["0"]
    count = len(nodes)
    positions = {}
    for i, node in enumerate(nodes):
        angle = math.pi / 2 - 2 * math.pi * i / max(count, 1)
        positions[node] = (math.cos(angle) * 2.5, math.sin(angle) * 2.5)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor("#0b1724")
    fig.patch.set_facecolor("#0b1724")
    for comp in records:
        a, b = str(comp["Node1"]).strip(), str(comp["Node2"]).strip()
        if a not in positions or b not in positions:
            continue
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1.0
        px, py = -dy / length, dx / length
        ax.plot([x1, x2], [y1, y2], color="#91a9bb", lw=1.8, zorder=1)
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.plot([mx-px*.22, mx+px*.22], [my-py*.22, my+py*.22],
                color="#5ee0d0" if str(comp["Type"]).upper()=="R" else "#f6c66b", lw=5, solid_capstyle="round", zorder=3)
        label = f'{comp["Ref"]} · {comp["Value"]:g} {"Ω" if str(comp["Type"]).upper()=="R" else "V"}'
        ax.text(mx+px*.42, my+py*.42, label, color="#f2f7fb", fontsize=9, ha="center",
                bbox={"boxstyle":"round,pad=0.25","facecolor":"#172b3e","edgecolor":"#35516a","alpha":0.96}, zorder=4)
    for node, (x, y) in positions.items():
        ax.scatter([x], [y], s=180, color="#e8f2f8", edgecolors="#5ee0d0", linewidths=2, zorder=5)
        ax.text(x, y-.32, node + (" · GND" if node=="0" else ""), color="#f2f7fb",
                ha="center", va="top", fontsize=10, weight="bold", zorder=6)
    ax.set_title("Circuit topology view · ideal DC network", color="#f2f7fb", fontsize=14, pad=18)
    ax.axis("off")
    ax.margins(.25)
    fig.tight_layout()
    return fig


def render() -> None:
    st.markdown("""
    <div style="padding:24px 28px;border-radius:18px;background:linear-gradient(115deg,#0b1724,#124b5a);color:#f4fbff;margin-bottom:16px">
      <div style="letter-spacing:.16em;font-size:.72rem;color:#68ded0;font-weight:700">CIRCUITLAB ACADEMY · RELEASE 3.1</div>
      <h1 style="color:#f4fbff;margin:.35rem 0">Interactive Engineering Studio</h1>
      <p style="color:#c9dbe6;margin:0">Construct a DC network, inspect its topology, solve node voltages and examine component currents and power.</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("This first Studio increment is a structured circuit editor and transparent DC solver. It is not yet a drag-and-drop schematic canvas or a SPICE engine. Supported components are ideal DC voltage sources and resistors.")
    if "r3_network" not in st.session_state:
        st.session_state.r3_network = pd.DataFrame(STARTER, columns=COLUMNS)
    left, right = st.columns([1.15, .85])
    with left:
        st.subheader("1 · Build your circuit")
        st.caption("Use node 0 as ground. Each component connects Node1 to Node2. Type R = resistor; Type V = ideal DC voltage source.")
        edited = st.data_editor(
            st.session_state.r3_network,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ref": st.column_config.TextColumn("Reference", help="Unique label, e.g. R1 or V1"),
                "Type": st.column_config.SelectboxColumn("Type", options=["R", "V"], help="R = resistor; V = ideal DC voltage source"),
                "Node1": st.column_config.TextColumn("Positive / first node"),
                "Node2": st.column_config.TextColumn("Negative / second node"),
                "Value": st.column_config.NumberColumn("Value", min_value=0.000000001, format="%.6g"),
            },
            key="r3_network_editor",
        )
        st.session_state.r3_network = edited
        c1, c2 = st.columns(2)
        if c1.button("Load example voltage divider", key="r3_example"):
            st.session_state.r3_network = pd.DataFrame(STARTER, columns=COLUMNS)
            st.session_state.pop("r3_network_editor", None)
            st.session_state.pop("r3_result", None)
            st.session_state.pop("r3_error", None)
            st.rerun()
        if c2.button("Clear circuit", key="r3_clear"):
            st.session_state.r3_network = pd.DataFrame(columns=COLUMNS)
            st.session_state.pop("r3_network_editor", None)
            st.session_state.pop("r3_result", None)
            st.session_state.pop("r3_error", None)
            st.rerun()
        st.subheader("2 · Circuit topology")
        fig = _draw_network(edited.to_dict("records"))
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    with right:
        st.subheader("3 · Solve the DC network")
        st.write("The solver uses modified nodal analysis (MNA). Voltage-source current is an additional unknown; resistor conductance is stamped into the nodal matrix.")
        if st.button("Analyse circuit", type="primary", use_container_width=True, key="r3_solve"):
            try:
                result = solve_dc_network(edited.to_dict("records"))
                st.session_state.r3_result = result
                st.session_state.r3_error = ""
            except Exception as exc:
                st.session_state.r3_result = None
                st.session_state.r3_error = str(exc)
        if st.session_state.get("r3_error"):
            st.error(st.session_state.r3_error)
        result = st.session_state.get("r3_result")
        if result:
            st.success("DC operating point calculated.")
            st.markdown("**Node voltages**")
            st.dataframe(pd.DataFrame([{"Node": k, "Voltage (V)": v} for k, v in result["node_voltages"].items()]),
                         use_container_width=True, hide_index=True)
            st.markdown("**Component operating values**")
            st.dataframe(pd.DataFrame(result["components"]), use_container_width=True, hide_index=True)
            st.caption("Current reference is Node1 → Node2. Positive power means absorbed power; negative power means supplied power.")
            st.download_button("Download SPICE-style netlist", _to_netlist(result["netlist"]),
                               file_name="circuitlab_design.cir", mime="text/plain")
            st.download_button("Download operating-point report", _to_report(result),
                               file_name="circuitlab_dc_analysis.md", mime="text/markdown")
        else:
            st.caption("Run the analysis to calculate the node voltages, branch currents and component power.")
    st.divider()
    st.subheader("4 · Measurement probe")
    result = st.session_state.get("r3_result")
    if result:
        node_names = list(result["node_voltages"])
        a, b = st.columns(2)
        n1 = a.selectbox("Probe positive node", node_names, key="r3_probe_a")
        n2 = b.selectbox("Probe reference node", node_names, index=node_names.index("0"), key="r3_probe_b")
        measured = result["node_voltages"][n1] - result["node_voltages"][n2]
        st.metric(f"Voltage · {n1} relative to {n2}", f"{measured:.6g} V")
    st.caption("Calculated values are ideal-model results. Real components have tolerances, parasitics, temperature effects and power limits. Verify exact datasheets and laboratory requirements before any physical construction.")


def _to_netlist(records: list[dict[str, Any]]) -> str:
    lines = ["* CircuitLab Academy Release 3.1 — ideal DC resistor/source network"]
    for c in records:
        lines.append(f'{c["Ref"]} {c["Node1"]} {c["Node2"]} {c["Value"]:.12g}')
    lines.append(".op")
    lines.append(".end")
    return "\n".join(lines) + "\n"


def _to_report(result: dict[str, Any]) -> str:
    lines = ["# CircuitLab Academy — DC operating-point report", "",
             "**Method:** Modified nodal analysis (ideal DC sources and resistors only).", "",
             "## Node voltages"]
    lines.extend(f'- {node}: {voltage:.8g} V' for node, voltage in result["node_voltages"].items())
    lines.extend(["", "## Component values", "",
                  "| Ref | Type | Nodes | Value | Voltage (V) | Current (A) | Power (W) |",
                  "|---|---|---|---:|---:|---:|---:|"])
    for c in result["components"]:
        lines.append(f'| {c["Reference"]} | {c["Type"]} | {c["Node1"]}–{c["Node2"]} | {c["Value"]:.8g} | {c["Voltage (V)"]:.8g} | {c["Current (A)"]:.8g} | {c["Power (W)"]:.8g} |')
    lines.extend(["", "## Limitations", "",
                  "Ideal DC model; excludes capacitor/inductor dynamics, AC/transient analysis, semiconductor models, parasitics, thermal effects and physical safety validation.", ""])
    return "\n".join(lines)
