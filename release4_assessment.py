"""Release 4.2 — Engineering Assessment Centre and Practical Laboratory."""
from __future__ import annotations

from typing import Any

ASSESSMENTS: dict[str, list[dict[str, Any]]] = {
    "DC fundamentals": [
        {"q":"A 15 V source is connected across a 5 kΩ resistor. What current flows?","options":["3 mA","75 mA","0.33 mA","3 A"],"answer":0,"why":"I=V/R=15/5000=0.003 A = 3 mA.","topic":"Ohm's law","marks":2},
        {"q":"A resistor carries 0.1 A with 20 V across it. Its power is…","options":["2 W","0.5 W","20 W","200 W"],"answer":0,"why":"P=VI=20×0.1=2 W.","topic":"Power","marks":2},
        {"q":"Two 1 kΩ resistors in parallel have an equivalent resistance of…","options":["2 kΩ","1 kΩ","500 Ω","250 Ω"],"answer":2,"why":"Two equal resistors in parallel give R/2 = 500 Ω.","topic":"Network analysis","marks":2},
        {"q":"At a node, 12 mA enters. Two branches carry 5 mA and 4 mA out. The third branch current out is…","options":["3 mA","7 mA","21 mA","1 mA"],"answer":0,"why":"KCL: 12=5+4+I, so I=3 mA.","topic":"KCL","marks":2},
    ],
    "Capacitors and transients": [
        {"q":"For R=4.7 kΩ and C=100 µF, the RC time constant is…","options":["0.047 s","0.47 s","4.7 s","47 s"],"answer":1,"why":"τ=RC=4700×100×10⁻⁶=0.47 s.","topic":"Time constant","marks":2},
        {"q":"At one time constant during ideal capacitor charging, the capacitor reaches about…","options":["36.8%","50%","63.2%","100%"],"answer":2,"why":"1−e⁻¹≈0.632.","topic":"RC response","marks":2},
        {"q":"The unit of capacitance is…","options":["Henry","Farad","Ohm","Weber"],"answer":1,"why":"Capacitance is measured in farads (F).","topic":"Component units","marks":2},
        {"q":"In an ideal capacitor, voltage cannot change instantaneously because…","options":["It would require infinite current","Resistance is infinite","The dielectric is a conductor","Its capacitance becomes zero"],"answer":0,"why":"i=C dv/dt; an instantaneous voltage step implies an unbounded dv/dt and idealised infinite current.","topic":"Physical interpretation","marks":2},
    ],
    "Diodes and power supplies": [
        {"q":"A silicon diode in forward conduction is commonly approximated in a first-pass model by…","options":["0 V","0.7 V","5 V","12 V"],"answer":1,"why":"About 0.7 V is a rough silicon-junction estimate, not a universal fixed drop; check the datasheet and current/temperature.","topic":"Diode models","marks":2},
        {"q":"A full-wave rectifier supplied at 50 Hz has an ideal ripple frequency of…","options":["25 Hz","50 Hz","100 Hz","200 Hz"],"answer":2,"why":"Full-wave rectification produces two ripple pulses per input cycle: 2×50=100 Hz.","topic":"Rectification","marks":2},
        {"q":"Increasing reservoir capacitance, with load current and ripple frequency fixed, generally…","options":["Increases ripple","Reduces ripple","Eliminates all ripple","Reverses polarity"],"answer":1,"why":"The first-order estimate ΔV≈I/(fC) decreases as C increases.","topic":"Filtering","marks":2},
        {"q":"Before selecting a replacement regulator, the designer should first verify…","options":["Only package colour","Output/current/thermal ratings and datasheet conditions","Only its brand","Only lead length"],"answer":1,"why":"Electrical limits, dropout, thermal behaviour, pinout and operating conditions must be checked against the exact datasheet.","topic":"Component selection","marks":2},
    ],
    "Semiconductor and transistor basics": [
        {"q":"A diode is primarily used to…","options":["Store magnetic energy","Conduct preferentially in one direction","Amplify all signals","Generate clock pulses"],"answer":1,"why":"A diode's asymmetric current-voltage behaviour enables rectification and other functions.","topic":"Diodes","marks":2},
        {"q":"For a BJT operating as a saturated low-side switch, the load is commonly placed…","options":["Between supply and collector","Between base and ground","Across base-emitter only","In parallel with the supply without a switch"],"answer":0,"why":"In a common NPN low-side arrangement, the load is between positive supply and collector; verify drive and protection requirements.","topic":"BJT switching","marks":2},
        {"q":"A MOSFET gate is controlled primarily by…","options":["Gate-source voltage","Collector current","Emitter resistance only","Magnetic flux"],"answer":0,"why":"The MOSFET channel is controlled by gate-source voltage; practical drive and gate charge matter.","topic":"MOSFETs","marks":2},
        {"q":"A flyback diode across a DC relay coil is used to…","options":["Increase coil voltage","Provide a path for inductive current at switch-off","Measure coil resistance","Make the relay AC"],"answer":1,"why":"The diode clamps the inductive kick and protects the switching device, with polarity chosen for normal operation.","topic":"Inductive protection","marks":2},
    ],
}

LAB_MANUALS: dict[str, dict[str, Any]] = {
    "Resistor network verification": {
        "purpose":"Verify Ohm's law and series/parallel resistance relationships using a low-voltage DC network.",
        "outcomes":["Measure voltage and current using correct meter connections","Calculate equivalent resistance","Compare theoretical and measured values","Discuss resistor tolerance and measurement uncertainty"],
        "apparatus":["Isolated current-limited DC supply (≤12 V)","Resistors with known nominal values and power ratings","Digital multimeter","Breadboard and insulated leads"],
        "procedure":["Inspect component values and ratings; keep the supply switched off.","Construct the approved resistor network and have the instructor check it.","Set a low current limit and energise the circuit.","Measure voltage across each resistor with the voltmeter in parallel.","Measure branch current with the ammeter in series; never place an ammeter directly across a supply.","De-energise before changing the network; repeat for series and parallel arrangements.","Compare measured values with calculations and record deviations."],
        "tables":[("Component","Nominal resistance (Ω)","Measured resistance (Ω)","Tolerance (%)"),("Measurement point","Calculated voltage (V)","Measured voltage (V)","Difference (%)")],
        "analysis":["Calculate equivalent resistance for each arrangement.","Use measured V and I to calculate resistance and compare with nominal values.","Explain the effect of component tolerance, meter burden and lead/contact resistance."],
        "safety":["Use only instructor-approved isolated low-voltage supplies.","Check resistor power ratings and current limit before energising.","Never measure resistance on an energised circuit.","Power off before rewiring."]
    },
    "RC charging and discharging": {
        "purpose":"Observe capacitor voltage during charging/discharging and compare the response with the first-order RC model.",
        "outcomes":["Calculate τ=RC","Identify the 63.2% charging point","Plot voltage against time","Explain departures from an ideal exponential response"],
        "apparatus":["Isolated current-limited low-voltage DC source","Resistor and electrolytic/non-polar capacitor appropriate to the circuit","Digital multimeter or approved oscilloscope","Breadboard and leads"],
        "procedure":["Check capacitor polarity and voltage rating where applicable.","Calculate the expected time constant before assembly.","With supply off, assemble the approved series RC circuit.","Connect the voltage instrument across the capacitor; verify probe settings and grounding with the instructor.","Apply the approved low-voltage step and record capacitor voltage at planned time intervals.","Discharge the capacitor through an approved resistor before changing connections.","Repeat for a changed R or C and compare the time constants."],
        "tables":[("Time (s)","Predicted capacitor voltage (V)","Measured capacitor voltage (V)","Notes")],
        "analysis":["Calculate the theoretical time constant.","Estimate the time at which the capacitor reaches 63.2% of its final voltage.","Compare the measured waveform with vC(t)=Vs(1−e^(−t/RC)).","Discuss capacitor tolerance, ESR, leakage, source resistance and instrument loading."],
        "safety":["Observe capacitor polarity and maximum voltage rating.","Discharge capacitors through a suitable resistor; do not short terminals with a tool.","Use only supervised, isolated, current-limited low-voltage sources."]
    },
    "Diode rectifier investigation": {
        "purpose":"Investigate diode forward/reverse behaviour and compare half-wave and full-wave rectification at safe low voltage.",
        "outcomes":["Identify diode polarity and interpret a datasheet","Explain half-wave/full-wave rectification","Measure rectified output and ripple","Relate ripple to load and reservoir capacitance"],
        "apparatus":["Isolated low-voltage AC source approved by instructor","Rectifier diodes or pre-approved bridge module","Rated load resistor","Rated reservoir capacitor where authorised","Oscilloscope/DMM and insulated leads"],
        "procedure":["Identify diode markings, pinout, current and reverse-voltage ratings from the exact datasheet.","With the source disconnected, assemble the instructor-approved half-wave rectifier.","Ask the instructor to verify wiring, polarity, source isolation and instrument connections.","Apply the specified low-voltage AC and observe the output waveform.","De-energise and discharge the capacitor safely before changing components.","Repeat with the approved full-wave arrangement and compare ripple frequency.","Record results and compare with first-order estimates."],
        "tables":[("Configuration","Input frequency (Hz)","Ripple frequency (Hz)","Measured average output (V)","Ripple (Vpp)")],
        "analysis":["Explain why full-wave rectification doubles ripple frequency.","Compare observed ripple with ΔV≈I/(fC), stating the approximation limits.","Discuss diode drop, load current, capacitor ESR/ripple-current rating and transformer regulation."],
        "safety":["Only isolated low-voltage AC approved by the instructor; never use mains.","Check diode and capacitor ratings and polarity before energising.","Discharge capacitors through a resistor and verify safe voltage before handling."]
    },
    "Transistor switching investigation": {
        "purpose":"Investigate a low-voltage transistor switch and the role of base/gate drive and inductive-load protection.",
        "outcomes":["Distinguish control and load paths","Calculate a first-pass drive requirement using the device datasheet","Measure switching states","Explain inductive kick and protection"],
        "apparatus":["Instructor-approved isolated current-limited low-voltage DC supply","Low-voltage transistor/MOSFET module with datasheet","Resistive test load or approved low-voltage relay module","Control resistor and protection diode where specified","Digital multimeter"],
        "procedure":["Identify exact device pinout, maximum ratings and required drive conditions from its datasheet.","Calculate a conservative first-pass load and drive arrangement; submit it for instructor approval.","With supply off, assemble the approved low-voltage switching circuit.","Check common reference, polarity, resistor values and protective components.","Energise with a low current limit and test OFF and ON states.","Measure control voltage, load voltage and current without exceeding ratings.","Power down before changing the load or wiring; record results."],
        "tables":[("Switch state","Control voltage (V)","Load voltage (V)","Load current (mA)","Observations")],
        "analysis":["Explain how the control input changes the conducting state.","Compare measured voltage/current with first-pass estimates.","Explain why a relay coil needs a suitable flyback path and how diode polarity is selected."],
        "safety":["Do not build or test mains switching circuits.","Use only approved low-voltage modules and instructor-verified pinouts.","Check device safe operating limits and heatsinking; power down before rewiring."]
    },
}


def grade_assessment(topic: str, answers: dict[str, str]) -> dict[str, Any]:
    if topic not in ASSESSMENTS:
        raise ValueError("Unknown assessment topic.")
    questions=ASSESSMENTS[topic]
    earned=0
    details=[]
    for index,q in enumerate(questions):
        selected=answers.get(str(index))
        correct=selected==q["options"][q["answer"]]
        score=q["marks"] if correct else 0
        earned+=score
        details.append({"question":q["q"],"selected":selected or "Not answered",
                        "correct_answer":q["options"][q["answer"]],"correct":correct,
                        "explanation":q["why"],"topic":q["topic"],"marks":score,
                        "max_marks":q["marks"]})
    maximum=sum(q["marks"] for q in questions)
    return {"topic":topic,"earned":earned,"maximum":maximum,
            "percentage":100*earned/maximum if maximum else 0,"details":details}


def build_assessment_report(result: dict[str, Any]) -> str:
    lines=[f"# CircuitLab Academy — {result['topic']} assessment","",
           f"**Score:** {result['earned']}/{result['maximum']} ({result['percentage']:.1f}%)","","## Review"]
    for i,item in enumerate(result["details"],1):
        lines.extend([f"### Question {i}",item["question"],f"- Your answer: {item['selected']}",
                      f"- Correct answer: {item['correct_answer']}",
                      f"- Result: {'Correct' if item['correct'] else 'Review'}",
                      f"- Explanation: {item['explanation']}",""])
    lines.extend(["## Learning note","This formative result is a study aid, not an accredited examination grade."])
    return "\n".join(lines)


def build_lab_manual(title: str, manual: dict[str, Any], student: str = "", date: str = "") -> str:
    lines=[f"# Practical laboratory: {title}","",f"**Student:** {student or '________________'}  ",
           f"**Date:** {date or '________________'}","","## Purpose",manual["purpose"],"",
           "## Learning outcomes"]+[f"- {x}" for x in manual["outcomes"]]
    lines += ["","## Apparatus"]+[f"- {x}" for x in manual["apparatus"]]
    lines += ["","## Procedure"]+[f"{i}. {x}" for i,x in enumerate(manual["procedure"],1)]
    lines += ["","## Results tables"]
    for header in manual["tables"]:
        lines += ["| "+" | ".join(header)+"|","| "+" | ".join(["---"]*len(header))+"|","| "+" | ".join([""]*len(header))+"|"]
    lines += ["","## Analysis and discussion"]+[f"- {x}" for x in manual["analysis"]]
    lines += ["","## Safety"]+[f"- {x}" for x in manual["safety"]]
    lines += ["","## Conclusion","Summarise the results, compare them with theory, and state limitations."]
    return "\n".join(lines)


def render_assessment_and_labs() -> None:
    import streamlit as st
    import pandas as pd

    st.markdown("""
    <div style="padding:22px 26px;border-radius:18px;background:linear-gradient(115deg,#101d32,#155c68);color:#f4fbff;margin-bottom:16px">
      <div style="letter-spacing:.14em;font-size:.72rem;color:#72e2d4;font-weight:700">RELEASE 4.2 · ASSESSMENT & PRACTICALS</div>
      <h2 style="color:#f4fbff;margin:.35rem 0">Test your understanding. Document your engineering.</h2>
      <p style="color:#d4e7ed;margin:0">Formative topic assessments, feedback, practical manuals and a session learning record.</p>
    </div>
    """,unsafe_allow_html=True)
    exam_tab,lab_tab,progress_tab=st.tabs(["Assessment centre","Practical laboratory","My learning record"])
    with exam_tab:
        topic=st.selectbox("Assessment topic",list(ASSESSMENTS),key="r42_exam_topic")
        questions=ASSESSMENTS[topic]
        st.caption(f"{len(questions)} questions · {sum(q['marks'] for q in questions)} marks · formative practice")
        answers={}
        with st.form(f"r42_form_{topic}"):
            for i,q in enumerate(questions):
                answers[str(i)]=st.radio(f"{i+1}. {q['q']} ({q['marks']} marks)",q["options"],index=None,key=f"r42_answer_{topic}_{i}")
            submitted=st.form_submit_button("Submit assessment",type="primary")
        if submitted:
            result=grade_assessment(topic,{k:v for k,v in answers.items() if v is not None})
            st.session_state.setdefault("r42_attempts",[]).append(result)
            st.session_state["r42_latest_result"]=result
        result=st.session_state.get("r42_latest_result")
        if result and result["topic"]==topic:
            a,b=st.columns(2)
            a.metric("Your score",f"{result['earned']} / {result['maximum']}")
            b.metric("Percentage",f"{result['percentage']:.1f}%")
            st.progress(result["percentage"]/100)
            st.dataframe(pd.DataFrame([{"Question":d["question"],"Your answer":d["selected"],"Correct answer":d["correct_answer"],"Result":"Correct" if d["correct"] else "Review","Marks":f"{d['marks']}/{d['max_marks']}"} for d in result["details"]]),use_container_width=True,hide_index=True)
            with st.expander("Read explanations",expanded=True):
                for i,d in enumerate(result["details"],1):
                    st.markdown(f"**{i}. {d['topic']}** — {d['explanation']}")
            st.download_button("Download assessment review",build_assessment_report(result),file_name="circuitlab_assessment_review.md",mime="text/markdown")
    with lab_tab:
        lab=st.selectbox("Choose a practical",list(LAB_MANUALS),key="r42_lab")
        manual=LAB_MANUALS[lab]
        st.write(manual["purpose"])
        for label,items in [("Learning outcomes",manual["outcomes"]),("Apparatus",manual["apparatus"]),("Procedure",manual["procedure"]),("Analysis",manual["analysis"]),("Safety",manual["safety"])]:
            with st.expander(label,expanded=label in ("Learning outcomes","Safety")):
                for item in items: st.markdown(f"- {item}")
        student=st.text_input("Student name / identifier (optional)",key="r42_lab_student")
        date=st.date_input("Practical date",key="r42_lab_date")
        pack=build_lab_manual(lab,manual,student,str(date))
        st.download_button("Download practical manual and results sheets",pack,file_name="circuitlab_practical_manual.md",mime="text/markdown")
    with progress_tab:
        attempts=st.session_state.get("r42_attempts",[])
        if not attempts:
            st.info("Complete a topic assessment to start your session learning record.")
        else:
            rows=[{"Attempt":i+1,"Topic":r["topic"],"Score":f"{r['earned']}/{r['maximum']}","Percentage":round(r["percentage"],1)} for i,r in enumerate(attempts)]
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
            latest={}
            for r in attempts: latest[r["topic"]]=r["percentage"]
            st.subheader("Latest result by topic")
            st.bar_chart(pd.DataFrame({"Latest percentage":latest}))
            st.caption("This record is held only in the current Streamlit session. It is not a persistent student account or institution-gradebook record.")
            st.download_button("Download learning record CSV",pd.DataFrame(rows).to_csv(index=False),file_name="circuitlab_learning_record.csv",mime="text/csv")
    st.warning("Assessments are formative practice, not accredited examinations. Practical manuals are educational templates; instructors must approve apparatus, circuit values, procedures and local safety rules before use.")
