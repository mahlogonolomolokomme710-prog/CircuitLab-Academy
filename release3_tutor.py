"""Release 3.9 — Project Tutor and Design Reviewer.

Provides an offline, evidence-based project review and Socratic tutoring workflow.
An optional OpenAI-compatible chat endpoint can be enabled with Streamlit secrets.
The reviewer checks evidence completeness; it does not certify engineering correctness.
"""
from __future__ import annotations

import json
import os
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from release3_project_factory import PROJECTS


TUTOR_PROMPTS = {
    "regulated_supply": [
        ("Rectification", "Why does a bridge rectifier use four diodes, and how many normally conduct in each half-cycle?"),
        ("Filtering", "Between rectified peaks, what supplies the load current, and how does that create ripple?"),
        ("Regulation", "At the lowest expected input voltage, how will you prove the regulator still has sufficient headroom?"),
        ("Thermal design", "Which voltage drop and load current determine the regulator's approximate dissipation?"),
        ("Verification", "Which measurements would distinguish insufficient headroom from excessive ripple?")
    ],
    "ldr_light": [
        ("Sensor behaviour", "What resistance change do you expect from the LDR between bright and dark conditions?"),
        ("Divider", "Which divider node is your output, and why does its voltage move in the direction you predict?"),
        ("Threshold", "How will you choose a switching threshold between the measured bright and dark voltages?"),
        ("Switching stage", "Why might a comparator or transistor be needed instead of driving the load directly from the divider?"),
        ("Flicker", "What could cause repeated switching near the threshold, and how could hysteresis help?")
    ],
    "rc_delay": [
        ("Time constant", "Derive the relationship between resistance, capacitance and the RC time constant, including units."),
        ("Charging", "What fraction of the final voltage is reached after one time constant during ideal charging?"),
        ("Threshold", "How does your chosen switching threshold change the delay relative to the time constant?"),
        ("Tolerance", "How would resistor and capacitor tolerances affect the actual delay?"),
        ("Measurement", "How would you record and compare the predicted and observed capacitor-voltage curve?")
    ],
    "led_driver": [
        ("LED behaviour", "Why must an LED normally have a current-limiting element in a voltage-driven circuit?"),
        ("Resistor", "Show how you derive the minimum series resistance from supply voltage, LED forward voltage and target current."),
        ("Standard value", "Why should the selected standard resistor generally be rounded up from the calculated minimum?"),
        ("Power", "How will you calculate resistor dissipation and choose a suitable power rating?"),
        ("Tolerance", "Which worst-case supply and LED forward-voltage conditions could increase LED current?")
    ],
    "motor_pwm": [
        ("PWM principle", "How does changing duty cycle change the ideal average voltage applied by a PWM stage?"),
        ("Motor data", "Why is motor stall current important when selecting the switching device and supply?"),
        ("Switch", "Which MOSFET parameters matter beyond its headline current rating?"),
        ("Inductive energy", "What happens to motor current when the switch turns off, and how is the current path managed?"),
        ("Testing", "How will you test start-up, load changes and temperature without exceeding the motor or driver ratings?")
    ],
    "astable_555": [
        ("Operation", "Describe how the timing capacitor charges and discharges in a standard 555 astable circuit."),
        ("Frequency", "Which timing components determine the oscillation period, and how do they affect frequency?"),
        ("Duty cycle", "Why is the standard two-resistor astable topology's duty cycle normally above 50%?"),
        ("Tolerance", "How do timing resistor and capacitor tolerances affect the expected frequency?"),
        ("Validation", "How will you measure frequency and duty cycle and calculate percentage error?")
    ],
}


def review_project_evidence(project_id: str, requirements: str = "", calculations: str = "",
                            component_selection: str = "", schematic_simulation: str = "",
                            testing: str = "", discussion: str = "", safety: str = "") -> dict[str, Any]:
    """Score completeness of submitted evidence, not technical correctness."""
    if project_id not in PROJECTS:
        raise ValueError(f"Unknown project: {project_id}")
    fields = [
        ("Requirements and specifications", requirements, 15),
        ("Theory and calculations", calculations, 20),
        ("Component selection and datasheets", component_selection, 15),
        ("Schematic and simulation evidence", schematic_simulation, 15),
        ("Testing and interpretation", testing, 20),
        ("Discussion and engineering justification", discussion, 10),
        ("Safety and limitations", safety, 5),
    ]
    results, total, missing = [], 0, []
    for label, raw, weight in fields:
        value = str(raw or "").strip()
        if not value:
            score, status, feedback = 0, "Missing", "Add this evidence before submission."
            missing.append(label)
        elif len(value) < 45:
            score, status, feedback = round(weight * 0.4), "Develop", "Evidence is present but brief; add values, units, reasoning or supporting observations."
        else:
            score, status, feedback = weight, "Present", "Evidence is present. Check accuracy, traceability and alignment with the project brief."
        total += score
        results.append({"criterion": label, "weight": weight, "score": score, "status": status, "feedback": feedback})
    project = PROJECTS[project_id]
    text_blob = " ".join(str(x or "") for x in [requirements, calculations, component_selection, schematic_simulation, testing, discussion, safety]).lower()
    keywords = {
        "regulated_supply": ["ripple", "headroom", "rectif", "regulat", "thermal"],
        "ldr_light": ["ldr", "bright", "dark", "threshold", "divider"],
        "rc_delay": ["time constant", "tau", "capac", "resistan", "threshold"],
        "led_driver": ["forward voltage", "resistor", "current", "power", "datasheet"],
        "motor_pwm": ["duty", "stall current", "mosfet", "flyback", "motor"],
        "astable_555": ["555", "frequency", "duty", "capac", "timing"],
    }[project_id]
    domain_checks = [{"item": term, "present": term in text_blob} for term in keywords]
    return {
        "project": project["name"], "score": total, "maximum": sum(x[2] for x in fields),
        "percentage": round(100 * total / sum(x[2] for x in fields)),
        "criteria": results, "missing": missing, "domain_checks": domain_checks,
        "domain_gaps": [x for x in keywords if x not in text_blob],
        "disclaimer": "This is an evidence-completeness screen. It does not verify equations, component ratings, schematic connectivity, simulation validity, standards compliance or physical safety.",
    }


def build_tutor_context(project_id: str, student_level: str, student_question: str, project_work: str) -> str:
    if project_id not in PROJECTS:
        raise ValueError(f"Unknown project: {project_id}")
    project = PROJECTS[project_id]
    return (
        f"Project: {project['name']}\nLevel: {student_level}\nGoal: {project['goal']}\n"
        f"Requirements: {'; '.join(project['requirements'])}\n"
        f"Learning outcomes: {'; '.join(project['outcomes'])}\n"
        f"Student work: {project_work[:9000]}\nQuestion: {student_question[:3000]}"
    )


def ask_optional_ai(context: str, api_key: str | None = None, model: str | None = None,
                    base_url: str | None = None) -> str:
    """Call an OpenAI-compatible chat-completions endpoint only when configured."""
    key = (api_key or os.getenv("OPENAI_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("No API key is configured. Use the offline tutor and reviewer, or add OPENAI_API_KEY to Streamlit Secrets.")
    model_name = (model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip()
    endpoint = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    payload = {
        "model": model_name, "temperature": 0.25,
        "messages": [
            {"role": "system", "content": (
                "You are CircuitLab Academy's electronics project tutor. Teach with clear stepwise reasoning and "
                "Socratic questions. Use the supplied project context. Separate established equations, assumptions, "
                "estimates and unverified claims. Never invent datasheet ratings or claim a design is safe. "
                "Flag missing information and ask the student to verify exact manufacturer datasheets. "
                "Never give instructions for connecting student circuits directly to mains. Restrict physical "
                "experiments to supervised, isolated, current-limited low-voltage equipment."
            )},
            {"role": "user", "content": context},
        ],
    }
    request = Request(endpoint + "/chat/completions", data=json.dumps(payload).encode("utf-8"),
                      headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                      method="POST")
    try:
        with urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
        answer = data["choices"][0]["message"]["content"]
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("The AI service returned an empty response.")
        return answer.strip()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:600]
        raise RuntimeError(f"AI service returned HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not complete the AI tutor request: {exc}") from exc


def render_project_tutor() -> None:
    import streamlit as st
    import pandas as pd

    st.markdown("""
    <div style="padding:20px 24px;border-radius:16px;background:linear-gradient(115deg,#101d32,#145b69);color:#f3fbff;margin-bottom:14px">
      <div style="letter-spacing:.14em;font-size:.72rem;color:#69dfd0;font-weight:700">RELEASE 3.9 · PROJECT INTELLIGENCE</div>
      <h2 style="color:#f3fbff;margin:.35rem 0">AI Project Tutor & Design Reviewer</h2>
      <p style="color:#d3e5ee;margin:0">Learn to defend your engineering decisions, review your evidence and improve your project systematically.</p>
    </div>
    """, unsafe_allow_html=True)
    project_id = st.selectbox("Choose the project you are working on", list(PROJECTS),
                              format_func=lambda k: PROJECTS[k]["name"], key="r39_project")
    project = PROJECTS[project_id]
    level = st.selectbox("Student level", ["First year", "Second year", "Third year", "Final year"], key="r39_level")
    st.caption(project["goal"])
    with st.expander("Project outcomes and requirements", expanded=False):
        st.markdown("**Learning outcomes**")
        for item in project["outcomes"]:
            st.write("• " + item)
        st.markdown("**Requirements to address**")
        for item in project["requirements"]:
            st.write("• " + item)

    st.subheader("1 · Offline design review")
    st.caption("Paste your own work into the sections below. The reviewer checks evidence coverage and terminology; it does not mark technical correctness.")
    with st.form("r39_review_form"):
        requirements = st.text_area("Requirements and specifications", placeholder="Target values, operating range, load, constraints and assumptions…")
        calculations = st.text_area("Theory and calculations", placeholder="Equations, substitutions, units, assumptions and calculated results…")
        components = st.text_area("Component selection and datasheets", placeholder="Part numbers, ratings, datasheet links and selection justification…")
        schematic = st.text_area("Schematic and simulation evidence", placeholder="Describe the topology, node labels, simulator setup and observations…")
        testing = st.text_area("Testing and interpretation", placeholder="Test procedure, expected values, actual values, units and comparison…")
        discussion = st.text_area("Discussion and engineering justification", placeholder="Explain why you chose this design and interpret discrepancies…")
        safety = st.text_area("Safety and limitations", placeholder="Supply isolation, current limit, component ratings, limitations and supervision…")
        run_review = st.form_submit_button("Review my project evidence", type="primary")
    if run_review:
        report = review_project_evidence(project_id, requirements, calculations, components, schematic, testing, discussion, safety)
        st.session_state["r39_review"] = report
        st.session_state["r39_review_project"] = project_id
    report = st.session_state.get("r39_review")
    if report and st.session_state.get("r39_review_project") == project_id:
        st.metric("Evidence completeness (not a technical grade)", f"{report['percentage']}%", f"{report['score']} / {report['maximum']} points")
        st.dataframe(pd.DataFrame(report["criteria"]), use_container_width=True, hide_index=True)
        if report["missing"]:
            st.warning("Missing sections: " + ", ".join(report["missing"]))
        if report["domain_gaps"]:
            st.info("Project-specific topics not yet mentioned: " + ", ".join(report["domain_gaps"]))
        st.caption(report["disclaimer"])
        review_md = ["# CircuitLab Academy — Project evidence review", "", f"**Project:** {report['project']}", f"**Evidence completeness:** {report['percentage']}%", "", "| Criterion | Score | Status | Feedback |", "|---|---:|---|---|"]
        review_md.extend(f"| {r['criterion']} | {r['score']}/{r['weight']} | {r['status']} | {r['feedback']} |" for r in report["criteria"])
        review_md.extend(["", "## Project-specific topic coverage", ""] + [f"- {'Present' if x['present'] else 'Not mentioned'}: {x['item']}" for x in report["domain_checks"]])
        review_md.extend(["", "## Limitation", report["disclaimer"]])
        st.download_button("Download review report", "\n".join(review_md), file_name="circuitlab_project_review.md", mime="text/markdown")

    st.divider()
    st.subheader("2 · Socratic project tutor")
    prompts = TUTOR_PROMPTS[project_id]
    topic = st.selectbox("Choose a concept to defend", [x[0] for x in prompts], key="r39_topic")
    question = next(x[1] for x in prompts if x[0] == topic)
    st.info(question)
    student_answer = st.text_area("Your answer / question for the tutor", key="r39_answer", placeholder="Explain your reasoning. Include equations and units where relevant.")
    if st.button("Get guided feedback", key="r39_offline_feedback"):
        if len(student_answer.strip()) < 12:
            st.warning("Write a little more so the tutor can respond meaningfully.")
        else:
            answer = (
                f"**Your task:** {question}\n\n"
                "**Check your response:** Have you stated the governing principle, written the relevant equation, "
                "defined each variable with units, explained your design choice and identified an assumption?\n\n"
                "**Next step:** Compare your explanation with the project requirements and the relevant component datasheet. "
                "If you are uncertain, identify exactly which value or principle you need to verify."
            )
            st.session_state["r39_offline_feedback"] = answer
    if st.session_state.get("r39_offline_feedback"):
        st.markdown(st.session_state["r39_offline_feedback"])
    st.caption("The offline tutor gives a structured self-check rather than pretending to understand or grade the technical correctness of your free-text answer.")

    st.divider()
    st.subheader("3 · Optional live AI tutor")
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY", "")
        secret_model = st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")
        secret_base = st.secrets.get("OPENAI_BASE_URL", "")
    except Exception:
        secret_key, secret_model, secret_base = "", "gpt-4o-mini", ""
    if not secret_key:
        st.info("Live AI is optional and currently not configured. The offline reviewer and Socratic tutor work without API billing.")
    api_question = st.text_area("Ask a project-specific question", key="r39_ai_question", placeholder="For example: Explain how I should verify regulator headroom at low line.")
    work_context = st.text_area("Relevant design details (optional)", key="r39_ai_context", placeholder="Paste your calculation, component values or observation…")
    if st.button("Ask live AI tutor", key="r39_ai_submit"):
        if not secret_key:
            st.warning("Add OPENAI_API_KEY to Streamlit Secrets before using live AI. No API request was made.")
        elif not api_question.strip():
            st.warning("Enter a question first.")
        else:
            context = build_tutor_context(project_id, level, api_question, work_context)
            try:
                with st.spinner("Reviewing your project question…"):
                    response = ask_optional_ai(context, secret_key, secret_model, secret_base or None)
                st.session_state["r39_ai_response"] = response
                st.session_state["r39_ai_response_project"] = project_id
            except Exception as exc:
                st.error(str(exc))
    if st.session_state.get("r39_ai_response") and st.session_state.get("r39_ai_response_project") == project_id:
        st.markdown(st.session_state["r39_ai_response"])
