"""Release 4.3 — Visual Electronics Learning Engine.

Interactive idealised visual demonstrations. These models are educational and are
not live CircuitJS simulations or physical instrument measurements.
"""
from __future__ import annotations

import math
from typing import Any


def _finite_positive(value: float, label: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be a finite positive value.")


def ohmic_circuit(voltage_v: float, resistance_ohm: float) -> dict[str, float]:
    if not math.isfinite(voltage_v) or voltage_v < 0:
        raise ValueError("Voltage must be finite and non-negative.")
    _finite_positive(resistance_ohm, "Resistance")
    current = voltage_v / resistance_ohm
    return {"current_a": current, "power_w": voltage_v * current,
            "resistor_drop_v": voltage_v}


def voltage_drop_series(source_v: float, resistances: list[float]) -> list[dict[str, float | str]]:
    if not math.isfinite(source_v) or source_v < 0 or not resistances:
        raise ValueError("Use a non-negative finite source and at least one resistor.")
    for r in resistances:
        _finite_positive(r, "Each resistance")
    total = sum(resistances)
    current = source_v / total
    return [{"reference": f"R{i+1}", "resistance_ohm": r,
             "current_a": current, "drop_v": current*r,
             "power_w": current*current*r} for i, r in enumerate(resistances)]


def diode_current(voltage_v: float, saturation_a: float = 1e-12,
                  ideality: float = 1.8, temperature_c: float = 25.0) -> float:
    if not all(math.isfinite(x) for x in (voltage_v, saturation_a, ideality, temperature_c)):
        raise ValueError("All diode parameters must be finite.")
    _finite_positive(saturation_a, "Saturation current")
    _finite_positive(ideality, "Ideality factor")
    kelvin = temperature_c + 273.15
    _finite_positive(kelvin, "Absolute temperature")
    vt = 1.380649e-23 * kelvin / 1.602176634e-19
    exponent = max(-100.0, min(40.0, voltage_v/(ideality*vt)))
    return saturation_a * math.expm1(exponent)


def diode_curve(start_v: float = -0.2, stop_v: float = 0.8, points: int = 201,
                saturation_a: float = 1e-12, ideality: float = 1.8,
                temperature_c: float = 25.0) -> list[dict[str, float]]:
    if not math.isfinite(start_v) or not math.isfinite(stop_v) or stop_v <= start_v or points < 2:
        raise ValueError("Voltage range must increase and contain at least two points.")
    return [{"voltage_v": start_v+(stop_v-start_v)*i/(points-1),
             "current_a": diode_current(start_v+(stop_v-start_v)*i/(points-1),
                                        saturation_a, ideality, temperature_c)}
            for i in range(points)]


def transistor_switch(v_supply: float, load_ohm: float, control_on: bool,
                      saturation_v: float = 0.2) -> dict[str, float | str | bool]:
    if not all(math.isfinite(x) for x in (v_supply, load_ohm, saturation_v)) or v_supply < 0 or saturation_v < 0:
        raise ValueError("Supply and saturation voltage must be finite and non-negative.")
    _finite_positive(load_ohm, "Load resistance")
    if control_on:
        drop = min(saturation_v, v_supply)
        current = max(0.0, v_supply-drop)/load_ohm
        return {"state":"ON (idealised saturated switch)","on":True,
                "load_current_a":current,"switch_drop_v":drop,
                "load_voltage_v":v_supply-drop,"load_power_w":current*current*load_ohm}
    return {"state":"OFF (open-switch approximation)","on":False,
            "load_current_a":0.0,"switch_drop_v":v_supply,
            "load_voltage_v":0.0,"load_power_w":0.0}


def capacitor_response(source_v: float, resistance_ohm: float,
                       capacitance_f: float, duration_tau: float = 5.0,
                       points: int = 201) -> list[dict[str, float]]:
    if not math.isfinite(source_v) or source_v < 0:
        raise ValueError("Source voltage must be finite and non-negative.")
    _finite_positive(resistance_ohm, "Resistance")
    _finite_positive(capacitance_f, "Capacitance")
    _finite_positive(duration_tau, "Duration in time constants")
    if points < 2:
        raise ValueError("At least two waveform points are required.")
    tau = resistance_ohm * capacitance_f
    output = []
    for i in range(points):
        t = duration_tau*tau*i/(points-1)
        v = source_v*(1-math.exp(-t/tau))
        output.append({"time_s":t,"capacitor_voltage_v":v,
                       "resistor_voltage_v":source_v-v})
    return output


def build_visual_lab_report(title: str, values: dict[str, Any]) -> str:
    lines=[f"# {title}","",
           "Educational model only; not live CircuitJS or physical measurement.",""]
    for key,value in values.items():
        lines.append(f"- **{key.replace('_',' ').title()}:** {value}")
    return "\n".join(lines)


def _schematic_svg(kind: str, current_on: bool = True) -> str:
    # SVG is deliberately self-contained so the diagrams work without image hosting.
    if kind == "series":
        return """<svg viewBox="0 0 640 180" role="img" aria-label="Series resistor circuit" style="width:100%;height:auto">
        <g fill="none" stroke="#d6e4ee" stroke-width="4" stroke-linejoin="round">
        <path d="M90 90 V35 H170 l12 -12 20 24 20 -24 20 24 20 -24 20 24 12 -12 H520 V145 H90 V90"/>
        <path d="M90 70 V110 M75 78 H105 M80 102 H100"/>
        </g><g fill="#72e2d4" font-size="17" font-family="sans-serif"><text x="190" y="15">R1</text><text x="365" y="15">R2</text><text x="40" y="135">DC</text><text x="525" y="95">I →</text></g></svg>"""
    if kind == "diode":
        return """<svg viewBox="0 0 640 170" role="img" aria-label="Diode symbol and bias direction" style="width:100%;height:auto">
        <g stroke="#d6e4ee" stroke-width="4" fill="none"><path d="M75 85 H250 M390 85 H565"/><path d="M250 45 L250 125 L370 85 Z" fill="#72e2d4" stroke="#72e2d4"/><path d="M390 42 V128"/></g>
        <g fill="#72e2d4" font-size="18" font-family="sans-serif"><text x="70" y="45">Anode</text><text x="485" y="45">Cathode</text><text x="265" y="155">Conventional forward direction →</text></g></svg>"""
    state = "#72e2d4" if current_on else "#f59e0b"
    label = "ON" if current_on else "OFF"
    return f"""<svg viewBox="0 0 640 190" role="img" aria-label="Low-side transistor switch {label}" style="width:100%;height:auto">
    <g stroke="#d6e4ee" stroke-width="4" fill="none"><path d="M160 35 V65 H270 M160 65 V95 M160 95 H270 V125 H160 V160 H480 V35 H160"/>
    <path d="M270 65 L320 95 L270 125 M320 95 H400 V35"/></g>
    <path d="M160 95 H270" stroke="{state}" stroke-width="7"/>
    <g fill="{state}" font-size="19" font-family="sans-serif"><text x="110" y="25">+V</text><text x="330" y="145">Switch {label}</text><text x="425" y="25">Load</text></g></svg>"""


def render_visual_learning_engine() -> None:
    import streamlit as st
    import pandas as pd

    st.markdown("""
    <div style="padding:22px 26px;border-radius:18px;background:linear-gradient(115deg,#101d32,#155c68);color:#f4fbff;margin-bottom:16px">
      <div style="letter-spacing:.14em;font-size:.72rem;color:#72e2d4;font-weight:700">RELEASE 4.3 · VISUAL ELECTRONICS ENGINE</div>
      <h2 style="color:#f4fbff;margin:.35rem 0">See what the circuit is doing.</h2>
      <p style="color:#d4e7ed;margin:0">Change circuit parameters and explore current, voltage drops, semiconductor behaviour and transient response.</p>
    </div>
    """,unsafe_allow_html=True)
    st.info("All demonstrations are idealised mathematical teaching models. They are not live CircuitJS simulations, measured physical data or safety certification.")
    tabs=st.tabs(["Current flow & voltage drops","Diode behaviour","Transistor switching","Capacitor charging"])
    with tabs[0]:
        st.subheader("Series circuit: one current, shared voltage")
        st.markdown(_schematic_svg("series"),unsafe_allow_html=True)
        a,b,c=st.columns(3)
        voltage=a.number_input("Supply voltage (V)",min_value=0.0,value=12.0,step=0.5,key="r43_series_v")
        r1=b.number_input("R1 (Ω)",min_value=0.1,value=1000.0,step=100.0,key="r43_series_r1")
        r2=c.number_input("R2 (Ω)",min_value=0.1,value=2000.0,step=100.0,key="r43_series_r2")
        result=voltage_drop_series(voltage,[r1,r2])
        st.metric("Same series current",f"{result[0]['current_a']*1000:.4g} mA")
        frame=pd.DataFrame([{"Component":x["reference"],"Voltage drop (V)":x["drop_v"],"Power (W)":x["power_w"]} for x in result]).set_index("Component")
        st.dataframe(frame,use_container_width=True)
        st.bar_chart(frame[["Voltage drop (V)"]])
        st.caption(f"KVL check: source {voltage:.4g} V = total resistor drops {sum(float(x['drop_v']) for x in result):.4g} V.")
        st.download_button("Download voltage-drop data",frame.reset_index().to_csv(index=False),file_name="series_voltage_drops.csv",mime="text/csv")
    with tabs[1]:
        st.subheader("Diode: forward and reverse bias")
        st.markdown(_schematic_svg("diode"),unsafe_allow_html=True)
        a,b,c=st.columns(3)
        v=a.slider("Diode voltage (V)",min_value=-0.5,max_value=0.8,value=0.2,step=0.01,key="r43_diode_v")
        temp=b.slider("Temperature (°C)",min_value=0,max_value=100,value=25,key="r43_diode_t")
        ideality=c.slider("Ideality factor",min_value=1.0,max_value=2.5,value=1.8,step=0.1,key="r43_diode_n")
        current=diode_current(v,1e-12,ideality,float(temp))
        st.metric("Shockley-model current",f"{current*1e6:.5g} µA")
        curve=diode_curve(-0.5,0.8,261,1e-12,ideality,float(temp))
        chart=pd.DataFrame(curve).set_index("voltage_v")
        st.line_chart(chart)
        st.caption("The Shockley equation omits series resistance, reverse breakdown, junction capacitance, self-heating and high-level injection. The exponential is numerically bounded.")
        st.write("Reverse bias: this simplified model predicts a small reverse saturation current. Forward bias: current rises exponentially in the idealised model.")
        st.download_button("Download diode I–V data",pd.DataFrame(curve).to_csv(index=False),file_name="diode_iv_curve.csv",mime="text/csv")
    with tabs[2]:
        st.subheader("Transistor as a low-side switch")
        on=st.toggle("Apply control signal (switch ON)",value=True,key="r43_transistor_on")
        st.markdown(_schematic_svg("transistor",on),unsafe_allow_html=True)
        a,b=st.columns(2)
        supply=a.number_input("Supply voltage (V)",min_value=0.0,value=9.0,step=0.5,key="r43_transistor_v")
        load=b.number_input("Load resistance (Ω)",min_value=1.0,value=100.0,step=10.0,key="r43_transistor_r")
        result=transistor_switch(supply,load,on)
        x,y,z=st.columns(3)
        x.metric("Switch state",str(result["state"]))
        y.metric("Load current",f"{float(result['load_current_a'])*1000:.4g} mA")
        z.metric("Load voltage",f"{float(result['load_voltage_v']):.4g} V")
        st.caption("This is a low-side switch analogy using a fixed saturation-drop approximation. It does not calculate base/gate drive, switching transients, SOA or device heating.")
    with tabs[3]:
        st.subheader("Capacitor: charging over time")
        a,b,c=st.columns(3)
        source=a.number_input("DC source (V)",min_value=0.0,value=5.0,step=0.5,key="r43_rc_v")
        resistance=b.number_input("Series resistance (Ω)",min_value=1.0,value=10000.0,step=1000.0,key="r43_rc_r")
        capacitance=c.number_input("Capacitance (µF)",min_value=1.0,value=100.0,step=10.0,key="r43_rc_c")
        tau=resistance*capacitance*1e-6
        data=capacitor_response(source,resistance,capacitance*1e-6)
        frame=pd.DataFrame(data).set_index("time_s")
        st.metric("Time constant τ = RC",f"{tau:.5g} s")
        st.line_chart(frame)
        st.caption(f"At one time constant ({tau:.4g} s), ideal capacitor voltage is {source*(1-math.exp(-1)):.4g} V, or 63.2% of the final value.")
        st.download_button("Download charging waveform",frame.reset_index().to_csv(index=False),file_name="capacitor_charging.csv",mime="text/csv")
    st.warning("For physical experiments, use only instructor-approved, isolated, current-limited low-voltage equipment. De-energise before rewiring. Never connect student-built circuits directly to mains.")
