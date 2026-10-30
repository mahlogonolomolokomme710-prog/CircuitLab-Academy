"""Compare theoretical circuit values with student-supplied simulator readings.

This module performs transparent arithmetic only. It does not run CircuitJS,
solve a circuit, or validate that a measurement was taken correctly.
"""
import csv
import io
import math


REQUIRED_COLUMNS = {"measurement", "theoretical", "simulated"}


def parse_measurement_csv(content):
    """Parse CSV text with measurement,theoretical,simulated,unit,tolerance_pct."""
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        raise ValueError("The CSV file is empty or has no header row.")
    normalized = {name.strip().lower() for name in reader.fieldnames if name}
    missing = REQUIRED_COLUMNS - normalized
    if missing:
        raise ValueError("Missing required CSV column(s): " + ", ".join(sorted(missing)))
    rows = []
    for line_no, raw in enumerate(reader, start=2):
        row = {str(k).strip().lower(): (v or "").strip() for k, v in raw.items() if k}
        if not any(row.values()):
            continue
        rows.append({
            "measurement": row.get("measurement", ""),
            "theoretical": row.get("theoretical", ""),
            "simulated": row.get("simulated", ""),
            "unit": row.get("unit", ""),
            "tolerance_pct": row.get("tolerance_pct", ""),
            "tolerance_abs": row.get("tolerance_abs", ""),
            "line": line_no,
        })
    if not rows:
        raise ValueError("The CSV contains a header but no measurement rows.")
    return rows


def _number(value, label, line):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"CSV line {line}: '{label}' must be a number.")
    if not math.isfinite(number):
        raise ValueError(f"CSV line {line}: '{label}' must be finite.")
    return number


def analyze_measurements(rows, default_tolerance_pct=5.0):
    """Compare expected and observed values; return row-level results and summary."""
    if not math.isfinite(float(default_tolerance_pct)) or float(default_tolerance_pct) < 0:
        raise ValueError("Default percentage tolerance must be a finite non-negative number.")
    results = []
    for index, row in enumerate(rows, start=1):
        line = row.get("line", index + 1)
        name = str(row.get("measurement", "")).strip() or f"Measurement {index}"
        theoretical = _number(row.get("theoretical"), "theoretical", line)
        simulated = _number(row.get("simulated"), "simulated", line)
        unit = str(row.get("unit", "")).strip()
        tolerance_raw = row.get("tolerance_pct", "")
        tolerance = float(default_tolerance_pct) if tolerance_raw in (None, "") else _number(tolerance_raw, "tolerance_pct", line)
        if tolerance < 0:
            raise ValueError(f"CSV line {line}: tolerance_pct cannot be negative.")
        absolute_error = simulated - theoretical
        if theoretical == 0:
            abs_tol_raw = row.get("tolerance_abs", "")
            if abs_tol_raw in (None, ""):
                pct_error = None
                status = "REVIEW — zero reference"
                criterion = "Percentage error is undefined for a zero theoretical value; supply tolerance_abs."
                abs_tolerance = None
            else:
                abs_tolerance = _number(abs_tol_raw, "tolerance_abs", line)
                if abs_tolerance < 0:
                    raise ValueError(f"CSV line {line}: tolerance_abs cannot be negative.")
                pct_error = None
                status = "WITHIN TOLERANCE" if abs(absolute_error) <= abs_tolerance else "OUTSIDE TOLERANCE"
                criterion = f"Absolute deviation ≤ {abs_tolerance:g} {unit}".strip()
        else:
            pct_error = absolute_error / abs(theoretical) * 100.0
            abs_tolerance = None
            status = "WITHIN TOLERANCE" if abs(pct_error) <= tolerance else "OUTSIDE TOLERANCE"
            criterion = f"Absolute percentage error ≤ {tolerance:g}%"
        results.append({
            "measurement": name, "theoretical": theoretical, "simulated": simulated,
            "unit": unit, "absolute_error": absolute_error, "percentage_error": pct_error,
            "status": status, "criterion": criterion,
        })
    within = sum(1 for r in results if r["status"] == "WITHIN TOLERANCE")
    outside = sum(1 for r in results if r["status"] == "OUTSIDE TOLERANCE")
    review = len(results) - within - outside
    lines = [
        f"Simulation comparison: {len(results)} measurement(s) analysed.",
        f"Within tolerance: {within}; outside tolerance: {outside}; require review: {review}.",
        "These are comparisons of student-supplied values, not measurements collected or verified by CircuitLab Academy.",
    ]
    for item in results:
        pct = "not defined" if item["percentage_error"] is None else f'{item["percentage_error"]:+.3f}%'
        lines.append(
            f'- {item["measurement"]}: theoretical {item["theoretical"]:g} {item["unit"]}; '
            f'simulated {item["simulated"]:g} {item["unit"]}; difference {item["absolute_error"]:+g} {item["unit"]}; '
            f'percentage error {pct}; {item["status"]}.'
        )
    return {
        "results": results, "within_tolerance": within, "outside_tolerance": outside,
        "review": review, "summary": "\n".join(lines),
    }


CSV_TEMPLATE = """measurement,theoretical,simulated,unit,tolerance_pct,tolerance_abs
Output voltage,5.0,4.92,V,5,
Resistor current,0.005,0.00495,A,5,
Capacitor final voltage,0,0.02,V,,0.05
"""
