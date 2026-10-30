"""First-pass engineering design calculations for a low-voltage linear DC supply.

This module is intentionally transparent and conservative about limitations. It
does not size a transformer, certify a design, model a regulator, or simulate a
circuit. All source values and assumptions must be verified by the designer.
"""
import math


def _positive(value, label, allow_zero=False):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be numeric.")
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite.")
    if number < 0 or (number == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "greater than zero"
        raise ValueError(f"{label} must be {qualifier}.")
    return number


def design_linear_supply(
    secondary_vac_rms,
    mains_frequency_hz,
    output_voltage_v,
    maximum_load_current_a,
    target_ripple_vpp,
    diode_forward_drop_v=0.8,
    regulator_dropout_v=2.0,
    ambient_temperature_c=25.0,
    regulator_theta_ja_c_per_w=0.0,
):
    """Return transparent estimates for a bridge + capacitor + linear regulator."""
    vac = _positive(secondary_vac_rms, "Secondary AC RMS voltage")
    frequency = _positive(mains_frequency_hz, "AC frequency")
    vout = _positive(output_voltage_v, "Target output voltage")
    current = _positive(maximum_load_current_a, "Maximum load current")
    ripple = _positive(target_ripple_vpp, "Target ripple")
    diode_drop = _positive(diode_forward_drop_v, "Assumed diode forward drop", allow_zero=True)
    dropout = _positive(regulator_dropout_v, "Regulator dropout", allow_zero=True)
    try:
        ambient = float(ambient_temperature_c)
    except (TypeError, ValueError):
        raise ValueError("Ambient temperature must be numeric.")
    if not math.isfinite(ambient):
        raise ValueError("Ambient temperature must be finite.")
    theta = _positive(regulator_theta_ja_c_per_w, "Thermal resistance", allow_zero=True)

    secondary_peak = vac * math.sqrt(2.0)
    rectified_peak = secondary_peak - 2.0 * diode_drop
    if rectified_peak <= 0:
        raise ValueError("The assumed two-diode drop leaves no positive rectified peak voltage.")

    ripple_frequency = 2.0 * frequency
    minimum_capacitance_f = current / (ripple_frequency * ripple)
    valley_voltage = rectified_peak - ripple
    average_unregulated_voltage = rectified_peak - ripple / 2.0
    required_regulator_input = vout + dropout
    headroom = valley_voltage - required_regulator_input
    regulator_dissipation_w = max(0.0, average_unregulated_voltage - vout) * current
    load_resistance_ohm = vout / current
    load_power_w = vout * current
    estimated_junction_temperature_c = (
        ambient + regulator_dissipation_w * theta if theta > 0 else None
    )

    warnings = []
    if headroom < 0:
        warnings.append(
            "Insufficient estimated regulator headroom at the ripple valley. "
            "The output may fall out of regulation; revisit the AC input, ripple target, "
            "regulator dropout or supply architecture."
        )
    else:
        warnings.append(
            "The idealized ripple-valley estimate clears the stated dropout requirement. "
            "Verify minimum AC line, transformer regulation, diode drops, load transients "
            "and regulator datasheet conditions."
        )
    if regulator_dissipation_w > 1.0:
        warnings.append(
            "Estimated regulator dissipation exceeds 1 W. Perform a proper thermal design; "
            "do not assume the package can dissipate this power without a heatsink."
        )
    if estimated_junction_temperature_c is not None:
        warnings.append(
            "The junction-temperature estimate uses the thermal-resistance value entered "
            "by the user. Confirm whether it applies to the actual PCB, copper area, airflow "
            "and heatsink arrangement."
        )
        if estimated_junction_temperature_c >= 125:
            warnings.append(
                "Estimated junction temperature is at least 125 °C. Treat this as a serious "
                "thermal warning and redesign using the exact regulator's absolute maximum "
                "and recommended operating limits."
            )
    else:
        warnings.append(
            "Junction temperature was not estimated because no thermal resistance was supplied."
        )

    warnings.extend([
        "Capacitance is a first-order constant-load discharge estimate: C ≈ I/(fripple × Vripple).",
        "The calculation omits transformer regulation and winding resistance, mains variation, "
        "diode dynamic behaviour, capacitor ESR/ripple-current heating, inrush, regulator "
        "stability and load transients.",
        "A bridge rectifier conducts through two diodes at a time; the assumed forward drop "
        "must be checked at the actual current and temperature.",
        "This result is not a validated design, simulator result, safety approval or build instruction."
    ])

    return {
        "inputs": {
            "secondary_vac_rms": vac, "mains_frequency_hz": frequency,
            "output_voltage_v": vout, "maximum_load_current_a": current,
            "target_ripple_vpp": ripple, "diode_forward_drop_v": diode_drop,
            "regulator_dropout_v": dropout, "ambient_temperature_c": ambient,
            "regulator_theta_ja_c_per_w": theta,
        },
        "secondary_peak_v": secondary_peak,
        "rectified_peak_v": rectified_peak,
        "ripple_frequency_hz": ripple_frequency,
        "minimum_capacitance_f": minimum_capacitance_f,
        "minimum_capacitance_uf": minimum_capacitance_f * 1e6,
        "estimated_valley_voltage_v": valley_voltage,
        "estimated_average_unregulated_voltage_v": average_unregulated_voltage,
        "required_regulator_input_v": required_regulator_input,
        "dropout_headroom_v": headroom,
        "estimated_regulator_dissipation_w": regulator_dissipation_w,
        "estimated_load_resistance_ohm": load_resistance_ohm,
        "estimated_load_power_w": load_power_w,
        "estimated_junction_temperature_c": estimated_junction_temperature_c,
        "warnings": warnings,
        "status": "HEADROOM CHECK FAILED" if headroom < 0 else "IDEALIZED HEADROOM CHECK PASSED",
    }


def build_design_report(result):
    """Create a Markdown report; values remain estimates, not verified measurements."""
    i = result["inputs"]
    def fmt(value, unit, digits=4):
        return f"{value:.{digits}g} {unit}"
    lines = [
        "# CircuitLab Academy — Preliminary 5 V Linear Supply Design",
        "",
        f"**Screening result:** {result['status']}",
        "",
        "## Design brief",
        f"- Isolated secondary input: {fmt(i['secondary_vac_rms'], 'V RMS')}",
        f"- AC frequency: {fmt(i['mains_frequency_hz'], 'Hz')}",
        f"- Target output: {fmt(i['output_voltage_v'], 'V DC')}",
        f"- Maximum load current: {fmt(i['maximum_load_current_a'], 'A')}",
        f"- Target ripple: {fmt(i['target_ripple_vpp'], 'V peak-to-peak')}",
        "",
        "## Calculated estimates",
        f"- Secondary peak: {fmt(result['secondary_peak_v'], 'V')}",
        f"- Rectified peak after two assumed diode drops: {fmt(result['rectified_peak_v'], 'V')}",
        f"- Full-wave ripple frequency: {fmt(result['ripple_frequency_hz'], 'Hz')}",
        f"- First-order minimum smoothing capacitance: {fmt(result['minimum_capacitance_uf'], 'µF')}",
        f"- Estimated ripple-valley voltage: {fmt(result['estimated_valley_voltage_v'], 'V')}",
        f"- Regulator input required (output + stated dropout): {fmt(result['required_regulator_input_v'], 'V')}",
        f"- Estimated dropout headroom: {fmt(result['dropout_headroom_v'], 'V')}",
        f"- Estimated average unregulated voltage: {fmt(result['estimated_average_unregulated_voltage_v'], 'V')}",
        f"- Estimated regulator dissipation: {fmt(result['estimated_regulator_dissipation_w'], 'W')}",
        f"- Equivalent load resistance at maximum current: {fmt(result['estimated_load_resistance_ohm'], 'Ω')}",
        f"- Load power: {fmt(result['estimated_load_power_w'], 'W')}",
    ]
    if result["estimated_junction_temperature_c"] is not None:
        lines.append(
            f"- Indicative junction temperature using user-entered thermal resistance: "
            f"{fmt(result['estimated_junction_temperature_c'], '°C')}"
        )
    lines.extend([
        "",
        "## Component selection and datasheet checks",
        "- **AC source/transformer:** verify isolation, secondary RMS voltage under load, regulation, frequency, current capability, insulation and applicable safety approvals. This tool does not size the transformer VA.",
        "- **Bridge diodes:** verify repetitive reverse voltage, average and surge forward current, forward drop at operating current, thermal resistance and package.",
        "- **Smoothing capacitor:** select capacitance at or above the calculated first-pass estimate, then verify voltage rating with margin for no-load/high-line conditions, ripple-current rating, ESR, temperature and lifetime.",
        "- **Linear regulator:** verify input range, dropout at maximum load and temperature, output current, current limit, power dissipation, safe operating area, thermal resistance, stability and required capacitors.",
        "- **Load resistor (if used):** verify resistance, tolerance, continuous power, working voltage and thermal derating.",
        "",
        "## Warnings and assumptions",
    ])
    lines.extend(f"- {warning}" for warning in result["warnings"])
    lines.extend([
        "",
        "## Validation plan",
        "1. Recalculate using minimum and maximum AC input and the exact component datasheets.",
        "2. Confirm rectifier and capacitor voltage/current stresses, including startup and surge conditions.",
        "3. Perform regulator thermal calculations for the real PCB, heatsink and ambient conditions.",
        "4. Build and simulate a low-voltage isolated model; label simulated readings separately from calculations.",
        "5. If a physical prototype is authorized, use an appropriately isolated, current-limited low-voltage source and approved laboratory procedures.",
        "6. Record measured output, ripple, load current and component temperatures with instrument details.",
        "",
        "**Important:** This preliminary educational estimate is not a certified design, safety assessment or substitute for lecturer/laboratory review. Never connect a student breadboard or beginner circuit directly to mains electricity.",
        "",
    ])
    return "\n".join(lines)
