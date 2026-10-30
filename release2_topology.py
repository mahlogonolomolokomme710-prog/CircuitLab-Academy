"""Heuristic topology interpretation for CircuitJS text schematics.

This module describes recognizable graph patterns. It does not solve circuits,
prove electrical function, decode every component pinout, or replace simulation.
"""
from collections import defaultdict


def _nets(item):
    values = item.get("nets") or []
    return [v for v in values if v is not None]


def _component_value(item):
    params = item.get("parameters") or []
    for token in reversed(params):
        try:
            return float(token.replace("E", "e"))
        except (TypeError, ValueError):
            continue
    return None


def analyze_topology(parsed):
    components = parsed.get("components", [])
    resistors = [c for c in components if c.get("type_code") == "r" and len(_nets(c)) >= 2]
    capacitors = [c for c in components if c.get("type_code") == "c" and len(_nets(c)) >= 2]
    inductors = [c for c in components if c.get("type_code") == "l" and len(_nets(c)) >= 2]
    diodes = [c for c in components if c.get("type_code") in ("d", "z") and len(_nets(c)) >= 2]
    sources = [c for c in components if c.get("type_code") in ("v", "i")]
    grounds = [c for c in components if c.get("type_code") == "g"]

    findings = []
    warnings = []
    resistor_degree = defaultdict(int)
    resistor_at_node = defaultdict(list)
    for r in resistors:
        a, b = _nets(r)[:2]
        resistor_degree[a] += 1
        resistor_degree[b] += 1
        resistor_at_node[a].append(r)
        resistor_at_node[b].append(r)

    # Two resistors connected to the same two nets form a parallel pair.
    parallel_pairs = defaultdict(list)
    for r in resistors:
        a, b = _nets(r)[:2]
        parallel_pairs[tuple(sorted((a, b)))].append(r)
    for pair, group in parallel_pairs.items():
        if len(group) >= 2:
            values = [_component_value(x) for x in group]
            value_text = ", ".join(f"{v:g} Ω" if v is not None else "unknown value" for v in values)
            findings.append(f"Possible parallel-resistor group: {len(group)} resistors share the same two inferred nets ({value_text}).")

    # A shared node with exactly two resistor branches is a series-chain segment
    # in the resistor-only subgraph. Other component connections can still load it.
    series_pairs = []
    for node, attached in resistor_at_node.items():
        unique = list({id(x): x for x in attached}.values())
        if len(unique) == 2 and resistor_degree[node] == 2:
            series_pairs.append((node, unique[0], unique[1]))
    seen_series = set()
    for node, left, right in series_pairs:
        key = tuple(sorted((id(left), id(right))))
        if key in seen_series:
            continue
        seen_series.add(key)
        findings.append("Possible series-resistor relationship: two resistors meet at an inferred node with no third resistor branch. Check whether another component is connected at that node.")

    # Voltage-divider candidate: exactly two resistors share one junction,
    # ground is on one outer end, and a voltage source spans the outer nets.
    if len(resistors) == 2:
        r1, r2 = resistors
        n1, n2 = _nets(r1)[:2]
        m1, m2 = _nets(r2)[:2]
        shared = set((n1, n2)) & set((m1, m2))
        outer = (set((n1, n2)) | set((m1, m2))) - shared
        ground_nets = {n for g in grounds for n in _nets(g)}
        source_pairs = [set(_nets(s)[:2]) for s in sources if len(_nets(s)) >= 2]
        if len(shared) == 1 and len(outer) == 2 and (outer & ground_nets) and any(outer.issubset(pair) for pair in source_pairs):
            values = [_component_value(r1), _component_value(r2)]
            if all(v is not None for v in values):
                findings.append(f"Voltage-divider candidate: two series resistors span a voltage-source/ground path. Ideal unloaded ratio depends on their decoded values ({values[0]:g} Ω and {values[1]:g} Ω); verify which resistor is upper/lower before calculating Vout.")
            else:
                findings.append("Voltage-divider candidate: two series resistors appear to span a voltage-source/ground path. Confirm values and output-node position.")

    # RC relationship: at least one resistor and capacitor share a node.
    rc_shared = []
    for r in resistors:
        for c in capacitors:
            common = set(_nets(r)[:2]) & set(_nets(c)[:2])
            if common:
                rc_shared.append((r, c, common))
    if rc_shared:
        findings.append(f"RC network candidate: {len(rc_shared)} resistor-capacitor pair(s) share inferred node(s). Determine whether the arrangement is low-pass, high-pass, timing, coupling or another topology from the complete connections and source/load.")

    if len(diodes) >= 4:
        findings.append(f"Rectifier candidate: {len(diodes)} diode-like devices detected. Four diodes may form a bridge rectifier, but diode orientation and node arrangement must be checked before confirming.")
    elif diodes:
        findings.append(f"Diode network detected: {len(diodes)} diode-like device(s). Their orientation and surrounding connections determine circuit function.")

    if inductors and capacitors:
        findings.append("LC network candidate: both inductors and capacitors are present. Resonance or filtering cannot be confirmed without topology, values and source/load context.")
    if any(c.get("type_code") in ("t", "q") for c in components):
        findings.append("Transistor device(s) detected. Pin roles and operating region require device-specific pin mapping and bias analysis; this version does not infer them.")

    if not findings:
        findings.append("No supported circuit pattern could be confidently identified from the extracted graph. Provide a clearer export or inspect the circuit manually.")

    if parsed.get("warnings"):
        warnings.append("The schematic parser reported unsupported or incomplete records.")
    warnings.append("Topology findings are heuristic candidates based on inferred nets, not a validated circuit solution. Cross-check wiring, pin semantics, values and operating conditions in CircuitJS.")
    lines = ["Topology interpretation (heuristic):"]
    lines.extend(f"- {item}" for item in findings)
    lines.append("Interpretation limits:")
    lines.extend(f"- {item}" for item in warnings)
    return {"findings": findings, "warnings": warnings, "summary": "\\n".join(lines)}
