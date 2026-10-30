"""Release 4.4 — Engineering Design Challenge Centre.

Structured, evidence-led design challenges. Completion scoring measures submitted
evidence only; it is not a technical grade or safety approval.
"""
from __future__ import annotations

from typing import Any
import streamlit as st

CHALLENGES: dict[str, dict[str, Any]] = {
    "regulated_supply": {
        "title": "Design a regulated 5 V DC supply",
        "level": "Intermediate",
        "scenario": "A small laboratory instrument needs a stable 5 V DC supply from an approved isolated low-voltage source.",
        "brief": "Develop and justify a rectifier, reservoir-filter and regulator architecture for a defined load.",
        "requirements": [
            "Specify 5.0 V nominal output and a clearly stated maximum load current.",
            "Set a quantitative ripple target and identify where it will be measured.",
            "Show rectification, reservoir filtering, regulation and output decoupling in the block diagram.",
            "Calculate load power, reservoir capacitance and regulator dissipation using stated assumptions.",
            "Select candidate diodes, capacitor and regulator using manufacturer datasheets.",
            "Define tests for no-load, full-load, ripple and regulator temperature."
        ],
        "constraints": [
            "Use only an approved isolated low-voltage source for any supervised practical work.",
            "No mains-side design, wiring or construction instructions.",
            "State the regulator dropout/headroom and low-line assumptions.",
            "Do not describe a first-pass estimate as a validated power-supply design."
        ],
        "deliverables": ["Requirements/specification sheet", "Block diagram and annotated schematic", "Calculation sheet with units and assumptions", "Datasheet-backed component selection", "Simulation evidence and model details", "Verification plan, results and discussion", "Safety review and final engineering report"],
        "milestones": ["Define output and load requirements", "Choose rectifier/filter/regulator architecture", "Complete first-pass electrical and thermal calculations", "Select candidate components from datasheets", "Simulate and review operating margins", "Prepare a supervised low-voltage verification plan"],
        "rubric": {"Requirements and measurable specifications": 15, "Theory and calculations": 20, "Component selection and datasheets": 15, "Schematic and simulation evidence": 15, "Verification, interpretation and discussion": 20, "Report quality and safety": 15}
    },
    "automatic_light": {
        "title": "Design an automatic streetlight controller",
        "level": "Beginner–Intermediate",
        "scenario": "A low-voltage demonstration streetlight should switch on as ambient light falls and switch off in bright conditions.",
        "brief": "Design an LDR sensing stage and a suitable low-voltage switching stage with a defined threshold.",
        "requirements": [
            "Define bright and dark test conditions, including how illumination will be recorded.",
            "Use measured or datasheet-supported LDR resistance values for both conditions.",
            "Calculate divider output in bright and dark conditions and identify the switching threshold.",
            "Explain and justify the transistor or comparator switching stage.",
            "Calculate LED/load current and verify the current-limiting or driver arrangement.",
            "Investigate threshold instability and propose hysteresis or another remedy."
        ],
        "constraints": [
            "Demonstrator load must be low-voltage only.",
            "Do not connect to building lighting circuits or mains.",
            "State the LDR divider orientation and assumptions.",
            "Check transistor/comparator and LED ratings against exact datasheets."
        ],
        "deliverables": ["Functional requirements", "Bright/dark sensor data", "Divider calculations", "Annotated schematic", "Switching-stage justification", "Simulation and threshold evidence", "Test table and report"],
        "milestones": ["Characterise bright and dark sensor conditions", "Calculate divider outputs", "Choose a switching threshold", "Design the switching and load stage", "Simulate threshold behaviour", "Document repeatability and limitations"],
        "rubric": {"Requirements and sensor characterisation": 15, "Divider theory and calculations": 20, "Switching-stage design": 20, "Schematic and simulation": 15, "Testing and interpretation": 20, "Report and safety": 10}
    },
    "motor_controller": {
        "title": "Design a low-voltage PWM motor controller",
        "level": "Intermediate–Advanced",
        "scenario": "A small DC motor needs adjustable speed using pulse-width modulation and an appropriately rated switching stage.",
        "brief": "Develop a conceptual PWM control architecture and justify the driver, suppression path and supply requirements.",
        "requirements": [
            "Record motor rated voltage, running current and stall current from a reliable source.",
            "Specify PWM frequency and minimum/maximum duty-cycle requirements.",
            "Calculate ideal average motor-terminal voltage at at least three duty cycles.",
            "Select a driver using voltage, stall current, thermal and safe-operating-area information.",
            "Explain the inductive-energy/current recirculation path and supply decoupling.",
            "Define tests for start-up, load variation, current and driver temperature."
        ],
        "constraints": [
            "Use a low-voltage motor and current-limited supply only.",
            "Do not infer driver suitability from nominal running current alone.",
            "Include motor stall current and transient stress in the review.",
            "A simple average-voltage calculation is not a motor dynamics simulation."
        ],
        "deliverables": ["Motor and load specification", "PWM requirements and calculations", "Driver datasheet comparison", "Annotated power-stage schematic", "Simulation evidence", "Protection and thermal review", "Verification plan and report"],
        "milestones": ["Characterise motor requirements", "Define PWM operating range", "Calculate average-value estimates", "Select and review switching device", "Review suppression and decoupling", "Prepare test and fault-response plan"],
        "rubric": {"Requirements and motor data": 15, "PWM theory and calculations": 20, "Driver/protection selection": 20, "Schematic and simulation": 15, "Testing and interpretation": 20, "Report and safety": 10}
    },
    "rc_timer": {
        "title": "Design an RC delay circuit",
        "level": "Beginner",
        "scenario": "A low-voltage indicator should activate after a defined delay following power-up.",
        "brief": "Select an RC network and threshold stage, then justify the delay using the exponential charging response.",
        "requirements": [
            "Define the required delay and the voltage threshold that represents activation.",
            "Derive the RC charging equation and time-constant relationship.",
            "Select practical resistor and capacitor values and calculate the resulting delay.",
            "Plot or tabulate capacitor voltage against time.",
            "Discuss capacitor tolerance, leakage and input loading.",
            "Define a repeatable timing test and compare measured/simulated results with theory."
        ],
        "constraints": [
            "Use low-voltage DC only.",
            "State the assumed initial capacitor voltage and threshold fraction.",
            "Check capacitor polarity and voltage rating where applicable.",
            "Do not assume the 63.2% time constant equals every possible switching delay."
        ],
        "deliverables": ["Delay specification", "Equation derivation", "Component selection", "Waveform and threshold calculation", "Annotated schematic", "Comparison/test table", "Engineering report"],
        "milestones": ["Set target delay and threshold", "Derive required time constant", "Choose standard R and C values", "Generate expected waveform", "Review loading and tolerances", "Prepare timing verification"],
        "rubric": {"Requirements and threshold definition": 15, "Theory and derivation": 20, "Component selection and calculations": 20, "Schematic and waveform evidence": 15, "Testing and interpretation": 20, "Report and safety": 10}
    },
    "555_oscillator": {
        "title": "Design a 555 astable oscillator",
        "level": "Intermediate",
        "scenario": "A low-voltage timer circuit must generate a periodic output at a specified frequency for a demonstration load.",
        "brief": "Choose timing components, estimate frequency and duty cycle, and verify operation against the selected timer datasheet.",
        "requirements": [
            "Specify target frequency, supply voltage and output load.",
            "Derive or cite the approximate astable timing relationships used.",
            "Calculate candidate RA, RB and C values and predicted high/low times.",
            "Discuss the duty-cycle limitation of the standard two-resistor topology.",
            "Check the exact timer variant's supply, output-current and timing-component guidance.",
            "Define frequency, duty-cycle and output-level verification tests."
        ],
        "constraints": [
            "Use a low-voltage supply within the selected timer datasheet limits.",
            "Identify whether the selected device is bipolar or CMOS.",
            "Do not assume all 555 variants have identical electrical limits.",
            "Treat approximate equations as estimates and account for component tolerances."
        ],
        "deliverables": ["Oscillator specification", "Timing derivation and calculations", "Datasheet-backed component choices", "Annotated schematic", "Simulated waveform", "Measured frequency/duty-cycle comparison", "Report and safety review"],
        "milestones": ["Define frequency and duty-cycle targets", "Choose a timing capacitor", "Calculate resistor values", "Check topology and timer datasheet limits", "Simulate waveform", "Plan and document verification"],
        "rubric": {"Requirements and operating principle": 15, "Timing derivation and calculations": 25, "Component selection and datasheets": 15, "Schematic and simulation": 15, "Measurement and interpretation": 20, "Report and safety": 10}
    }
}


def rubric_total(challenge_id: str) -> int:
    if challenge_id not in CHALLENGES:
        raise ValueError("Unknown design challenge.")
    return sum(CHALLENGES[challenge_id]["rubric"].values())


def evidence_completion(challenge_id: str, completed: list[str]) -> dict[str, Any]:
    """Return a transparent evidence-completion indicator, not a technical grade."""
    if challenge_id not in CHALLENGES:
        raise ValueError("Unknown design challenge.")
    rubric = CHALLENGES[challenge_id]["rubric"]
    valid = [item for item in rubric if item in completed]
    score = sum(rubric[item] for item in valid)
    return {"completed_categories": valid, "missing_categories": [item for item in rubric if item not in valid],
            "points": score, "maximum": sum(rubric.values()),
            "percentage": score / sum(rubric.values()) * 100}


def build_submission(challenge_id: str, student: str, course: str, evidence: dict[str, str],
                     completed: list[str], reflection: str) -> str:
    if challenge_id not in CHALLENGES:
        raise ValueError("Unknown design challenge.")
    challenge = CHALLENGES[challenge_id]
    status = evidence_completion(challenge_id, completed)
    lines = ["# CircuitLab Academy — Engineering Design Challenge Submission", "",
             f"**Challenge:** {challenge['title']}", f"**Student:** {student or 'Not supplied'}",
             f"**Course / level:** {course or 'Not supplied'}", "",
             "## Scenario and design brief", challenge["scenario"], "", challenge["brief"], ""]
    lines[-1] = challenge["brief"]
    lines.extend(["## Design requirements"] + [f"- [ ] {x}" for x in challenge["requirements"]])
    lines.extend(["", "## Design constraints"] + [f"- {x}" for x in challenge["constraints"]])
    lines.extend(["", "## Milestones"] + [f"- {x}" for x in challenge["milestones"]])
    lines.extend(["", "## Student evidence"])
    for category in challenge["rubric"]:
        lines.extend([f"### {category}", evidence.get(category, "").strip() or "_Evidence not supplied._"])
    lines.extend(["", "## Evidence completeness review",
                  f"- Evidence categories marked complete: {status['points']} / {status['maximum']} points ({status['percentage']:.1f}%).",
                  "- This is a self-reported evidence-completeness indicator, not a technical grade, independent verification or safety approval.",
                  "", "## Student reflection", reflection.strip() or "_Not supplied._",
                  "", "## Assessment rubric"])
    lines.extend([f"- {name}: {points} points" for name, points in challenge["rubric"].items()])
    lines.extend(["", "## Safety and academic integrity",
                  "Use only instructor-approved, supervised, isolated and current-limited low-voltage equipment. Never connect student-built circuits directly to mains. Verify equations, exact component datasheets and simulation assumptions. Cite sources and distinguish calculations, simulation results and physical measurements.",
                  "", "This submission template does not certify a design as safe or construction-ready.", ""])
    return "\n".join(lines)


def render_design_challenge_centre() -> None:
    st.markdown("""
    <div style="padding:22px 26px;border-radius:16px;background:linear-gradient(110deg,#102238,#15515b);color:#f4fbff;margin-bottom:14px">
      <div style="letter-spacing:.15em;font-size:.72rem;color:#72e1d1;font-weight:700">CIRCUITLAB ACADEMY · RELEASE 4.4</div>
      <h2 style="color:#f4fbff;margin:.35rem 0">Engineering Design Challenge Centre</h2>
      <p style="color:#d0e3eb;margin:0">Turn engineering theory into a documented design, evidence package and defensible engineering decision.</p>
    </div>
    """, unsafe_allow_html=True)
    challenge_id = st.selectbox("Choose a design challenge", list(CHALLENGES),
                                format_func=lambda key: CHALLENGES[key]["title"], key="r44_challenge")
    challenge = CHALLENGES[challenge_id]
    st.caption(f"{challenge['level']} · Design brief")
    st.subheader(challenge["scenario"])
    st.write(challenge["brief"])
    overview, work, submit = st.tabs(["Challenge brief", "Design workspace", "Submission pack"])
    with overview:
        st.markdown("#### Requirements")
        for item in challenge["requirements"]:
            st.markdown(f"- {item}")
        st.markdown("#### Design constraints")
        for item in challenge["constraints"]:
            st.markdown(f"- {item}")
        st.markdown("#### Project milestones")
        for index, item in enumerate(challenge["milestones"], 1):
            st.markdown(f"{index}. {item}")
        st.markdown("#### Required deliverables")
        for item in challenge["deliverables"]:
            st.markdown(f"- {item}")
        st.markdown("#### Assessment rubric")
        st.dataframe([{"Criterion": key, "Weight": value} for key, value in challenge["rubric"].items()],
                     use_container_width=True, hide_index=True)
        st.metric("Total rubric weighting", f"{rubric_total(challenge_id)} / 100")
        st.download_button("Download challenge brief", build_submission(challenge_id, "", "", {}, [], ""),
                           file_name=f"circuitlab_{challenge_id}_challenge.md", mime="text/markdown")
    with work:
        st.info("Use this workspace to assemble evidence. Mark a category complete only when you have added and checked the corresponding evidence.")
        student = st.text_input("Student name", key=f"r44_student_{challenge_id}")
        course = st.text_input("Course / module / level", key=f"r44_course_{challenge_id}")
        evidence: dict[str, str] = {}
        completed: list[str] = []
        for index, (criterion, weight) in enumerate(challenge["rubric"].items()):
            with st.expander(f"{criterion} · {weight} points", expanded=index == 0):
                evidence[criterion] = st.text_area("Evidence, calculations, references or observations",
                                                   key=f"r44_evidence_{challenge_id}_{index}", height=130)
                if st.checkbox("I have included and reviewed this evidence", key=f"r44_complete_{challenge_id}_{index}"):
                    completed.append(criterion)
        reflection = st.text_area("Engineering reflection: what changed after reviewing your evidence?",
                                   key=f"r44_reflection_{challenge_id}", height=110)
        status = evidence_completion(challenge_id, completed)
        st.progress(status["percentage"] / 100)
        st.metric("Evidence completeness (self-reported)", f"{status['points']} / {status['maximum']}")
        st.caption("This indicator measures only the rubric categories you marked complete. It does not judge technical correctness or award an academic grade.")
        submission = build_submission(challenge_id, student, course, evidence, completed, reflection)
        st.download_button("Export current design submission", submission,
                           file_name=f"circuitlab_{challenge_id}_submission.md", mime="text/markdown",
                           key=f"r44_export_{challenge_id}")
    with submit:
        st.markdown("### Before submitting")
        st.markdown("- [ ] All requirements have been addressed.")
        st.markdown("- [ ] Calculations show equations, units, assumptions and working.")
        st.markdown("- [ ] Component choices are supported by exact manufacturer datasheets.")
        st.markdown("- [ ] Schematic and simulation evidence are labelled and reproducible.")
        st.markdown("- [ ] Simulated, calculated and physically measured values are clearly distinguished.")
        st.markdown("- [ ] Limitations, unexpected results and safety considerations are discussed.")
        st.markdown("- [ ] Sources are cited and the report is proofread.")
        st.warning("The workspace is session-based. Download your submission before leaving or refreshing the app. The Centre does not store student accounts, submit work to TUT, or independently verify a design.")
