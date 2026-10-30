"""Release 3 — Interactive Engineering Studio.

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
from urllib.parse import quote


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



def build_circuitjs_text(records: list[dict[str, Any]]) -> str:
    """Create a CircuitJS text circuit for the supported R/V subset."""
    clean = []
    nodes = sorted({str(row[k]).strip() for row in records for k in ("Node1", "Node2")})
    if not records:
        raise ValueError("Add components before exporting a simulator circuit.")
    if "0" not in nodes:
        raise ValueError("Node 0 must be present as ground before exporting.")
    # Place nodes around a roomy circle; shared coordinates create electrical connections.
    coords = {}
    radius = max(128, 48 * len(nodes))
    for index, node in enumerate(nodes):
        angle = math.pi / 2 - 2 * math.pi * index / max(1, len(nodes))
        coords[node] = (int(round(320 + radius * math.cos(angle) / 16) * 16),
                        int(round(240 + radius * math.sin(angle) / 16) * 16))
    lines = ["$ 1 5.0E-6 10.20027730826997 50 5.0 50"]
    for row in records:
        ref = str(row["Ref"]).strip()
        kind = str(row["Type"]).strip().upper()
        a, b = str(row["Node1"]).strip(), str(row["Node2"]).strip()
        value = float(row["Value"])
        x1, y1 = coords[a]
        x2, y2 = coords[b]
        if kind == "R":
            lines.append(f"r {x1} {y1} {x2} {y2} 0 {value:.12g}")
        elif kind == "V":
            lines.append(f"v {x1} {y1} {x2} {y2} 0 0 40 {value:.12g} 0 0 0.5")
        else:
            raise ValueError(f"{ref}: CircuitJS export currently supports only R and V components.")
    gx, gy = coords["0"]
    lines.append(f"g {gx} {gy} {gx} {gy + 32} 0")
    return "\n".join(lines) + "\n"


def build_circuitjs_url(records: list[dict[str, Any]]) -> str:
    circuit = build_circuitjs_text(records)
    return "https://www.falstad.com/circuit/circuitjs.html?cct=" + quote(circuit, safe="")

def _draw_network(records: list[dict[str, Any]]) -> plt.Figure:
    """Draw a simplified schematic with conventional resistor and source marks."""
    nodes = sorted({str(r[k]).strip() for r in records for k in ("Node1", "Node2")})
    if not nodes:
        nodes = ["0"]
    count = len(nodes)
    radius = max(2.2, 0.8 * count)
    positions = {}
    for i, node in enumerate(nodes):
        angle = math.pi / 2 - 2 * math.pi * i / max(count, 1)
        positions[node] = (radius * math.cos(angle), radius * math.sin(angle))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor("#0b1724")
    fig.patch.set_facecolor("#0b1724")
    for comp in records:
        a, b = str(comp["Node1"]).strip(), str(comp["Node2"]).strip()
        if a not in positions or b not in positions:
            continue
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        dx, dy = x2-x1, y2-y1
        length = math.hypot(dx, dy) or 1.0
        ux, uy = dx/length, dy/length
        px, py = -uy, ux
        mx, my = (x1+x2)/2, (y1+y2)/2
        # Wires from terminals to a compact component symbol.
        half = min(.38, length*.22)
        ax.plot([x1, mx-ux*half], [y1, my-uy*half], color="#91a9bb", lw=1.8, zorder=1)
        ax.plot([mx+ux*half, x2], [my+uy*half, y2], color="#91a9bb", lw=1.8, zorder=1)
        kind = str(comp["Type"]).upper()
        if kind == "R":
            zig = [(-1,0),(-.72,.16),(-.48,-.16),(-.24,.16),(0,-.16),(.24,.16),(.48,-.16),(.72,.16),(1,0)]
            xs = [mx + ux*t*half + px*v*half for t,v in zig]
            ys = [my + uy*t*half + py*v*half for t,v in zig]
            ax.plot(xs, ys, color="#5ee0d0", lw=3.0, solid_capstyle="round", zorder=3)
            unit = "Ω"
        else:
            ax.plot([mx-px*.24, mx+px*.24], [my-py*.24, my+py*.24],
                    color="#f6c66b", lw=4.0, zorder=3)
            ax.plot([mx-ux*.12-px*.34, mx-ux*.12+px*.34],
                    [my-uy*.12-py*.34, my-uy*.12+py*.34], color="#f6c66b", lw=2.2, zorder=3)
            unit = "V"
        ax.text(mx+px*.52, my+py*.52, f'{comp["Ref"]} · {float(comp["Value"]):g} {unit}',
                color="#f2f7fb", fontsize=9, ha="center",
                bbox={"boxstyle":"round,pad=0.25","facecolor":"#172b3e","edgecolor":"#35516a","alpha":.96}, zorder=4)
    for node, (x, y) in positions.items():
        ax.scatter([x], [y], s=155, color="#e8f2f8", edgecolors="#5ee0d0", linewidths=2, zorder=5)
        ax.text(x, y-.24, node + (" · GND" if node=="0" else ""), color="#f2f7fb",
                ha="center", va="top", fontsize=9, weight="bold", zorder=6)
    ax.set_title("Schematic view · node-based DC circuit", color="#f2f7fb", fontsize=14, pad=18)
    ax.axis("off")
    ax.margins(.3)
    fig.tight_layout()
    return fig

def render() -> None:
    st.markdown("""
    <div style="padding:24px 28px;border-radius:18px;background:linear-gradient(115deg,#0b1724,#124b5a);color:#f4fbff;margin-bottom:16px">
      <div style="letter-spacing:.16em;font-size:.72rem;color:#68ded0;font-weight:700">CIRCUITLAB ACADEMY · RELEASE 3.2</div>
      <h1 style="color:#f4fbff;margin:.35rem 0">Interactive Engineering Studio</h1>
      <p style="color:#c9dbe6;margin:0">Construct a DC network, inspect its topology, solve node voltages and examine component currents and power.</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("Release 3.2 adds a component palette, a more schematic-like topology view, and export/preview in the existing CircuitJS engine. The local MNA solver still supports ideal DC voltage sources and resistors only.")
    if "r3_network" not in st.session_state:
        st.session_state.r3_network = pd.DataFrame(STARTER, columns=COLUMNS)
    if "r3_editor_version" not in st.session_state:
        st.session_state.r3_editor_version = 0
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
            key=f"r3_network_editor_{st.session_state.r3_editor_version}",
        )
        st.session_state.r3_network = edited
        with st.expander("Component palette · add a part without editing the table", expanded=False):
            with st.form("r3_component_palette"):
                p1, p2, p3 = st.columns(3)
                new_type = p1.selectbox("Component", ["R", "V"], format_func=lambda x: "Resistor" if x=="R" else "DC voltage source")
                new_ref = p2.text_input("Reference", value="R3" if new_type=="R" else "V2")
                new_value = p3.number_input("Value", min_value=0.000001, value=1000.0 if new_type=="R" else 5.0, format="%.6g")
                node_options = sorted({str(v).strip() for _, row in edited.iterrows() for v in (row.get("Node1"), row.get("Node2")) if str(v).strip()})
                if "0" not in node_options:
                    node_options = ["0"] + node_options
                p4, p5 = st.columns(2)
                new_n1 = p4.selectbox("First terminal", node_options, index=1 if len(node_options)>1 else 0)
                new_n2 = p5.selectbox("Second terminal", node_options, index=0)
                add_part = st.form_submit_button("Add component")
            if add_part:
                if not new_ref.strip() or new_ref.strip() in edited["Ref"].astype(str).tolist():
                    st.error("Enter a unique component reference.")
                elif new_n1 == new_n2:
                    st.error("Choose two different terminal nodes.")
                else:
                    appended = pd.concat([edited, pd.DataFrame([{"Ref":new_ref.strip(),"Type":new_type,"Node1":new_n1,"Node2":new_n2,"Value":new_value}])], ignore_index=True)
                    st.session_state.r3_network = appended
                    st.session_state.r3_editor_version += 1
                    st.session_state.pop("r3_result", None)
                    st.rerun()
        c1, c2 = st.columns(2)
        if c1.button("Load example voltage divider", key="r3_example"):
            st.session_state.r3_network = pd.DataFrame(STARTER, columns=COLUMNS)
            st.session_state.r3_editor_version += 1
            st.session_state.pop("r3_result", None)
            st.session_state.pop("r3_error", None)
            st.rerun()
        if c2.button("Clear circuit", key="r3_clear"):
            st.session_state.r3_network = pd.DataFrame(columns=COLUMNS)
            st.session_state.r3_editor_version += 1
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
            circuitjs_text = build_circuitjs_text(result["netlist"])
            st.download_button("Download CircuitJS circuit", circuitjs_text,
                               file_name="circuitlab_design.txt", mime="text/plain")
            with st.expander("Open this design in the CircuitJS simulator", expanded=False):
                st.caption("The design is translated into CircuitJS text format for the supported resistor and ideal DC-source components. Confirm the simulator rendering and values independently.")
                st.iframe(build_circuitjs_url(result["netlist"]), height=620)
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

    st.divider()
    st.markdown("## Release 3.3 · Dynamic circuit laboratory")
    from release3_transient import render_transient_lab
    render_transient_lab()

    st.divider()
    st.markdown("## Release 3.4 · Semiconductor and rectifier laboratory")
    from release3_semiconductors import render_component_lab
    render_component_lab()

    st.divider()
    st.markdown("## Release 3.5 · Advanced power-supply design studio")
    from release3_power_supply import render_power_supply_studio
    render_power_supply_studio()

    st.divider()
    st.markdown("## Release 3.6 · Intelligent circuit design validation")
    from release3_validation import render_design_validator
    render_design_validator()

    st.divider()
    st.markdown("## Release 3.7 · Fault Detective")
    from release3_fault_diagnosis import render_fault_lab
    render_fault_lab(solve_dc_network)

    st.divider()
    st.markdown("## Release 3.8 · Engineering Project Factory")
    from release3_project_factory import render_project_factory
    render_project_factory()

    st.divider()
    st.markdown("## Release 3.9 · AI Project Tutor and Design Reviewer")
    from release3_tutor import render_project_tutor
    render_project_tutor()

    st.divider()
    st.markdown("## Release 4.0 · Electronics University")
    from release4_university import render_university_hub
    render_university_hub()

    st.divider()
    st.markdown("## Release 4.1 · Interactive Electronics Classroom")
    from release4_classroom import render_interactive_classroom
    render_interactive_classroom()

    st.divider()
    st.markdown("## Release 4.2 · Engineering Assessment Centre")
    from release4_assessment import render_assessment_and_labs
    render_assessment_and_labs()

    st.divider()
    st.markdown("## Release 4.3 · Visual Electronics Learning Engine")
    from release4_visual_engine import render_visual_learning_engine
    render_visual_learning_engine()


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
