"""Release 3.5 — Advanced low-voltage linear power-supply design studio.

Transparent first-pass engineering estimates. Not a validated design, SPICE
solver, transformer/semiconductor model, or safety certification.
"""
from __future__ import annotations

import math
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

CAPACITOR_VOLTAGE_STANDARDS = [6.3, 10, 16, 25, 35, 50, 63, 100, 160, 250]
CAPACITANCE_STANDARDS_UF = [10, 22, 33, 47, 68, 100, 150, 220, 330, 470, 680, 1000, 1500, 2200, 3300, 4700, 6800, 10000, 15000, 22000]


def _finite_positive(name: str, value: float, allow_zero: bool = False) -> float:
    value = float(value)
    if not math.isfinite(value) or (value < 0 if allow_zero else value <= 0):
        raise ValueError(f"{name} must be {'non-negative' if allow_zero else 'positive'} and finite.")
    return value


def design_power_supply(
    secondary_rms_v: float = 12.0,
    line_frequency_hz: float = 50.0,
    topology: str = "Full-wave bridge",
    load_current_ma: float = 100.0,
    output_voltage_v: float = 5.0,
    ripple_target_v: float = 1.0,
    diode_drop_v: float = 0.7,
    transformer_regulation_pct: float = 10.0,
    low_line_pct: float = 10.0,
    capacitor_esr_ohm: float = 0.08,
    regulator_dropout_v: float = 2.0,
    regulator_type: str = "Linear",
    transformer_current_factor: float = 1.8,
    theta_ja_c_per_w: float = 50.0,
    ambient_c: float = 25.0,
    maximum_junction_c: float = 125.0,
    theta_jc_c_per_w: float = 5.0,
    theta_cs_c_per_w: float = 1.0,
) -> dict[str, Any]:
    """Calculate a first-pass isolated AC to regulated DC supply estimate."""
    positive = {
        "Secondary RMS voltage": secondary_rms_v,
        "Line frequency": line_frequency_hz,
        "Load current": load_current_ma,
        "Output voltage": output_voltage_v,
        "Ripple target": ripple_target_v,
        "Transformer current factor": transformer_current_factor,
        "Junction-to-ambient thermal resistance": theta_ja_c_per_w,
        "Maximum junction temperature": maximum_junction_c,
    }
    for name, value in positive.items():
        _finite_positive(name, value)
    for name, value in {
        "Diode drop": diode_drop_v, "Capacitor ESR": capacitor_esr_ohm,
        "Regulator dropout": regulator_dropout_v, "Transformer regulation": transformer_regulation_pct,
        "Low-line allowance": low_line_pct, "Ambient temperature": ambient_c,
        "Junction-to-case thermal resistance": theta_jc_c_per_w,
        "Case-to-sink thermal resistance": theta_cs_c_per_w,
    }.items():
        if not math.isfinite(float(value)) or value < 0:
            raise ValueError(f"{name} must be finite and non-negative.")
    if transformer_regulation_pct >= 100 or low_line_pct >= 100:
        raise ValueError("Transformer regulation and low-line allowances must each be below 100%.")
    if topology not in {"Half-wave", "Full-wave bridge"}:
        raise ValueError("Select Half-wave or Full-wave bridge.")
    if regulator_type not in {"Linear", "Low-dropout (LDO)"}:
        raise ValueError("Select Linear or Low-dropout (LDO).")
    if maximum_junction_c <= ambient_c:
        raise ValueError("Maximum junction temperature must exceed ambient temperature.")

    current_a = load_current_ma / 1000.0
    drops = 1 if topology == "Half-wave" else 2
    ripple_frequency = line_frequency_hz if topology == "Half-wave" else 2 * line_frequency_hz
    nominal_peak = secondary_rms_v * math.sqrt(2)
    low_line_rms = secondary_rms_v * (1 - low_line_pct / 100)
    low_line_peak = low_line_rms * math.sqrt(2)
    regulated_low_rms = low_line_rms / (1 + transformer_regulation_pct / 100)
    regulated_low_peak = regulated_low_rms * math.sqrt(2)
    peak_nominal_after_drops = nominal_peak - drops * diode_drop_v
    peak_low_after_drops = low_line_peak - drops * diode_drop_v
    required_c_f = current_a / (ripple_frequency * ripple_target_v)
    required_c_uf = required_c_f * 1e6
    standard_cap = next((c for c in CAPACITANCE_STANDARDS_UF if c >= required_c_uf), None)
    selected_cap_uf = standard_cap if standard_cap is not None else required_c_uf
    selected_cap_f = selected_cap_uf * 1e-6
    ripple_pp = current_a / (ripple_frequency * selected_cap_f)
    esr_ripple = current_a * capacitor_esr_ohm
    total_ripple_estimate = ripple_pp + esr_ripple
    valley_nominal = peak_nominal_after_drops - ripple_pp
    valley_low = peak_low_after_drops - ripple_pp
    average_low = peak_low_after_drops - ripple_pp / 2
    required_regulator_input = output_voltage_v + regulator_dropout_v
    headroom = valley_low - required_regulator_input
    regulator_power = max(0.0, (average_low - output_voltage_v) * current_a)
    junction_estimate = ambient_c + regulator_power * theta_ja_c_per_w
    allowable_power = (maximum_junction_c - ambient_c) / theta_ja_c_per_w
    transformer_secondary_current = current_a * transformer_current_factor
    transformer_va = secondary_rms_v * transformer_secondary_current
    diode_average_each = current_a / 2 if topology == "Full-wave bridge" else current_a
    diode_power_each = diode_drop_v * diode_average_each
    cap_voltage_min = peak_nominal_after_drops * 1.25
    cap_voltage_rating = next((v for v in CAPACITOR_VOLTAGE_STANDARDS if v >= cap_voltage_min), None)
    regulator_ok = headroom >= 0
    thermal_ok = junction_estimate < maximum_junction_c and regulator_power <= allowable_power

    warnings = []
    if headroom < 0:
        warnings.append("LOW-LINE REGULATOR HEADROOM: the estimated valley is below the output plus dropout requirement.")
    if valley_low <= output_voltage_v:
        warnings.append("LOW-LINE VALLEY BELOW OUTPUT: the selected input cannot maintain the requested output in this simplified model.")
    if ripple_pp > ripple_target_v * 1.001:
        warnings.append("RIPPLE TARGET NOT MET: increase capacitance or reduce load current.")
    if cap_voltage_rating is None:
        warnings.append("CAPACITOR VOLTAGE: calculated suggested rating exceeds the built-in standard list; select a suitable higher-rated part.")
    if not thermal_ok:
        warnings.append("THERMAL LIMIT: estimated junction temperature exceeds the entered limit or the estimated dissipation exceeds the simplified thermal budget.")
    if transformer_va <= 0:
        warnings.append("TRANSFORMER: verify the selected transformer VA and secondary current rating.")
    if not warnings:
        warnings.append("No limit was flagged by these first-pass checks. This is not proof of a safe or validated design.")

    return {
        "topology": topology, "regulator_type": regulator_type,
        "secondary_rms_v": secondary_rms_v, "line_frequency_hz": line_frequency_hz,
        "load_current_ma": load_current_ma, "output_voltage_v": output_voltage_v,
        "ripple_target_v": ripple_target_v, "diode_drop_v": diode_drop_v,
        "nominal_peak_after_drops_v": peak_nominal_after_drops,
        "low_line_peak_after_drops_v": peak_low_after_drops,
        "low_line_regulated_peak_after_drops_v": regulated_low_peak - drops * diode_drop_v,
        "ripple_frequency_hz": ripple_frequency, "required_capacitance_uf": required_c_uf,
        "selected_capacitance_uf": selected_cap_uf, "ripple_pp_v": ripple_pp,
        "esr_ripple_estimate_v": esr_ripple, "total_ripple_estimate_v": total_ripple_estimate,
        "valley_nominal_v": valley_nominal, "valley_low_v": valley_low,
        "average_low_v": average_low, "required_regulator_input_v": required_regulator_input,
        "headroom_v": headroom, "regulator_power_w": regulator_power,
        "junction_estimate_c": junction_estimate, "allowable_power_w": allowable_power,
        "transformer_secondary_current_a": transformer_secondary_current,
        "transformer_va": transformer_va, "diode_average_each_a": diode_average_each,
        "diode_power_each_w": diode_power_each, "capacitor_voltage_min_v": cap_voltage_min,
        "suggested_capacitor_voltage_v": cap_voltage_rating,
        "regulator_headroom_ok": regulator_ok, "thermal_ok": thermal_ok,
        "warnings": warnings, "transformer_regulation_pct": transformer_regulation_pct,
        "low_line_pct": low_line_pct, "capacitor_esr_ohm": capacitor_esr_ohm,
        "regulator_dropout_v": regulator_dropout_v, "theta_ja_c_per_w": theta_ja_c_per_w,
        "ambient_c": ambient_c, "maximum_junction_c": maximum_junction_c,
        "theta_jc_c_per_w": theta_jc_c_per_w, "theta_cs_c_per_w": theta_cs_c_per_w,
    }


def thermal_analysis(result: dict[str, Any]) -> dict[str, float | str]:
    """Estimate heatsink thermal resistance for a chosen junction target."""
    power = float(result["regulator_power_w"])
    allowed_r_total = (float(result["maximum_junction_c"]) - float(result["ambient_c"])) / power if power > 0 else math.inf
    sink_required = allowed_r_total - float(result["theta_jc_c_per_w"]) - float(result["theta_cs_c_per_w"])
    return {
        "regulator_power_w": power,
        "maximum_total_thermal_resistance_c_per_w": allowed_r_total,
        "maximum_heatsink_thermal_resistance_c_per_w": max(0.0, sink_required) if math.isfinite(sink_required) else math.inf,
        "heatsink_required": "Yes" if sink_required < float(result["theta_ja_c_per_w"]) else "Not indicated by this simplified comparison",
    }


def build_design_report(result: dict[str, Any], design_name: str = "Low-voltage regulated DC supply") -> str:
    thermal = thermal_analysis(result)
    rows = [
        f"# CircuitLab Academy — {design_name}", "",
        "## Design inputs",
        f'- Transformer secondary: {result["secondary_rms_v"]:.6g} V RMS, {result["line_frequency_hz"]:.6g} Hz',
        f'- Rectifier: {result["topology"]}; assumed diode drop: {result["diode_drop_v"]:.6g} V per conducting diode',
        f'- Load: {result["load_current_ma"]:.6g} mA; target output: {result["output_voltage_v"]:.6g} V',
        f'- Ripple target: {result["ripple_target_v"]:.6g} V peak-to-peak',
        f'- Regulator: {result["regulator_type"]}; assumed dropout: {result["regulator_dropout_v"]:.6g} V',
        f'- Low-line allowance: {result["low_line_pct"]:.6g}%; transformer regulation allowance: {result["transformer_regulation_pct"]:.6g}%', "",
        "## Calculated estimates",
        f'- Ripple frequency: {result["ripple_frequency_hz"]:.6g} Hz',
        f'- Minimum calculated capacitance: {result["required_capacitance_uf"]:.6g} µF',
        f'- Selected nominal capacitance: {result["selected_capacitance_uf"]:.6g} µF',
        f'- Estimated ripple (capacitor discharge): {result["ripple_pp_v"]:.6g} V p-p',
        f'- Additional ESR ripple estimate: {result["esr_ripple_estimate_v"]:.6g} V',
        f'- Estimated low-line valley: {result["valley_low_v"]:.6g} V',
        f'- Required regulator input: {result["required_regulator_input_v"]:.6g} V',
        f'- Low-line headroom margin: {result["headroom_v"]:.6g} V',
        f'- Regulator dissipation: {result["regulator_power_w"]:.6g} W',
        f'- Estimated junction temperature: {result["junction_estimate_c"]:.6g} °C',
        f'- Transformer secondary current estimate: {result["transformer_secondary_current_a"]:.6g} A',
        f'- Transformer apparent-power estimate: {result["transformer_va"]:.6g} VA',
        f'- Suggested capacitor voltage rating: {result["suggested_capacitor_voltage_v"] or "Select a suitable higher-rated component"} V',
        f'- Heatsink thermal-resistance target: {thermal["maximum_heatsink_thermal_resistance_c_per_w"]:.6g} °C/W' if math.isfinite(thermal["maximum_heatsink_thermal_resistance_c_per_w"]) else "- Heatsink thermal-resistance target: no dissipation in this ideal estimate",
        "", "## Design review flags",
    ]
    rows.extend(f"- {warning}" for warning in result["warnings"])
    rows.extend([
        "", "## Assumptions and limitations",
        "- First-pass educational model for an isolated low-voltage AC secondary feeding a rectifier, reservoir capacitor and linear regulator.",
        "- Transformer low-line and regulation allowances are simplified independent percentage reductions; transformer winding resistance and load-dependent waveform are not solved.",
        "- Transformer VA uses a user-selected current form factor; capacitor-input rectifier RMS current depends on transformer impedance, conduction angle and capacitor charging pulses.",
        "- Ripple uses ΔV ≈ I/(fC), with a separate simple I×ESR estimate. It is not a detailed capacitor charging simulation.",
        "- Diode losses use average current sharing estimates; reverse voltage, surge current, recovery, junction temperature and heatsink are not fully modelled.",
        "- Regulator dissipation and junction temperature are simplified steady-state estimates. Verify datasheet thermal metrics, safe operating area, dropout versus current/temperature and protection behaviour.",
        "- Capacitor voltage suggestion is a screening margin only. Verify surge, ripple-current, ESR, lifetime and temperature ratings.",
        "- No safety certification, mains-side design, PCB creepage/clearance, insulation coordination, fuse design or construction approval is provided.",
        "", "## Verification checklist",
        "- [ ] Confirm exact transformer isolation, RMS regulation, current and VA ratings.",
        "- [ ] Confirm diode IF(AV), IFSM, VRRM and thermal limits.",
        "- [ ] Confirm capacitor polarity, voltage, ripple-current, ESR and lifetime ratings.",
        "- [ ] Confirm regulator pinout, input range, dropout, current limit, SOA and thermal data.",
        "- [ ] Independently verify calculations and simulate with suitable component models.",
        "- [ ] Use only an appropriately isolated, current-limited low-voltage source for supervised student experiments.",
        "- [ ] Keep physical measurements distinct from calculated and simulated results.",
        "", "**Educational estimate only — not a construction-ready or safety-approved design.**", ""
    ])
    return "\n".join(rows)


def _draw_power_path(result: dict[str, Any]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(12, 3.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3)
    ax.axis("off")
    labels = [
        ("Isolated AC\ntransformer", f'{result["secondary_rms_v"]:.3g} V RMS'),
        (result["topology"], f'{result["ripple_frequency_hz"]:.3g} Hz ripple'),
        ("Reservoir capacitor", f'{result["selected_capacitance_uf"]:.3g} µF'),
        ("Linear regulator", f'{result["output_voltage_v"]:.3g} V target'),
        ("DC load", f'{result["load_current_ma"]:.3g} mA'),
    ]
    xs = [1.2, 3.6, 6.0, 8.4, 10.8]
    for i, (title, detail) in enumerate(labels):
        ax.add_patch(plt.Rectangle((xs[i]-0.9, 1.0), 1.8, 1.15, fill=False, linewidth=2))
        ax.text(xs[i], 1.65, title, ha="center", va="center", fontsize=9, weight="bold")
        ax.text(xs[i], 1.2, detail, ha="center", va="center", fontsize=8)
        if i < len(xs)-1:
            ax.annotate("", xy=(xs[i+1]-0.95, 1.57), xytext=(xs[i]+0.95, 1.57),
                        arrowprops={"arrowstyle":"->", "lw":1.8})
    ax.set_title("Power-supply functional block diagram · not a pin-level schematic", fontsize=12)
    fig.tight_layout()
    return fig


def render_power_supply_studio() -> None:
    st.markdown("### Advanced power-supply design studio · Release 3.5")
    st.caption("Work from load requirements backwards through regulation, filtering, rectification and transformer capacity.")
    st.info("This studio is for isolated low-voltage AC educational designs. It does not calculate or approve a mains-side circuit.")
    with st.expander("1 · Define the supply requirements", expanded=True):
        a, b, c = st.columns(3)
        output = a.number_input("Required regulated output (V)", min_value=0.1, value=5.0, key="r35_vout")
        current = b.number_input("Maximum load current (mA)", min_value=1.0, value=100.0, key="r35_iout")
        ripple = c.number_input("Maximum reservoir ripple target (V p-p)", min_value=0.01, value=1.0, key="r35_ripple")
    with st.expander("2 · Transformer and rectifier", expanded=True):
        a, b, c = st.columns(3)
        secondary = a.number_input("Isolated secondary (V RMS)", min_value=0.1, value=12.0, key="r35_secondary")
        frequency = b.selectbox("Secondary frequency (Hz)", [50.0, 60.0], index=0, key="r35_frequency")
        topology = c.selectbox("Rectifier", ["Full-wave bridge", "Half-wave"], key="r35_topology")
        d, e, f = st.columns(3)
        diode_drop = d.number_input("Assumed forward drop per diode (V)", min_value=0.0, value=0.7, key="r35_vf")
        regulation = e.number_input("Transformer regulation allowance (%)", min_value=0.0, value=10.0, key="r35_regulation")
        low_line = f.number_input("Low-line allowance (%)", min_value=0.0, value=10.0, key="r35_lowline")
        form_factor = st.slider("Transformer secondary RMS current factor × DC load current", 1.0, 3.0, 1.8, 0.05, key="r35_factor")
    with st.expander("3 · Reservoir capacitor and regulator", expanded=True):
        a, b, c = st.columns(3)
        esr = a.number_input("Capacitor ESR estimate (Ω)", min_value=0.0, value=0.08, key="r35_esr")
        regulator = b.selectbox("Regulator class", ["Linear", "Low-dropout (LDO)"], key="r35_regulator")
        dropout = c.number_input("Regulator dropout/headroom (V)", min_value=0.0, value=2.0 if regulator == "Linear" else 0.3, key="r35_dropout")
    with st.expander("4 · Thermal design assumptions", expanded=False):
        a, b, c = st.columns(3)
        ambient = a.number_input("Ambient temperature (°C)", value=25.0, key="r35_ambient")
        tjmax = b.number_input("Maximum design junction temperature (°C)", value=125.0, key="r35_tjmax")
        theta_ja = c.number_input("Junction-to-ambient θJA (°C/W)", min_value=0.1, value=50.0, key="r35_theta_ja")
        d, e = st.columns(2)
        theta_jc = d.number_input("Junction-to-case θJC (°C/W)", min_value=0.0, value=5.0, key="r35_theta_jc")
        theta_cs = e.number_input("Case-to-sink θCS (°C/W)", min_value=0.0, value=1.0, key="r35_theta_cs")
    try:
        result = design_power_supply(
            secondary_rms_v=secondary, line_frequency_hz=frequency, topology=topology,
            load_current_ma=current, output_voltage_v=output, ripple_target_v=ripple,
            diode_drop_v=diode_drop, transformer_regulation_pct=regulation,
            low_line_pct=low_line, capacitor_esr_ohm=esr, regulator_dropout_v=dropout,
            regulator_type=regulator, transformer_current_factor=form_factor,
            theta_ja_c_per_w=theta_ja, ambient_c=ambient, maximum_junction_c=tjmax,
            theta_jc_c_per_w=theta_jc, theta_cs_c_per_w=theta_cs,
        )
    except ValueError as exc:
        st.error(str(exc))
        return
    st.divider()
    st.markdown("#### Design results")
    a, b, c, d = st.columns(4)
    a.metric("Suggested reservoir capacitor", f'{result["selected_capacitance_uf"]:,.0f} µF')
    b.metric("Estimated low-line valley", f'{result["valley_low_v"]:.2f} V')
    c.metric("Regulator headroom margin", f'{result["headroom_v"]:.2f} V')
    d.metric("Transformer VA estimate", f'{result["transformer_va"]:.2f} VA')
    fig = _draw_power_path(result)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    left, right = st.columns(2)
    with left:
        st.markdown("**Rectifier and filtering**")
        st.write(f'Ripple frequency: {result["ripple_frequency_hz"]:.3g} Hz')
        st.write(f'Minimum calculated capacitance: {result["required_capacitance_uf"]:.3g} µF')
        st.write(f'Estimated capacitor ripple: {result["ripple_pp_v"]:.3g} V p-p')
        st.write(f'Additional ESR ripple estimate: {result["esr_ripple_estimate_v"]:.3g} V')
        st.write(f'Suggested capacitor voltage rating: {result["suggested_capacitor_voltage_v"] or "Select a higher-rated part"} V')
        st.write(f'Average estimated low-line reservoir voltage: {result["average_low_v"]:.3g} V')
    with right:
        st.markdown("**Regulator and thermal**")
        st.write(f'Regulator dissipation: {result["regulator_power_w"]:.3g} W')
        st.write(f'Estimated junction temperature: {result["junction_estimate_c"]:.1f} °C')
        st.write(f'Simplified allowable dissipation: {result["allowable_power_w"]:.3g} W')
        thermal = thermal_analysis(result)
        hs = thermal["maximum_heatsink_thermal_resistance_c_per_w"]
        st.write(f'Maximum heatsink θSA estimate: {hs:.3g} °C/W' if math.isfinite(hs) else "No regulator dissipation in this ideal estimate")
        st.write(f'Thermal check: {thermal["heatsink_required"]}')
    if result["regulator_headroom_ok"]:
        st.success("The simplified low-line headroom check is satisfied.")
    else:
        st.error("The simplified low-line headroom check fails. Revisit transformer voltage, ripple, load or regulator choice.")
    if result["thermal_ok"]:
        st.info("The simplified thermal estimate is below the entered junction-temperature limit.")
    else:
        st.error("The simplified thermal estimate exceeds the entered limit. Revisit regulator dissipation and thermal path.")
    st.markdown("**Engineering review flags**")
    for warning in result["warnings"]:
        st.warning(warning)
    report = build_design_report(result)
    st.download_button("Download complete power-supply design report", report,
                       file_name="circuitlab_power_supply_design_report.md", mime="text/markdown", type="primary")
    st.download_button("Download design results (CSV)",
                       pd.DataFrame([result]).drop(columns=["warnings"]).to_csv(index=False).encode("utf-8"),
                       file_name="circuitlab_power_supply_design.csv", mime="text/csv")
    st.caption("Calculated first-pass values only. Confirm the exact transformer, rectifier, capacitor and regulator datasheets; verify with appropriate simulation and supervised laboratory measurements.")
