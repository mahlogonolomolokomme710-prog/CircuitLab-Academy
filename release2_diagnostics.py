"""Evidence-led, rule-based fault investigation suggestions.

The engine ranks checks from supplied measurements, topology notes and symptoms.
It does not diagnose a physical circuit or prove a component has failed.
"""


def _text(value):
    return str(value or "").strip().lower()


def build_diagnosis(comparison, topology_summary="", symptoms=""):
    results = (comparison or {}).get("results", [])
    outside = [r for r in results if r.get("status") == "OUTSIDE TOLERANCE"]
    review = [r for r in results if str(r.get("status", "")).startswith("REVIEW")]
    topology = _text(topology_summary)
    symptom_text = _text(symptoms)
    evidence = []
    checks = []

    if not results and not symptom_text and not topology:
        return {
            "findings": ["Insufficient evidence: provide measurement comparisons, a topology summary, or a symptom description."],
            "checks": ["Record the expected and observed values with units and measurement locations."],
            "summary": "Fault investigation not performed: no measurement, topology or symptom evidence was supplied.",
            "limitations": ["No fault can be inferred from an empty evidence set."],
        }

    if outside:
        evidence.append(f"{len(outside)} measurement(s) were marked outside the supplied tolerance.")
        for row in outside:
            name = _text(row.get("measurement"))
            delta = row.get("percentage_error")
            direction = "higher" if delta is not None and delta > 0 else "lower" if delta is not None and delta < 0 else "different from"
            checks.append(
                f"Recheck {row.get('measurement', 'the measurement')}: the supplied simulated value is {direction} than the theoretical reference. "
                "Confirm units, probe location, reference node, source setting and component values before changing the circuit."
            )
            if any(token in name for token in ("out", "output", "vout", "voltage")):
                checks.append("For the voltage discrepancy, compare the source voltage at the circuit terminals with the output node, then inspect loading, ground/reference continuity and resistor or diode drops.")
            if any(token in name for token in ("current", "amps", "load")):
                checks.append("For the current discrepancy, verify the current probe is in series, check the load path for an open/short, and recalculate current from the actual voltage across the load and its resistance.")
            if any(token in name for token in ("ripple", "peak", "ac")):
                checks.append("For ripple or AC discrepancies, confirm the waveform measurement mode, time base, peak-to-peak definition, rectifier configuration and smoothing-capacitor value.")
    else:
        evidence.append("No measurement was classified outside the supplied tolerance.")
    if review:
        evidence.append(f"{len(review)} measurement(s) require review because a percentage comparison was not defined or evidence was incomplete.")
        checks.append("For zero-reference measurements, define a physically meaningful absolute tolerance and confirm the measurement resolution.")

    if "voltage-divider candidate" in topology or "voltage divider" in topology:
        evidence.append("The supplied topology notes contain a voltage-divider candidate.")
        checks.extend([
            "Verify the source, upper resistor, lower resistor and output node are connected in the intended order.",
            "Measure the output relative to the same ground/reference used in the theoretical divider calculation.",
            "Check whether a connected load changes the effective lower-leg resistance; the unloaded divider equation may no longer apply.",
        ])
    if "parallel-resistor" in topology or "parallel resistor" in topology:
        evidence.append("The supplied topology notes contain a possible parallel-resistor group.")
        checks.append("Confirm both terminals of each resistor really share the same two electrical nodes; compare equivalent resistance with R_eq = 1/(1/R1 + 1/R2 + …).")
    if "series-resistor" in topology or "series resistor" in topology:
        evidence.append("The supplied topology notes contain a possible series-resistor relationship.")
        checks.append("Confirm there is no additional branch at the shared node and compare the expected current through each series element.")
    if "rc network candidate" in topology or "capacitor" in symptom_text or "charging" in symptom_text or "discharging" in symptom_text:
        evidence.append("RC behaviour may be relevant based on the topology notes or symptom description.")
        checks.extend([
            "Check the capacitor value and units, polarity where applicable, initial voltage and the resistor path.",
            "Compare the observed response time with τ = R × C; a first-order response reaches approximately 63.2% of its final change after one time constant.",
            "Check whether the capacitor is actually connected to the intended node and whether the load creates an additional discharge path.",
        ])
    if "diode" in topology or "rectifier" in topology or "ripple" in symptom_text or "rectif" in symptom_text:
        evidence.append("A diode or rectifier-related issue may be relevant to the supplied topology or symptom.")
        checks.extend([
            "Verify diode orientation and the actual anode/cathode connections against the schematic.",
            "Check that the source waveform and polarity are appropriate for the intended rectifier stage.",
            "Inspect the output waveform before and after the smoothing capacitor; do not infer rectification from diode count alone.",
        ])
    if any(token in symptom_text for token in ("no output", "zero output", "not working", "no current", "doesn't work", "does not work")):
        evidence.append("The symptom description indicates absent or unexpectedly small output.")
        checks.extend([
            "Trace the circuit from source to load and verify each connection and return path.",
            "Check for an open switch, disconnected wire, incorrect ground/reference, or component inserted into the wrong node.",
            "Verify the source is enabled and that the selected measurement point is not floating.",
        ])
    if any(token in symptom_text for token in ("too hot", "overheat", "smoke", "burn")):
        evidence.append("The symptom description mentions possible overheating or damage.")
        checks.insert(0, "STOP the simulation or physical test and isolate power before inspection. Do not touch hot components or repeatedly re-energize a suspected fault.")
        checks.append("After power is isolated, calculate component dissipation and compare it with datasheet power, voltage, current and thermal ratings. A simulation result alone does not establish safe physical operation.")

    if not checks:
        checks = [
            "Confirm the circuit objective and expected operating conditions.",
            "Check supply settings, wiring continuity, reference/ground and component values.",
            "Record node voltages and branch currents at named measurement points, with units, before changing one variable at a time.",
        ]

    unique_checks = []
    seen = set()
    for item in checks:
        if item not in seen:
            seen.add(item)
            unique_checks.append(item)
    findings = evidence or ["The supplied information is insufficient to identify a specific likely fault."]
    limitations = [
        "These are ranked investigation suggestions, not a confirmed diagnosis or proof of a failed component.",
        "Topology notes may be heuristic and inferred from an exported schematic; verify connections and pin semantics in CircuitJS.",
        "Measurements are student-supplied and have not been independently collected or validated.",
        "For physical work, use isolated, current-limited low-voltage supplies for student experiments; never connect a beginner circuit directly to mains.",
    ]
    lines = ["Evidence-led fault investigation (Release 2.4)", "Evidence:"]
    lines.extend(f"- {x}" for x in findings)
    lines.append("Recommended checks (investigate in order):")
    lines.extend(f"{i}. {x}" for i, x in enumerate(unique_checks, 1))
    lines.append("Limitations:")
    lines.extend(f"- {x}" for x in limitations)
    return {"findings": findings, "checks": unique_checks, "summary": "\n".join(lines), "limitations": limitations}
