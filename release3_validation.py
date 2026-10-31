"""Release 3.6 — deterministic circuit design validation.

Rule-based checks for the supported resistor/DC-source network and the
first-pass Release 3.5 power-supply estimate. Findings are screening guidance,
not proof of safety, standards compliance, or construction readiness.
"""
from __future__ import annotations

import math
from typing import Any

import pandas as pd
import streamlit as st

RATING_COLUMNS = ["Ref", "Max voltage (V)", "Max current (A)", "Max power (W)"]


def validate_netlist(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Check basic structural integrity of the Studio's R/V node network."""
    findings: list[dict[str, str]] = []

    def add(level: str, code: str, message: str, detail: str) -> None:
        findings.append({"level": level, "code": code, "message": message, "detail": detail})

    if not records:
        add("error", "EMPTY", "No components found", "Add at least one supported component before analysis.")
        return findings

    refs: set[str] = set()
    nodes: set[str] = set()
    adjacency: dict[str, set[str]] = {}
    valid_edges: list[tuple[str, str]] = []
    source_count = 0
    resistor_count = 0

    for index, row in enumerate(records, start=1):
        ref = str(row.get("Ref", "")).strip()
        kind = str(row.get("Type", "")).strip().upper()
        n1 = str(row.get("Node1", "")).strip()
        n2 = str(row.get("Node2", "")).strip()
        try:
            value = float(row.get("Value"))
        except (TypeError, ValueError):
            add("error", "NON_NUMERIC", f"{ref or 'Row ' + str(index)} has a non-numeric value",
                "Enter a finite numeric component value.")
            continue
        if not ref:
            add("error", "MISSING_REF", f"Row {index} has no reference", "Give every component a unique label such as R1 or V1.")
        elif ref in refs:
            add("error", "DUPLICATE_REF", f"Duplicate reference {ref}", "Every component reference must be unique.")
        refs.add(ref)
        if not n1 or not n2:
            add("error", "MISSING_NODE", f"{ref or 'A component'} has a missing terminal node",
                "Specify both Node1 and Node2.")
            continue
        if n1 == n2:
            add("error", "SAME_NODE", f"{ref or 'A component'} connects a node to itself",
                "Use two distinct nodes for a two-terminal component.")
            continue
        if kind not in {"R", "V"}:
            add("error", "UNSUPPORTED_TYPE", f"{ref or 'A component'} uses unsupported type {kind!r}",
                "The current local DC solver supports resistors (R) and ideal DC voltage sources (V) only.")
            continue
        if not math.isfinite(value):
            add("error", "NON_FINITE", f"{ref} has a non-finite value", "Use a finite value.")
            continue
        if kind == "R":
            resistor_count += 1
            if value <= 0:
                add("error", "INVALID_RESISTANCE", f"{ref} has non-positive resistance",
                    "A resistor value must be greater than zero ohms.")
        else:
            source_count += 1
            if value == 0:
                add("warning", "ZERO_VOLTAGE_SOURCE", f"{ref} is a zero-volt ideal source",
                    "Confirm that this element is intentional; it may act as an ideal short constraint.")
        nodes.update((n1, n2))
        adjacency.setdefault(n1, set()).add(n2)
        adjacency.setdefault(n2, set()).add(n1)
        valid_edges.append((n1, n2))

    if "0" not in nodes:
        add("error", "NO_GROUND", "Ground node 0 is missing",
            "The current DC solver and CircuitJS export expect an explicit node named 0.")
    else:
        reached = {"0"}
        stack = ["0"]
        while stack:
            current = stack.pop()
            for neighbour in adjacency.get(current, set()):
                if neighbour not in reached:
                    reached.add(neighbour)
                    stack.append(neighbour)
        floating = sorted(nodes - reached)
        if floating:
            add("error", "FLOATING_NODES", "One or more nodes are disconnected from ground",
                "Floating/disconnected nodes: " + ", ".join(floating) + ". Check wiring and the reference node.")

    if resistor_count == 0:
        add("warning", "NO_RESISTORS", "No resistors are present",
            "A source-only network may not represent a useful loaded circuit.")
    if source_count == 0:
        add("warning", "NO_SOURCES", "No independent DC voltage source is present",
            "Check whether the network has an intended excitation.")
    if not any(f["level"] == "error" for f in findings):
        add("pass", "STRUCTURE_OK", "No structural errors detected",
            "Basic references, supported element types and ground connectivity passed these screening checks.")
    return findings


def validate_component_ratings(
    solved_components: list[dict[str, Any]],
    ratings: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Compare solved absolute V/I/P against user-entered maximum ratings."""
    by_ref = {str(row.get("Ref", "")).strip(): row for row in ratings if str(row.get("Ref", "")).strip()}
    findings: list[dict[str, str]] = []
    for component in solved_components:
        ref = str(component.get("Reference", "")).strip()
        rating = by_ref.get(ref)
        if not rating or all(
            rating.get(field) is None or pd.isna(rating.get(field)) or rating.get(field) == ""
            for field in ("Max voltage (V)", "Max current (A)", "Max power (W)")
        ):
            findings.append({"level": "info", "code": "RATING_MISSING",
                             "message": f"{ref}: component ratings not supplied",
                             "detail": "Enter datasheet maximum voltage, current and power where applicable; no rating compliance conclusion is possible."})
            continue
        actuals = {
            "Max voltage (V)": abs(float(component.get("Voltage (V)", 0.0))),
            "Max current (A)": abs(float(component.get("Current (A)", 0.0))),
            "Max power (W)": abs(float(component.get("Power (W)", 0.0))),
        }
        for field, actual in actuals.items():
            raw_limit = rating.get(field)
            if raw_limit is None or (isinstance(raw_limit, float) and math.isnan(raw_limit)) or raw_limit == "":
                continue
            try:
                limit = float(raw_limit)
            except (TypeError, ValueError):
                findings.append({"level": "error", "code": "INVALID_RATING",
                                 "message": f"{ref}: invalid {field.lower()} limit",
                                 "detail": "Use a finite positive datasheet limit or leave the field blank."})
                continue
            if not math.isfinite(limit) or limit <= 0:
                findings.append({"level": "error", "code": "INVALID_RATING",
                                 "message": f"{ref}: {field} limit must be positive",
                                 "detail": "Use a finite positive datasheet limit or leave the field blank."})
            elif actual > limit:
                findings.append({"level": "error", "code": "RATING_EXCEEDED",
                                 "message": f"{ref}: {field} limit exceeded",
                                 "detail": f"Calculated magnitude {actual:.6g} exceeds entered limit {limit:.6g}. Verify the analysis and exact part datasheet."})
            elif actual >= 0.8 * limit:
                findings.append({"level": "warning", "code": "RATING_MARGIN",
                                 "message": f"{ref}: limited margin against {field.lower()}",
                                 "detail": f"Calculated magnitude {actual:.6g} is at least 80% of entered limit {limit:.6g}; apply datasheet derating and transient checks."})
    if not findings:
        findings.append({"level": "pass", "code": "RATINGS_OK",
                         "message": "Entered component limits were not exceeded",
                         "detail": "Only the limits supplied by the user were checked. Missing datasheet ratings and derating requirements remain outside this result."})
    return findings


def validate_power_supply_design(result: dict[str, Any]) -> list[dict[str, str]]:
    """Translate Release 3.5 model outputs into concise design-review findings."""
    findings: list[dict[str, str]] = []

    def add(level: str, code: str, message: str, detail: str) -> None:
        findings.append({"level": level, "code": code, "message": message, "detail": detail})

    if not result:
        return [{"level": "info", "code": "NO_PSU_RESULT",
                 "message": "No power-supply calculation is available",
                 "detail": "Run the Release 3.5 Power Supply Design Studio first."}]
    if float(result.get("headroom_v", 0.0)) < 0:
        add("error", "REGULATOR_HEADROOM", "Regulator headroom check fails",
            "The estimated low-line reservoir valley is below output voltage plus assumed dropout.")
    else:
        add("pass", "REGULATOR_HEADROOM_OK", "Simplified regulator headroom check passes",
            "Confirm dropout at the actual load current and temperature using the exact regulator datasheet.")
    if float(result.get("valley_low_v", 0.0)) <= float(result.get("output_voltage_v", 0.0)):
        add("error", "VALLEY_BELOW_OUTPUT", "Reservoir valley is at or below the requested output",
            "The simplified low-line estimate cannot support the requested regulated output.")
    if float(result.get("ripple_pp_v", 0.0)) > float(result.get("ripple_target_v", math.inf)) * 1.001:
        add("warning", "RIPPLE_TARGET", "Estimated ripple exceeds the target",
            "Increase capacitance, reduce load current or revisit the rectifier and transformer assumptions.")
    if float(result.get("total_ripple_estimate_v", 0.0)) > float(result.get("ripple_target_v", math.inf)) * 1.001:
        add("warning", "ESR_RIPPLE", "Discharge ripple plus estimated ESR ripple exceeds the target",
            "Review capacitor ESR across temperature and frequency, ripple-current rating and lifetime.")
    if not bool(result.get("thermal_ok", False)):
        add("error", "THERMAL_ESTIMATE", "Simplified regulator thermal estimate fails",
            "Review dissipation, thermal resistance, heatsinking and the exact device safe operating area.")
    if result.get("suggested_capacitor_voltage_v") is None:
        add("warning", "CAPACITOR_VOLTAGE_RATING", "No built-in capacitor voltage rating meets the screening estimate",
            "Select a suitable higher-rated component and verify surge, ripple-current, ESR, temperature and lifetime.")
    if float(result.get("transformer_va", 0.0)) <= 0:
        add("error", "TRANSFORMER_VA", "Transformer VA estimate is invalid",
            "Verify secondary current and apparent-power assumptions.")
    add("info", "MODEL_LIMITATIONS", "This is a screening review, not design certification",
        "The underlying model does not solve transformer waveforms, rectifier conduction angle, inrush, fuse coordination, mains insulation, PCB clearances or detailed semiconductor/regulator safe operating areas.")
    return findings


def _render_findings(findings: list[dict[str, str]]) -> None:
    counts = {level: sum(1 for item in findings if item["level"] == level)
              for level in ("error", "warning", "info", "pass")}
    a, b, c, d = st.columns(4)
    a.metric("Errors", counts["error"])
    b.metric("Warnings", counts["warning"])
    c.metric("Information", counts["info"])
    d.metric("Passed checks", counts["pass"])
    for item in findings:
        title = f'{item["code"]} · {item["message"]}'
        body = item["detail"]
        if item["level"] == "error":
            st.error(f"**{title}**\n\n{body}")
        elif item["level"] == "warning":
            st.warning(f"**{title}**\n\n{body}")
        elif item["level"] == "pass":
            st.success(f"**{title}**\n\n{body}")
        else:
            st.info(f"**{title}**\n\n{body}")


def render_design_validator() -> None:
    st.markdown("### Intelligent design validation · Release 3.6")
    st.caption("Rule-based engineering checks for the supported DC network and the Release 3.5 power-supply estimate.")
    st.warning("A passed check means only that a particular rule did not flag the entered model. It does not establish electrical safety, regulatory compliance or construction readiness.")
    st.markdown("#### A · Circuit structure")
    network = st.session_state.get("r3_network")
    if network is None:
        st.info("Open the Interactive Engineering Studio and create a circuit to validate its structure.")
    else:
        records = network.to_dict("records") if hasattr(network, "to_dict") else list(network)
        structural = validate_netlist(records)
        _render_findings(structural)
        solved = st.session_state.get("r3_result")
        solved_netlist = solved.get("netlist", []) if solved else []
        current_netlist = []
        for row in records:
            try:
                current_netlist.append({
                    "Ref": str(row.get("Ref", "")).strip(),
                    "Type": str(row.get("Type", "")).strip().upper(),
                    "Node1": str(row.get("Node1", "")).strip(),
                    "Node2": str(row.get("Node2", "")).strip(),
                    "Value": float(row.get("Value")),
                })
            except (TypeError, ValueError):
                current_netlist.append({})
        # Require an exact match so stale operating-point results are never applied
        # to a circuit that has since changed values, nodes or component types.
        if solved and solved_netlist == current_netlist:
            st.markdown("#### B · Component operating-point ratings")
            st.caption("Enter maximum ratings from the exact datasheets. Leave unknown fields blank; blank limits are not checked.")
            defaults = pd.DataFrame([
                {"Ref": row.get("Ref", ""), "Max voltage (V)": None,
                 "Max current (A)": None, "Max power (W)": None}
                for row in records
            ], columns=RATING_COLUMNS)
            edited_ratings = st.data_editor(
                defaults, use_container_width=True, hide_index=True, num_rows="fixed",
                column_config={
                    "Ref": st.column_config.TextColumn("Reference", disabled=True),
                    "Max voltage (V)": st.column_config.NumberColumn("Max voltage (V)", min_value=0.000000001, format="%.6g"),
                    "Max current (A)": st.column_config.NumberColumn("Max current (A)", min_value=0.000000001, format="%.6g"),
                    "Max power (W)": st.column_config.NumberColumn("Max power (W)", min_value=0.000000001, format="%.6g"),
                },
                key="r36_component_ratings",
            )
            if st.button("Validate component ratings", key="r36_validate_ratings"):
                st.session_state["r36_rating_findings"] = validate_component_ratings(
                    solved.get("components", []), edited_ratings.to_dict("records"))
            if st.session_state.get("r36_rating_findings"):
                _render_findings(st.session_state["r36_rating_findings"])
        else:
            st.info("Solve the current circuit in Release 3.1 first. If you have changed its components since the last solve, analyse it again before checking operating-point ratings.")
    st.divider()
    st.markdown("#### C · Power-supply design review")
    psu = st.session_state.get("r35_result")
    if psu:
        _render_findings(validate_power_supply_design(psu))
    else:
        st.info("Run the Release 3.5 Advanced Power Supply Design Studio to generate a design for review.")
