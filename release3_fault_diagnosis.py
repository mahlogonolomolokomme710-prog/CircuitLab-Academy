"""Release 3.7 — Interactive fault diagnosis and troubleshooting laboratory.

Fault injection and comparison are limited to the Studio's ideal DC resistor
and voltage-source solver. A simulated symptom is not a physical measurement.
"""
from __future__ import annotations

from typing import Any, Callable
import math

import pandas as pd
import streamlit as st

FaultSolver = Callable[[list[dict[str, Any]]], dict[str, Any]]


def inject_fault(records: list[dict[str, Any]], reference: str, fault: str,
                 wrong_value_factor: float = 2.0,
                 short_resistance_ohm: float = 1e-3) -> list[dict[str, Any]]:
    """Return a modified copy of a supported R/V network for teaching."""
    if fault not in {"Open component", "Short resistor", "Wrong component value", "Reversed voltage source"}:
        raise ValueError("Choose a supported fault type.")
    changed = [dict(row) for row in records]
    matches = [row for row in changed if str(row.get("Ref", "")) == reference]
    if len(matches) != 1:
        raise ValueError("Select one existing component reference.")
    part = matches[0]
    kind = str(part.get("Type", "")).upper()
    if fault == "Open component":
        changed = [row for row in changed if str(row.get("Ref", "")) != reference]
    elif fault == "Short resistor":
        if kind != "R":
            raise ValueError("A short-circuit fault can only be applied to a resistor in this model.")
        if not math.isfinite(short_resistance_ohm) or short_resistance_ohm <= 0:
            raise ValueError("Short-circuit resistance must be finite and greater than zero.")
        part["Value"] = float(short_resistance_ohm)
    elif fault == "Wrong component value":
        if not math.isfinite(wrong_value_factor) or wrong_value_factor <= 0 or wrong_value_factor == 1:
            raise ValueError("Choose a finite positive multiplier other than 1.")
        part["Value"] = float(part["Value"]) * wrong_value_factor
    elif fault == "Reversed voltage source":
        if kind != "V":
            raise ValueError("Polarity reversal is only supported for an ideal DC voltage source.")
        part["Value"] = -float(part["Value"])
    return changed


def compare_operating_points(reference: dict[str, Any], faulted: dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Compare node voltages and common component operating values."""
    node_rows = []
    for node in sorted(set(reference["node_voltages"]) | set(faulted["node_voltages"])):
        expected = reference["node_voltages"].get(node, float("nan"))
        actual = faulted["node_voltages"].get(node, float("nan"))
        node_rows.append({"Node": node, "Baseline (V)": expected, "Faulted (V)": actual,
                          "Change (V)": actual - expected if math.isfinite(expected) and math.isfinite(actual) else float("nan")})
    base = {row["Reference"]: row for row in reference["components"]}
    altered = {row["Reference"]: row for row in faulted["components"]}
    comp_rows = []
    for ref in sorted(set(base) | set(altered)):
        a, b = base.get(ref), altered.get(ref)
        comp_rows.append({
            "Reference": ref,
            "Status": "Removed (open)" if b is None else ("Added" if a is None else "Present"),
            "Baseline current (A)": a["Current (A)"] if a else float("nan"),
            "Faulted current (A)": b["Current (A)"] if b else float("nan"),
            "Baseline power (W)": a["Power (W)"] if a else float("nan"),
            "Faulted power (W)": b["Power (W)"] if b else float("nan"),
        })
    return {"nodes": pd.DataFrame(node_rows), "components": pd.DataFrame(comp_rows)}


def explain_fault(fault: str, reference: str, component_type: str) -> dict[str, Any]:
    """Provide a concise causal explanation and a safe diagnostic sequence."""
    library = {
        "Open component": (
            "An open component interrupts its branch. Depending on circuit topology, branch current may fall to zero, a node may float, or the solver may be unable to find a unique operating point.",
            ["Power down and isolate the circuit before continuity testing.",
             "Check the component body, solder joints and connectors for an open path.",
             "With power restored only under supervised, current-limited low-voltage conditions, compare node voltages with the schematic.",
             "Replace only after confirming the component specification and the cause of failure."]),
        "Short resistor": (
            "A resistor replaced by a very low resistance can draw excessive current, collapse node voltages or make the ideal solver numerically ill-conditioned.",
            ["Do not reproduce a short fault on a physical supply without an approved current-limited test setup.",
             "Power down and inspect for solder bridges, damaged insulation or a failed component.",
             "Measure resistance only with power removed and stored energy safely discharged.",
             "Check the source current limit and protection before controlled re-energisation."]),
        "Wrong component value": (
            "A value error changes branch current and voltage division. The direction and size of the symptom depend on the component's position in the network.",
            ["Read the component marking and compare it with the bill of materials.",
             "Verify the unit and multiplier (Ω, kΩ, MΩ) and measure out of circuit when appropriate.",
             "Recalculate the expected node voltage and branch current.",
             "Fit the specified value and repeat the controlled measurement."]),
        "Reversed voltage source": (
            "Reversing an ideal DC source changes its signed polarity and can reverse node voltages or oppose another source.",
            ["Power down before changing polarity or wiring.",
             "Check the source positive and negative terminals against the schematic.",
             "Verify instrument lead polarity and reference node.",
             "Re-energise only with a suitable isolated, current-limited low-voltage source."]),
    }
    explanation, steps = library[fault]
    if fault == "Short resistor" and component_type != "R":
        raise ValueError("Short resistor fault requires a resistor.")
    if fault == "Reversed voltage source" and component_type != "V":
        raise ValueError("Reversed source fault requires a voltage source.")
    return {"explanation": explanation, "steps": steps}


def build_fault_report(reference: str, fault: str, explanation: str,
                       comparison: dict[str, pd.DataFrame], solver_error: str = "") -> str:
    lines = ["# CircuitLab Academy — Fault diagnosis exercise", "",
             f"- Component: {reference}", f"- Injected fault: {fault}", "",
             "## Fault mechanism", explanation, "",
             "## Simulation outcome"]
    if solver_error:
        lines.extend(["The faulted network could not be solved by the supported ideal DC solver.",
                      f"Solver message: {solver_error}", ""])
    else:
        lines.extend(["### Node voltage comparison", "",
                      comparison["nodes"].to_markdown(index=False), "",
                      "### Component operating-point comparison", "",
                      comparison["components"].to_markdown(index=False), ""])
    lines.extend(["## Safety and limitations",
                  "This is a simulated teaching fault in an ideal DC network containing only resistors and ideal voltage sources. It is not a physical measurement or a prediction of all real-world fault behaviour. No mains testing is supported. Never deliberately short a live circuit. Use only supervised, isolated, current-limited low-voltage laboratory equipment, and power down before rewiring.", ""])
    return "\n".join(lines)


def render_fault_lab(solver: FaultSolver) -> None:
    st.markdown("### Fault Detective · Release 3.7")
    st.caption("Introduce a controlled virtual fault, compare the ideal DC operating points, then follow a measurement-led troubleshooting sequence.")
    st.warning("Faults are injected into a software copy only. Do not reproduce shorts or other faults on physical circuits. This lab supports the current resistor/ideal-DC-source solver only.")
    network = st.session_state.get("r3_network")
    if network is None or len(network) == 0:
        st.info("Build a circuit in the Interactive Engineering Studio before opening Fault Detective.")
        return
    records = network.to_dict("records") if hasattr(network, "to_dict") else list(network)
    refs = [str(row.get("Ref", "")) for row in records]
    selected = st.selectbox("Component to investigate", refs, key="r37_fault_ref")
    part = next(row for row in records if str(row.get("Ref", "")) == selected)
    kind = str(part.get("Type", "")).upper()
    fault_options = ["Open component", "Wrong component value"]
    if kind == "R":
        fault_options.insert(1, "Short resistor")
    if kind == "V":
        fault_options.append("Reversed voltage source")
    fault = st.selectbox("Virtual fault", fault_options, key="r37_fault_type")
    factor = st.number_input("Incorrect value multiplier", min_value=0.01, max_value=1000.0,
                             value=2.0, key="r37_fault_factor") if fault == "Wrong component value" else 2.0
    short_r = st.number_input("Virtual short resistance (Ω)", min_value=0.000001,
                              max_value=1.0, value=0.001, format="%.6g",
                              key="r37_short_r") if fault == "Short resistor" else 0.001
    if st.button("Inject virtual fault and diagnose", type="primary", key="r37_run_fault"):
        try:
            baseline = solver(records)
            altered_records = inject_fault(records, selected, fault, factor, short_r)
            altered = solver(altered_records)
            comparison = compare_operating_points(baseline, altered)
            diagnosis = explain_fault(fault, selected, kind)
            st.session_state["r37_diagnosis"] = {
                "fault": fault, "reference": selected, "explanation": diagnosis["explanation"],
                "steps": diagnosis["steps"], "comparison": comparison, "solver_error": "",
            }
        except Exception as exc:
            try:
                diagnosis = explain_fault(fault, selected, kind)
                st.session_state["r37_diagnosis"] = {
                    "fault": fault, "reference": selected, "explanation": diagnosis["explanation"],
                    "steps": diagnosis["steps"], "comparison": None, "solver_error": str(exc),
                }
            except Exception as nested:
                st.error(str(nested))
                return
    diagnosis = st.session_state.get("r37_diagnosis")
    if diagnosis:
        st.divider()
        st.markdown("#### Diagnosis")
        st.markdown(f"**{diagnosis['reference']} · {diagnosis['fault']}**")
        st.write(diagnosis["explanation"])
        if diagnosis["solver_error"]:
            st.warning("The altered circuit could not be solved by the current ideal DC model. This itself may indicate a floating, disconnected or mathematically singular network.")
            st.code(diagnosis["solver_error"])
        elif diagnosis["comparison"]:
            st.markdown("**Node voltage changes**")
            st.dataframe(diagnosis["comparison"]["nodes"], use_container_width=True, hide_index=True)
            st.markdown("**Component current and power changes**")
            st.dataframe(diagnosis["comparison"]["components"], use_container_width=True, hide_index=True)
        st.markdown("#### Troubleshooting sequence")
        for index, step in enumerate(diagnosis["steps"], start=1):
            st.markdown(f"{index}. {step}")
        report = build_fault_report(diagnosis["reference"], diagnosis["fault"],
                                    diagnosis["explanation"],
                                    diagnosis["comparison"] or {"nodes": pd.DataFrame(), "components": pd.DataFrame()},
                                    diagnosis["solver_error"])
        st.download_button("Download fault diagnosis report", report,
                           file_name="circuitlab_fault_diagnosis.md", mime="text/markdown")
