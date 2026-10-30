"""Release 4.1 — Interactive Electronics Classroom."""
from __future__ import annotations

import math
from typing import Any

CLASSROOMS: dict[str, dict[str, Any]] = {
    "ohms_law": {
        "title": "Ohm's law: from prediction to measurement",
        "level": "Foundation",
        "goal": "Predict the current and power in a resistive DC circuit, then check the result.",
        "steps": [
            ("Start with the circuit", "A DC source is connected to a single resistor. The resistor is the load; the source establishes the potential difference."),
            ("Identify known quantities", "Record source voltage in volts (V) and resistance in ohms (Ω). Convert prefixes before substituting values."),
            ("Predict current", "For an ohmic resistor, I = V/R. Current is the rate of charge flow and is measured in amperes (A)."),
            ("Check power", "P = VI = I²R = V²/R. Compare calculated dissipation with the component's rated power and operating conditions."),
            ("Verify safely", "Use an isolated, current-limited low-voltage supply. Connect an ammeter in series and a voltmeter in parallel; de-energise before changing connections.")
        ],
        "equations": ["I = V/R", "P = VI", "P = I²R = V²/R"],
        "activity": "Change the resistance while keeping voltage fixed. Predict whether current increases or decreases before reading the calculated result.",
        "questions": [
            {"q":"A 12 V source is across 3 kΩ. Current?","options":["4 mA","36 mA","0.25 mA","4 A"],"answer":0,"why":"12/3000 = 0.004 A = 4 mA.","level":"Foundation"},
            {"q":"If resistance doubles at fixed voltage, current will…","options":["Double","Halve","Stay constant","Become zero"],"answer":1,"why":"I=V/R, so doubling R halves I.","level":"Foundation"},
            {"q":"A 1 kΩ resistor carries 20 mA. Its power is…","options":["0.4 W","2 W","20 W","0.02 W"],"answer":0,"why":"P=I²R=(0.02)²×1000=0.4 W.","level":"Intermediate"}
        ]
    },
    "voltage_divider": {
        "title": "Voltage divider: calculate and investigate loading",
        "level": "Foundation → intermediate",
        "goal": "Calculate the output of a two-resistor divider and understand why a load changes it.",
        "steps": [
            ("Understand the arrangement", "R1 and R2 are in series across Vin. The output is measured across R2."),
            ("Calculate the unloaded output", "Vout = Vin × R2/(R1+R2). The same current flows through both series resistors."),
            ("Introduce a load", "A load connected across R2 is in parallel with R2. The effective lower resistance becomes R2 || RL."),
            ("Recalculate", "Use Rlower = (R2×RL)/(R2+RL), then Vout = Vin × Rlower/(R1+Rlower)."),
            ("Interpret the result", "A lower load resistance draws current and usually reduces the output voltage. Check resistor power and source loading.")
        ],
        "equations": ["Vout(unloaded) = Vin × R2/(R1+R2)", "Rlower = R2 || RL", "Vout(loaded) = Vin × Rlower/(R1+Rlower)"],
        "activity": "Move the load resistance from very high to low. Observe how output voltage changes and explain the cause.",
        "questions": [
            {"q":"Vin=10 V, R1=R2. Unloaded Vout?","options":["2.5 V","5 V","10 V","20 V"],"answer":1,"why":"Equal divider resistors split the voltage equally.","level":"Foundation"},
            {"q":"Adding a finite load across R2 usually makes Vout…","options":["Increase","Decrease","Exactly double","Independent of RL"],"answer":1,"why":"The load is parallel with R2, reducing the lower-leg equivalent resistance.","level":"Intermediate"},
            {"q":"A 2 kΩ and 2 kΩ divider has a 2 kΩ load across the lower resistor. What is Vout/Vin?","options":["1/2","1/3","2/3","1/4"],"answer":1,"why":"Rlower=2k||2k=1k; ratio=1/(2+1)=1/3.","level":"Advanced"}
        ]
    },
    "rc_transient": {
        "title": "RC charging: read the transient waveform",
        "level": "Intermediate",
        "goal": "Predict a capacitor charging curve and relate its shape to the time constant.",
        "steps": [
            ("Identify the energy-storage element", "A capacitor stores energy in an electric field. Its voltage cannot change instantaneously in the ideal finite-current model."),
            ("Calculate the time constant", "For a simple series RC circuit, τ=RC. Use ohms and farads to obtain seconds."),
            ("Predict the response", "For a zero-initial-voltage capacitor charged from a DC step, vC(t)=Vs(1−e^(−t/RC))."),
            ("Read the waveform", "At t=τ, the capacitor reaches approximately 63.2% of the final voltage. At about 5τ it is close to its final value."),
            ("Challenge the model", "Real capacitors have tolerance, leakage and ESR. Source resistance and measurement loading can change the observed response.")
        ],
        "equations": ["τ = RC", "vC(t) = Vs(1−e^(−t/RC))", "vC(τ) ≈ 0.632 Vs"],
        "activity": "Change R or C. Predict the new time constant and identify the time at which the capacitor reaches 63.2% of its final voltage.",
        "questions": [
            {"q":"R=10 kΩ and C=100 µF. τ?","options":["0.1 s","1 s","10 s","100 s"],"answer":1,"why":"10000×0.0001=1 second.","level":"Intermediate"},
            {"q":"At one time constant, charging voltage is approximately…","options":["36.8%","50%","63.2%","99.9%"],"answer":2,"why":"1−e⁻¹≈0.632.","level":"Intermediate"},
            {"q":"If capacitance doubles and resistance is unchanged, τ…","options":["Halves","Doubles","Does not change","Becomes zero"],"answer":1,"why":"τ=RC, so doubling C doubles τ.","level":"Advanced"}
        ]
    },
    "kirchhoff": {
        "title": "Kirchhoff's laws: reason about a network",
        "level": "Intermediate",
        "goal": "Use current and voltage conservation to analyse a simple DC network.",
        "steps": [
            ("Choose a reference direction", "Assign current directions and voltage polarities. A negative answer means the actual direction is opposite to the chosen reference."),
            ("Apply KCL", "At a node, the algebraic sum of currents is zero. Current entering equals current leaving."),
            ("Apply KVL", "Around a closed loop, the algebraic sum of voltage rises and drops is zero."),
            ("Solve the network", "Combine Kirchhoff's laws with component relationships such as V=IR."),
            ("Check consistency", "Verify units, signs and that calculated current and voltage satisfy both node and loop equations.")
        ],
        "equations": ["ΣI(node) = 0", "ΣV(closed loop) = 0", "V = IR"],
        "activity": "A node receives 8 mA and has two outgoing branches. If one branch carries 3 mA, calculate the other branch current.",
        "questions": [
            {"q":"A node has 8 mA entering and 3 mA leaving. Remaining outgoing current?","options":["5 mA","11 mA","−5 mA","24 mA"],"answer":0,"why":"KCL: 8=3+I, so I=5 mA.","level":"Foundation"},
            {"q":"A loop has a 12 V rise and drops of 7 V and 5 V. KVL sum?","options":["24 V","5 V","0 V","−12 V"],"answer":2,"why":"12−7−5=0 V.","level":"Intermediate"},
            {"q":"A negative branch current after solving usually means…","options":["KCL is invalid","Actual direction is opposite the reference","The resistor has negative resistance","The source is disconnected"],"answer":1,"why":"The sign reports direction relative to your assumed reference.","level":"Advanced"}
        ]
    }
}


def divider_result(vin: float, r1: float, r2: float, load: float | None = None) -> dict[str, float]:
    if not all(math.isfinite(x) for x in (vin, r1, r2)) or vin < 0 or r1 <= 0 or r2 <= 0:
        raise ValueError("Use finite values, non-negative Vin and positive resistor values.")
    if load is not None and (not math.isfinite(load) or load <= 0):
        raise ValueError("Load resistance must be positive.")
    lower = r2 if load is None else r2 * load / (r2 + load)
    current = vin / (r1 + lower)
    return {"unloaded_v": vin * r2 / (r1 + r2), "loaded_v": current * lower,
            "series_current_a": current, "lower_equivalent_ohm": lower,
            "r1_power_w": current**2 * r1, "r2_power_w": (current*lower/r2)**2*r2}


def rc_waveform(resistance_ohm: float, capacitance_f: float, source_v: float, points: int = 101) -> list[dict[str,float]]:
    if not all(math.isfinite(x) for x in (resistance_ohm, capacitance_f, source_v)) or resistance_ohm <= 0 or capacitance_f <= 0 or source_v < 0:
        raise ValueError("R and C must be positive; source voltage must be non-negative.")
    tau = resistance_ohm * capacitance_f
    return [{"time_s": 5*tau*i/(points-1), "voltage_v": source_v*(1-math.exp(-5*i/(points-1)))}
            for i in range(points)]


def quiz_feedback(question: dict[str,Any], selected: str) -> dict[str,Any]:
    if selected not in question["options"]:
        raise ValueError("Select one of the listed options.")
    correct = question["options"].index(selected) == question["answer"]
    return {"correct":correct,"explanation":question["why"],"level":question["level"]}


def render_interactive_classroom() -> None:
    import streamlit as st
    import pandas as pd

    st.markdown("""
    <div style="padding:22px 26px;border-radius:18px;background:linear-gradient(115deg,#101d32,#155c68);color:#f4fbff;margin-bottom:16px">
      <div style="letter-spacing:.14em;font-size:.72rem;color:#72e2d4;font-weight:700">RELEASE 4.1 · INTERACTIVE CLASSROOM</div>
      <h2 style="color:#f4fbff;margin:.35rem 0">Learn it. Predict it. Experiment with it.</h2>
      <p style="color:#d4e7ed;margin:0">Guided lessons, live parameter experiments, visual models and adaptive knowledge checks.</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("These are idealised educational models. They are not measurements from physical hardware or a substitute for your current module guide.")
    lesson_ids=list(CLASSROOMS)
    selected=st.selectbox("Choose a classroom",lesson_ids,format_func=lambda x:CLASSROOMS[x]["title"],key="r41_classroom")
    lesson=CLASSROOMS[selected]
    st.caption(f"Level: {lesson['level']} · {lesson['goal']}")
    lesson_tab,experiment_tab,quiz_tab=st.tabs(["Guided lesson","Interactive experiment","Knowledge check"])
    with lesson_tab:
        step_key=f"r41_step_{selected}"
        step=st.session_state.get(step_key,0)
        step=max(0,min(step,len(lesson["steps"])-1))
        st.progress((step+1)/len(lesson["steps"]),text=f"Step {step+1} of {len(lesson['steps'])}")
        heading,body=lesson["steps"][step]
        st.subheader(heading)
        st.write(body)
        st.markdown("**Key equations**")
        for eq in lesson["equations"]: st.code(eq)
        left,right=st.columns(2)
        with left:
            if st.button("← Previous",disabled=step==0,key=f"r41_prev_{selected}"):
                st.session_state[step_key]=step-1
                st.rerun()
        with right:
            if st.button("Next step →",disabled=step==len(lesson["steps"])-1,key=f"r41_next_{selected}"):
                st.session_state[step_key]=step+1
                st.rerun()
        if step==len(lesson["steps"])-1:
            st.success("Guided lesson complete. Continue to the experiment and knowledge check.")
        st.download_button("Download guided lesson", "\n".join([f"# {lesson['title']}","",lesson["goal"],""]+[f"## {h}\n{b}" for h,b in lesson["steps"]]+["## Equations"]+lesson["equations"]+["## Activity",lesson["activity"]]), file_name=f"circuitlab_{selected}_classroom.md",mime="text/markdown")
    with experiment_tab:
        if selected=="voltage_divider":
            c1,c2,c3=st.columns(3)
            vin=c1.number_input("Input voltage (V)",min_value=0.1,value=12.0,step=0.5,key="r41_vin")
            r1=c2.number_input("R1 (Ω)",min_value=1.0,value=1000.0,step=100.0,key="r41_r1")
            r2=c3.number_input("R2 (Ω)",min_value=1.0,value=1000.0,step=100.0,key="r41_r2")
            use_load=st.checkbox("Connect a load across R2",key="r41_use_load")
            load=st.number_input("Load resistance (Ω)",min_value=1.0,value=2000.0,step=100.0,key="r41_load",disabled=not use_load)
            result=divider_result(vin,r1,r2,load if use_load else None)
            a,b,c=st.columns(3)
            a.metric("Unloaded Vout",f"{result['unloaded_v']:.4g} V")
            b.metric("Actual Vout",f"{result['loaded_v']:.4g} V")
            c.metric("Divider current",f"{result['series_current_a']*1000:.4g} mA")
            st.caption(f"Effective lower-leg resistance: {result['lower_equivalent_ohm']:.4g} Ω")
            st.bar_chart(pd.DataFrame({"Voltage (V)":[vin,result["loaded_v"]]},index=["Input","Output"]))
            st.write("Prediction: adding a finite load across R2 changes the lower-leg equivalent resistance and normally lowers Vout.")
        elif selected=="rc_transient":
            c1,c2,c3=st.columns(3)
            resistance=c1.number_input("Resistance (Ω)",min_value=1.0,value=10000.0,step=1000.0,key="r41_rc_r")
            capacitance=c2.number_input("Capacitance (µF)",min_value=1.0,value=100.0,step=10.0,key="r41_rc_c")
            source=c3.number_input("Source voltage (V)",min_value=0.1,value=5.0,step=0.5,key="r41_rc_v")
            data=rc_waveform(resistance,capacitance*1e-6,source)
            tau=resistance*capacitance*1e-6
            st.metric("Time constant τ",f"{tau:.5g} s")
            frame=pd.DataFrame(data).set_index("time_s")
            st.caption("Horizontal axis: time (s) · Vertical axis: capacitor voltage (V)")
            st.line_chart(frame,y="voltage_v")
            st.write(f"At τ = {tau:.4g} s, the ideal capacitor voltage is approximately {source*(1-math.exp(-1)):.4g} V (63.2% of the final value).")
            st.download_button("Download waveform CSV",frame.reset_index().to_csv(index=False),file_name="rc_charging_waveform.csv",mime="text/csv")
        elif selected=="ohms_law":
            c1,c2=st.columns(2)
            voltage=c1.number_input("Supply voltage (V)",min_value=0.0,value=9.0,step=0.5,key="r41_ohm_v")
            resistance=c2.number_input("Resistance (Ω)",min_value=1.0,value=1000.0,step=100.0,key="r41_ohm_r")
            current=voltage/resistance
            power=voltage*current
            a,b,c=st.columns(3)
            a.metric("Current",f"{current*1000:.4g} mA")
            b.metric("Power",f"{power*1000:.4g} mW")
            c.metric("Resistance",f"{resistance:,.4g} Ω")
            st.write(f"Predicted current is {current*1000:.4g} mA. The calculation assumes an ohmic resistor and ideal source.")
        else:
            incoming=st.number_input("Current entering node (mA)",min_value=0.0,value=8.0,step=0.5,key="r41_kcl_in")
            outgoing=st.number_input("Known current leaving node (mA)",min_value=0.0,value=3.0,step=0.5,key="r41_kcl_out")
            remaining=incoming-outgoing
            st.metric("Other branch current",f"{remaining:.4g} mA")
            st.write("KCL check: entering current = sum of leaving currents. A negative result means the assumed branch direction is reversed.")
    with quiz_tab:
        difficulty=st.select_slider("Question difficulty",options=["Foundation","Intermediate","Advanced"],value="Foundation",key="r41_difficulty")
        eligible=[q for q in lesson["questions"] if q["level"]==difficulty]
        if not eligible:
            eligible=lesson["questions"]
            st.caption("This lesson has no question at that exact level yet; showing its available questions.")
        for i,q in enumerate(eligible):
            key=f"r41_answer_{selected}_{difficulty}_{i}"
            answer=st.radio(q["q"],q["options"],key=key)
            if st.button("Check answer",key=f"r41_check_{selected}_{difficulty}_{i}"):
                feedback=quiz_feedback(q,answer)
                if feedback["correct"]: st.success("Correct. "+feedback["explanation"])
                else: st.error("Not quite. "+feedback["explanation"])
                st.session_state[f"r41_feedback_{selected}_{difficulty}_{i}"]=feedback
            feedback=st.session_state.get(f"r41_feedback_{selected}_{difficulty}_{i}")
            if feedback: st.caption(("Correct" if feedback["correct"] else "Review this concept")+" · "+feedback["explanation"])
    st.caption("For physical work, use approved, supervised, isolated and current-limited low-voltage equipment. De-energise before rewiring. Never connect student-built circuits directly to mains.")
