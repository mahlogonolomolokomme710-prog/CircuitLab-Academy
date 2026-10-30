"""Release 3.3 — first-order transient laboratory and virtual instruments.

Analytical step-response models for ideal series RC and RL circuits.
These are educational first-order models, not a general transient SPICE solver.
"""
from __future__ import annotations

import math
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def simulate_first_order(kind: str, resistance_ohm: float, energy_element: float,
                         source_voltage: float, duration_s: float,
                         initial_value: float = 0.0, samples: int = 501) -> dict[str, Any]:
    """Return ideal series RC capacitor-voltage or RL inductor-current step response."""
    kind = str(kind).strip().upper()
    values = [resistance_ohm, energy_element, source_voltage, duration_s, initial_value]
    if any(not math.isfinite(float(v)) for v in values):
        raise ValueError("All inputs must be finite numbers.")
    if kind not in {"RC", "RL"}:
        raise ValueError("Choose RC or RL.")
    if resistance_ohm <= 0 or energy_element <= 0 or duration_s <= 0:
        raise ValueError("Resistance, capacitance/inductance and duration must be greater than zero.")
    if samples < 51 or samples > 5001:
        raise ValueError("Sample count must be between 51 and 5001.")
    tau = resistance_ohm * energy_element if kind == "RC" else energy_element / resistance_ohm
    if not math.isfinite(tau) or tau <= 0:
        raise ValueError("The calculated time constant is outside the supported numeric range.")
    times = [duration_s * i / (samples - 1) for i in range(samples)]
    decay = [math.exp(-t / tau) for t in times]
    if kind == "RC":
        final_value = source_voltage
        response = [final_value + (initial_value - final_value) * e for e in decay]
        current = [(source_voltage - v) / resistance_ohm for v in response]
        response_label, response_unit = "Capacitor voltage", "V"
        secondary_label, secondary_unit = "Series current", "A"
        initial_valid = abs(initial_value) < 1e12
    else:
        final_value = source_voltage / resistance_ohm
        response = [final_value + (initial_value - final_value) * e for e in decay]
        current = response[:]
        response_label, response_unit = "Inductor current", "A"
        secondary_label, secondary_unit = "Inductor current", "A"
        initial_valid = abs(initial_value) < 1e12
    if not initial_valid or any(not math.isfinite(v) for v in response):
        raise ValueError("The initial condition or resulting response is outside the supported range.")
    return {
        "kind": kind, "tau_s": tau, "times_s": times, "response": response,
        "current": current, "final_value": final_value,
        "response_label": response_label, "response_unit": response_unit,
        "secondary_label": secondary_label, "secondary_unit": secondary_unit,
        "resistance_ohm": resistance_ohm, "energy_element": energy_element,
        "source_voltage": source_voltage, "initial_value": initial_value,
        "duration_s": duration_s,
    }


def sample_at(result: dict[str, Any], time_s: float) -> dict[str, float]:
    """Return an interpolated ideal measurement at the requested time."""
    times = result["times_s"]
    if not math.isfinite(float(time_s)) or time_s < 0 or time_s > times[-1]:
        raise ValueError("Cursor time must be within the displayed time range.")
    position = time_s / times[-1] * (len(times) - 1)
    lo = int(math.floor(position))
    hi = min(lo + 1, len(times) - 1)
    fraction = position - lo
    response = result["response"][lo] + fraction * (result["response"][hi] - result["response"][lo])
    current = result["current"][lo] + fraction * (result["current"][hi] - result["current"][lo])
    return {"time_s": time_s, "response": response, "current_a": current}


def waveform_frame(result: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame({
        "time_s": result["times_s"],
        "response": result["response"],
        "series_current_a": result["current"],
    })


def build_transient_report(result: dict[str, Any], cursor: dict[str, float]) -> str:
    return "\n".join([
        "# CircuitLab Academy — first-order transient report", "",
        f'- Model: ideal series {result["kind"]} step response',
        f'- Resistance: {result["resistance_ohm"]:.8g} Ω',
        f'- {"Capacitance" if result["kind"]=="RC" else "Inductance"}: {result["energy_element"]:.8g} {"F" if result["kind"]=="RC" else "H"}',
        f'- Source step: {result["source_voltage"]:.8g} V',
        f'- Initial {"capacitor voltage" if result["kind"]=="RC" else "inductor current"}: {result["initial_value"]:.8g} {"V" if result["kind"]=="RC" else "A"}',
        f'- Time constant: {result["tau_s"]:.8g} s',
        f'- Final value: {result["final_value"]:.8g} {result["response_unit"]}',
        "", "## Virtual instrument cursor",
        f'- Time: {cursor["time_s"]:.8g} s',
        f'- {result["response_label"]}: {cursor["response"]:.8g} {result["response_unit"]}',
        f'- Series current: {cursor["current_a"]:.8g} A',
        "", "## Model limitations",
        "Analytical first-order ideal series circuit. Assumes a constant ideal step source and constant component values. Excludes parasitic resistance/inductance, capacitor leakage/ESR, inductor saturation/core losses, switching effects, nonlinear devices, noise, probe loading and measurement uncertainty. Not a general SPICE transient solver or a physical measurement.", ""
    ])


def render_transient_lab() -> None:
    st.markdown("### Transient laboratory · RC and RL step response")
    st.caption("Explore how energy-storage components respond over time. Choose an ideal series circuit and apply a DC step.")
    a, b, c = st.columns(3)
    kind = a.selectbox("Circuit model", ["RC", "RL"], format_func=lambda x: "Series RC · capacitor charging" if x=="RC" else "Series RL · inductor current rise", key="r33_kind")
    resistance = b.number_input("Resistance (Ω)", min_value=0.001, value=1000.0, format="%.6g", key="r33_r")
    if kind == "RC":
        element = c.number_input("Capacitance (µF)", min_value=0.001, value=100.0, format="%.6g", key="r33_c") * 1e-6
        initial_label = "Initial capacitor voltage (V)"
    else:
        element = c.number_input("Inductance (mH)", min_value=0.001, value=100.0, format="%.6g", key="r33_l") * 1e-3
        initial_label = "Initial inductor current (A)"
    d, e, f = st.columns(3)
    source = d.number_input("DC step voltage (V)", value=5.0, format="%.6g", key="r33_source")
    initial = e.number_input(initial_label, value=0.0, format="%.6g", key="r33_initial")
    duration = f.number_input("Displayed time (s)", min_value=0.000001, value=0.5, format="%.6g", key="r33_duration")
    try:
        result = simulate_first_order(kind, resistance, element, source, duration, initial)
    except ValueError as exc:
        st.error(str(exc))
        return
    tau = result["tau_s"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Time constant τ", f"{tau:.6g} s")
    m2.metric("Final response", f'{result["final_value"]:.6g} {result["response_unit"]}')
    m3.metric("Approx. 5τ settling time", f"{5*tau:.6g} s")
    st.caption("At one time constant, a first-order step response has completed approximately 63.2% of its total change. Five time constants corresponds to approximately 99.3%.")
    frame = waveform_frame(result)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.plot(frame["time_s"], frame["response"], label=result["response_label"], linewidth=2.4)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(f'{result["response_label"]} ({result["response_unit"]})')
    ax.grid(True, alpha=.3)
    ax.legend()
    ax.set_title(f'Ideal series {kind} step response')
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown("#### Virtual oscilloscope")
    st.caption("Channel A displays the capacitor voltage (RC) or inductor current (RL). The cursor reports an interpolated reading; this is a calculated model value, not a real instrument measurement.")
    cursor_time = st.slider("Time cursor (s)", min_value=0.0, max_value=float(duration), value=float(duration)*0.5, key="r33_cursor")
    reading = sample_at(result, cursor_time)
    x, y, z = st.columns(3)
    x.metric("Cursor time", f'{reading["time_s"]:.6g} s')
    y.metric(result["response_label"], f'{reading["response"]:.6g} {result["response_unit"]}')
    z.metric("Series current", f'{reading["current_a"]:.6g} A')
    st.markdown("#### Virtual digital multimeter")
    st.write("At the selected cursor time, the ideal model predicts:")
    st.code(f'{result["response_label"]}: {reading["response"]:.6g} {result["response_unit"]}\nSeries current: {reading["current_a"]:.6g} A')
    st.download_button("Export waveform samples (CSV)", frame.to_csv(index=False).encode("utf-8"),
                       file_name=f"circuitlab_{kind.lower()}_waveform.csv", mime="text/csv")
    st.download_button("Download transient analysis report",
                       build_transient_report(result, reading),
                       file_name=f"circuitlab_{kind.lower()}_transient_report.md", mime="text/markdown")
    with st.expander("View waveform data"):
        st.dataframe(frame, use_container_width=True, hide_index=True)
    st.warning("Educational analytical model only. This virtual oscilloscope and multimeter do not connect to physical hardware or read live CircuitJS measurements. Confirm real circuit behaviour with appropriately rated equipment and supervised lab procedures.")
