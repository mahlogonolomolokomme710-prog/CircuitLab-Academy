"""Release 3.4 — diode, LED and rectifier learning laboratory.

Transparent educational models and first-pass design estimates. Not a SPICE
semiconductor model, validated power-supply design, or safety certification.
"""
from __future__ import annotations

import math
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

BOLTZMANN = 1.380649e-23
ELEMENTARY_CHARGE = 1.602176634e-19


def diode_shockley_current(voltage_v: float, saturation_current_a: float = 1e-12,
                           ideality_factor: float = 2.0, temperature_c: float = 25.0) -> float:
    """Ideal Shockley diode current; excludes series resistance and breakdown."""
    vals = (voltage_v, saturation_current_a, ideality_factor, temperature_c)
    if any(not math.isfinite(float(v)) for v in vals):
        raise ValueError("Diode inputs must be finite.")
    if saturation_current_a <= 0 or ideality_factor <= 0 or temperature_c <= -273.15:
        raise ValueError("Saturation current and ideality factor must be positive; temperature must exceed absolute zero.")
    thermal_voltage = BOLTZMANN * (temperature_c + 273.15) / ELEMENTARY_CHARGE
    exponent = max(-100.0, min(40.0, voltage_v / (ideality_factor * thermal_voltage)))
    current = saturation_current_a * math.expm1(exponent)
    if not math.isfinite(current):
        raise ValueError("Calculated diode current is outside the supported range.")
    return current


def diode_curve(saturation_current_a: float = 1e-12, ideality_factor: float = 2.0,
                temperature_c: float = 25.0, reverse_limit_v: float = -0.8,
                forward_limit_v: float = 0.85, samples: int = 301) -> pd.DataFrame:
    if samples < 51 or samples > 2001 or reverse_limit_v >= forward_limit_v:
        raise ValueError("Choose a valid voltage range and between 51 and 2001 samples.")
    voltages = [reverse_limit_v + (forward_limit_v - reverse_limit_v) * i / (samples - 1)
                for i in range(samples)]
    currents = [diode_shockley_current(v, saturation_current_a, ideality_factor, temperature_c)
                for v in voltages]
    return pd.DataFrame({"voltage_v": voltages, "current_a": currents})


def led_series_resistor(supply_v: float, led_forward_v: float, target_current_ma: float,
                        resistor_power_margin: float = 2.0) -> dict[str, float]:
    vals = (supply_v, led_forward_v, target_current_ma, resistor_power_margin)
    if any(not math.isfinite(float(v)) for v in vals):
        raise ValueError("LED design inputs must be finite.")
    if supply_v <= 0 or led_forward_v < 0 or target_current_ma <= 0 or resistor_power_margin < 1:
        raise ValueError("Supply/current must be positive; LED drop non-negative; power margin at least 1.")
    if supply_v <= led_forward_v:
        raise ValueError("Supply voltage must exceed the LED forward voltage.")
    current_a = target_current_ma / 1000.0
    minimum_r = (supply_v - led_forward_v) / current_a
    # Round UP to the next E12 nominal value so current does not exceed target.
    e12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
    decade = 10 ** math.floor(math.log10(minimum_r))
    candidates = sorted(m * decade * scale for scale in (0.1, 1.0, 10.0) for m in e12)
    chosen = next((r for r in candidates if r >= minimum_r), None)
    if chosen is None:
        chosen = minimum_r
    actual_i = (supply_v - led_forward_v) / chosen
    resistor_w = (supply_v - led_forward_v) * actual_i
    return {
        "minimum_resistance_ohm": minimum_r, "recommended_resistance_ohm": chosen,
        "actual_current_ma": actual_i * 1000.0, "resistor_dissipation_w": resistor_w,
        "suggested_power_rating_w": resistor_w * resistor_power_margin,
        "supply_v": supply_v, "led_forward_v": led_forward_v,
        "target_current_ma": target_current_ma,
    }


def rectifier_estimate(transformer_rms_v: float, mains_frequency_hz: float,
                       load_current_ma: float, capacitance_uf: float,
                       topology: str = "Full-wave bridge", diode_drop_v: float = 0.7) -> dict[str, float | str]:
    vals = (transformer_rms_v, mains_frequency_hz, load_current_ma, capacitance_uf, diode_drop_v)
    if any(not math.isfinite(float(v)) for v in vals):
        raise ValueError("Rectifier inputs must be finite.")
    if transformer_rms_v <= 0 or mains_frequency_hz <= 0 or load_current_ma < 0 or capacitance_uf <= 0 or diode_drop_v < 0:
        raise ValueError("RMS voltage, frequency and capacitance must be positive; current/drop cannot be negative.")
    if topology not in {"Half-wave", "Full-wave bridge"}:
        raise ValueError("Choose Half-wave or Full-wave bridge.")
    conducting_drops = 1 if topology == "Half-wave" else 2
    peak = transformer_rms_v * math.sqrt(2.0) - conducting_drops * diode_drop_v
    if peak <= 0:
        raise ValueError("The assumed diode drops exceed the secondary peak voltage.")
    ripple_frequency = mains_frequency_hz if topology == "Half-wave" else 2.0 * mains_frequency_hz
    current_a = load_current_ma / 1000.0
    capacitance_f = capacitance_uf * 1e-6
    ripple_pp = current_a / (ripple_frequency * capacitance_f)
    valley = peak - ripple_pp
    average = peak - ripple_pp / 2.0
    return {
        "topology": topology, "peak_after_drops_v": peak,
        "ripple_frequency_hz": ripple_frequency, "ripple_pp_v": ripple_pp,
        "valley_v": valley, "average_v": average,
        "load_current_ma": load_current_ma, "capacitance_uf": capacitance_uf,
        "transformer_rms_v": transformer_rms_v, "mains_frequency_hz": mains_frequency_hz,
        "diode_drop_v": diode_drop_v,
    }


def rectifier_waveform(result: dict[str, Any], duration_s: float | None = None,
                       samples: int = 1001) -> pd.DataFrame:
    if samples < 101 or samples > 5001:
        raise ValueError("Choose between 101 and 5001 waveform samples.")
    f = float(result["mains_frequency_hz"])
    duration = duration_s if duration_s is not None else 3.0 / f
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Waveform duration must be positive and finite.")
    topology = str(result["topology"])
    n_drops = 1 if topology == "Half-wave" else 2
    peak = float(result["transformer_rms_v"]) * math.sqrt(2.0) - n_drops * float(result["diode_drop_v"])
    ripple_f = float(result["ripple_frequency_hz"])
    ripple = float(result["ripple_pp_v"])
    # Capacitor discharge is approximated as a linear ramp between recharge peaks.
    times = [duration * i / (samples - 1) for i in range(samples)]
    values = []
    for t in times:
        phase = (t * ripple_f) % 1.0
        values.append(peak - ripple * phase)
    return pd.DataFrame({"time_s": times, "output_voltage_v": values})


def build_led_report(result: dict[str, float]) -> str:
    return "\\n".join([
        "# LED series-resistor first-pass calculation", "",
        f'- Supply: {result["supply_v"]:.6g} V',
        f'- Assumed LED forward voltage: {result["led_forward_v"]:.6g} V',
        f'- Target current: {result["target_current_ma"]:.6g} mA',
        f'- Minimum calculated resistance: {result["minimum_resistance_ohm"]:.6g} Ω',
        f'- Suggested E12 resistance (rounded up): {result["recommended_resistance_ohm"]:.6g} Ω',
        f'- Estimated current with suggested resistor: {result["actual_current_ma"]:.6g} mA',
        f'- Estimated resistor dissipation: {result["resistor_dissipation_w"]:.6g} W',
        f'- Suggested minimum power rating using 2x margin: {result["suggested_power_rating_w"]:.6g} W',
        "", "Check the actual LED datasheet, supply tolerance, resistor tolerance, temperature and power-rating derating. This estimate is not a validated design."
    ])


def build_rectifier_report(result: dict[str, Any]) -> str:
    return "\\n".join([
        "# Rectifier and smoothing-capacitor estimate", "",
        f'- Topology: {result["topology"]}',
        f'- Transformer secondary: {result["transformer_rms_v"]:.6g} V RMS at {result["mains_frequency_hz"]:.6g} Hz',
        f'- Load current: {result["load_current_ma"]:.6g} mA',
        f'- Smoothing capacitance: {result["capacitance_uf"]:.6g} µF',
        f'- Estimated peak after assumed diode drops: {result["peak_after_drops_v"]:.6g} V',
        f'- Ripple frequency: {result["ripple_frequency_hz"]:.6g} Hz',
        f'- Estimated ripple: {result["ripple_pp_v"]:.6g} V peak-to-peak',
        f'- Estimated valley voltage: {result["valley_v"]:.6g} V',
        f'- Estimated average output: {result["average_v"]:.6g} V',
        "", "Limitations: first-order capacitor-discharge approximation; assumes ideal transformer and constant load current. Excludes transformer regulation/resistance, diode dynamic resistance and heating, capacitor ESR/ripple-current rating, inrush, mains variation, regulator dropout/transients and thermal effects. Check all component datasheets and use an isolated low-voltage AC source for supervised experiments. Never connect student circuits directly to mains."
    ])


def render_component_lab() -> None:
    st.markdown("### Semiconductor and rectifier laboratory")
    st.caption("Explore diode conduction, LED current limiting, and rectifier smoothing with transparent educational models.")
    diode_tab, led_tab, rect_tab = st.tabs(["Diode characteristics", "LED resistor design", "Rectifier & smoothing"])
    with diode_tab:
        st.markdown("#### Ideal Shockley diode characteristic")
        a, b, c = st.columns(3)
        is_ua = a.number_input("Saturation current (µA)", min_value=0.0000001, value=0.000001, format="%.7g", key="r34_is") * 1e-6
        ideality = b.number_input("Ideality factor n", min_value=0.1, value=2.0, format="%.4g", key="r34_n")
        temp = c.number_input("Temperature (°C)", min_value=-100.0, max_value=200.0, value=25.0, key="r34_temp")
        curve = diode_curve(is_ua, ideality, temp)
        fig, ax = plt.subplots(figsize=(9, 4.2))
        ax.plot(curve["voltage_v"], curve["current_a"] * 1000.0, linewidth=2)
        ax.axhline(0, linewidth=.8)
        ax.axvline(0, linewidth=.8)
        ax.set_xlabel("Diode voltage (V)")
        ax.set_ylabel("Diode current (mA)")
        ax.set_title("Ideal Shockley I–V characteristic")
        ax.grid(True, alpha=.3)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        test_v = st.slider("Inspect diode voltage (V)", min_value=-0.8, max_value=0.85, value=0.65, step=0.01, key="r34_probe")
        test_i = diode_shockley_current(test_v, is_ua, ideality, temp)
        st.metric("Calculated diode current", f"{test_i*1000:.6g} mA")
        st.warning("The Shockley equation here is an ideal educational model. It excludes series resistance, reverse breakdown, junction capacitance, self-heating and manufacturer-specific parameters. High forward currents are not safe operating recommendations.")
    with led_tab:
        st.markdown("#### LED series-resistor calculator")
        a, b, c = st.columns(3)
        supply = a.number_input("Supply voltage (V)", min_value=0.1, value=5.0, key="r34_led_supply")
        vf = b.number_input("LED forward voltage (V)", min_value=0.0, value=2.0, key="r34_led_vf")
        current = c.number_input("Target LED current (mA)", min_value=0.1, value=10.0, key="r34_led_current")
        try:
            led = led_series_resistor(supply, vf, current)
            x, y, z = st.columns(3)
            x.metric("Suggested E12 resistor", f'{led["recommended_resistance_ohm"]:.4g} Ω')
            y.metric("Estimated LED current", f'{led["actual_current_ma"]:.4g} mA')
            z.metric("Resistor dissipation", f'{led["resistor_dissipation_w"]:.4g} W')
            st.code(build_led_report(led))
            st.download_button("Download LED design note", build_led_report(led),
                               file_name="circuitlab_led_resistor_note.md", mime="text/markdown")
        except ValueError as exc:
            st.error(str(exc))
    with rect_tab:
        st.markdown("#### Rectifier and smoothing-capacitor estimator")
        a, b, c = st.columns(3)
        topology = a.selectbox("Rectifier topology", ["Full-wave bridge", "Half-wave"], key="r34_rect_topology")
        secondary = b.number_input("Isolated secondary voltage (V RMS)", min_value=0.1, value=12.0, key="r34_rect_v")
        frequency = c.selectbox("AC frequency (Hz)", [50.0, 60.0], index=0, key="r34_rect_f")
        d, e, f = st.columns(3)
        load = d.number_input("Load current (mA)", min_value=0.0, value=100.0, key="r34_rect_i")
        cap = e.number_input("Smoothing capacitor (µF)", min_value=1.0, value=1000.0, key="r34_rect_c")
        drop = f.number_input("Assumed diode drop (V)", min_value=0.0, value=0.7, key="r34_rect_drop")
        try:
            rect = rectifier_estimate(secondary, frequency, load, cap, topology, drop)
            x, y, z = st.columns(3)
            x.metric("Ripple frequency", f'{rect["ripple_frequency_hz"]:.4g} Hz')
            y.metric("Estimated ripple", f'{rect["ripple_pp_v"]:.4g} V p-p')
            z.metric("Estimated valley", f'{rect["valley_v"]:.4g} V')
            st.write(f'Estimated average output: **{rect["average_v"]:.4g} V**')
            waveform = rectifier_waveform(rect)
            fig, ax = plt.subplots(figsize=(9, 4.2))
            ax.plot(waveform["time_s"], waveform["output_voltage_v"], linewidth=2)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Output voltage (V)")
            ax.set_title("Approximate capacitor-discharge waveform")
            ax.grid(True, alpha=.3)
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.download_button("Export rectifier waveform CSV", waveform.to_csv(index=False).encode("utf-8"),
                               file_name="circuitlab_rectifier_waveform.csv", mime="text/csv")
            report = build_rectifier_report(rect)
            st.download_button("Download rectifier design note", report,
                               file_name="circuitlab_rectifier_estimate.md", mime="text/markdown")
            st.warning("First-pass educational estimate only. Check capacitor voltage and ripple-current ratings, diode surge/average-current ratings, transformer regulation and regulator headroom. Use an isolated low-voltage AC source; never connect this student experiment directly to mains.")
        except ValueError as exc:
            st.error(str(exc))
