import json
import os
import urllib.error
import urllib.request

import streamlit as st

from release2_circuit_reader import parse_circuitjs
from release2_topology import analyze_topology

SYSTEM_PROMPT = """You are CircuitLab Academy's AI Engineering Copilot, an expert electronics and electrical engineering tutor.
Help students understand, design, calculate, simulate, test and troubleshoot circuits. Show equations, substitutions,
units, assumptions and reasonableness checks. Ask focused questions when requirements are missing.
Never invent simulator readings, measurements, datasheet values or project facts. Clearly distinguish calculated,
user-provided, simulated (only when the user supplied simulator evidence), and suggested information.
For component selection, explain which datasheet ratings must be checked; do not fabricate exact specifications.
For physical builds, never recommend connecting student circuits directly to mains. Prioritize isolated,
current-limited low-voltage supplies for beginner experiments and power-off checks before rewiring.
Do not claim to see a live schematic or simulator. When a CircuitJS schematic extraction and topology interpretation are supplied, use them as evidence with appropriate uncertainty. Treat recognized topologies as heuristic candidates, explain what graph pattern supports each candidate, and state what must be checked. Never infer unobserved simulator readings. Ask for circuit values, a description or observations when needed.
Do not present educational assistance as a substitute for lecturer, laboratory or professional review.
Use clear headings and complete step-by-step explanations."""

CALCULATORS = {
    "Ohm's law": "V = I × R",
    "Electrical power": "P = V × I; P = I²R; P = V²/R",
    "Voltage divider": "Vout = Vin × R2/(R1+R2), across R2; assumes an unloaded divider",
    "RC time constant": "τ = R × C; a first-order response reaches about 63.2% after one τ",
    "Full-wave ripple estimate": "C ≈ Iload/(2 × fline × Vripple_pp); first-order approximation only",
}

def _secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return os.environ.get(name, default)

def _calculators():
    st.subheader("Deterministic engineering calculators")
    choice = st.selectbox("Calculation", list(CALCULATORS), key="r2_calc")
    st.caption(CALCULATORS[choice])
    if choice == "Ohm's law":
        mode = st.radio("Known values", ["Voltage + resistance", "Current + resistance", "Voltage + current"], horizontal=True)
        a, b = st.columns(2)
        if mode == "Voltage + resistance":
            v = a.number_input("Voltage (V)", min_value=0.0, value=5.0, key="r2_ov")
            r = b.number_input("Resistance (Ω)", min_value=0.000001, value=1000.0, key="r2_or")
            st.success(f"Calculated current = {v/r:.6g} A ({v/r*1000:.5g} mA)")
            st.code(f"I = V/R = {v:g}/{r:g} = {v/r:.6g} A")
        elif mode == "Current + resistance":
            i = a.number_input("Current (A)", min_value=0.0, value=0.005, key="r2_oi")
            r = b.number_input("Resistance (Ω)", min_value=0.000001, value=1000.0, key="r2_or2")
            st.success(f"Calculated voltage = {i*r:.6g} V")
            st.code(f"V = I×R = {i:g}×{r:g} = {i*r:.6g} V")
        else:
            v = a.number_input("Voltage (V)", min_value=0.0, value=5.0, key="r2_ov2")
            i = b.number_input("Current (A)", min_value=0.000001, value=0.005, key="r2_oi2")
            st.success(f"Calculated resistance = {v/i:.6g} Ω")
            st.code(f"R = V/I = {v:g}/{i:g} = {v/i:.6g} Ω")
    elif choice == "Electrical power":
        v = st.number_input("Load voltage (V)", min_value=0.0, value=5.0, key="r2_pv")
        i = st.number_input("Load current (A)", min_value=0.0, value=0.1, key="r2_pi")
        st.success(f"Calculated power = {v*i:.6g} W")
        st.code(f"P = V×I = {v:g}×{i:g} = {v*i:.6g} W")
        st.caption("Choose a component rating with suitable derating and thermal margin; verify its datasheet.")
    elif choice == "Voltage divider":
        vin = st.number_input("Input voltage (V)", min_value=0.0, value=12.0, key="r2_dv")
        r1 = st.number_input("Upper resistor R1 (Ω)", min_value=0.000001, value=10000.0, key="r2_dr1")
        r2 = st.number_input("Lower resistor R2 (Ω)", min_value=0.000001, value=10000.0, key="r2_dr2")
        out = vin*r2/(r1+r2)
        st.success(f"Unloaded output = {out:.6g} V")
        st.code(f"Vout = Vin×R2/(R1+R2) = {vin:g}×{r2:g}/({r1:g}+{r2:g}) = {out:.6g} V")
        st.warning("A connected load changes the effective lower resistance and output voltage.")
    elif choice == "RC time constant":
        r = st.number_input("Resistance (Ω)", min_value=0.000001, value=10000.0, key="r2_rr")
        c = st.number_input("Capacitance (µF)", min_value=0.000001, value=100.0, key="r2_cc")
        tau = r*c*1e-6
        st.success(f"Time constant τ = {tau:.6g} s")
        st.code(f"τ = R×C = {r:g}×{c:g} µF = {tau:.6g} s")
        st.write(f"Approximate 63.2% point: {tau:.5g} s · 5τ estimate: {5*tau:.5g} s")
    else:
        current = st.number_input("Load current (A)", min_value=0.000001, value=0.1, key="r2_ri")
        freq = st.number_input("Mains frequency (Hz)", min_value=1.0, value=50.0, key="r2_rf")
        ripple = st.number_input("Target ripple (mV peak-to-peak)", min_value=0.1, value=100.0, key="r2_rv")
        cap = current/(2*freq*ripple/1000)
        st.success(f"First-pass capacitance estimate = {cap*1e6:.5g} µF")
        st.code(f"C ≈ I/(2fVripple) = {current:g}/(2×{freq:g}×{ripple/1000:g}) = {cap:.6g} F")
        st.warning("Assumes full-wave rectification and a simplified capacitor-discharge model. Check ESR, ripple-current rating, transformer regulation, diode drops, load variation and regulator headroom.")
    st.caption("Results are idealized calculations, not simulator output or physical measurements.")

def render():
    st.markdown("""
    <div style="padding:26px 30px;border-radius:18px;color:#F4FAFF;background:linear-gradient(115deg,#0A1929,#124A5A);margin-bottom:18px">
      <div style="font-size:.72rem;letter-spacing:.18em;color:#72D4DE;font-weight:750">CIRCUITLAB ACADEMY · RELEASE 2</div>
      <h1 style="color:#F4FAFF;margin:.45rem 0">AI Engineering Copilot</h1>
      <p style="color:#C3D5E1;margin:0;max-width:850px">A reasoning partner for circuit design, calculations, simulation interpretation and systematic fault diagnosis.</p>
    </div>
    """, unsafe_allow_html=True)
    configured_key = _secret("OPENAI_API_KEY", "")
    entered_key = st.text_input("AI API key (session only)", type="password", help="For a persistent deployment setup, add OPENAI_API_KEY to the separate Streamlit test app's Secrets. Never commit a key to GitHub.")
    api_key = entered_key.strip() or configured_key
    model = _secret("OPENAI_MODEL", "gpt-4o-mini")
    endpoint = _secret("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
    a, b = st.columns([1, 2])
    a.success("AI configured") if api_key else a.info("Local calculators ready · AI key not configured")
    b.caption(f"Model: {model} · OpenAI-compatible chat endpoint")
    chat_tab, calc_tab, guide_tab = st.tabs(["Copilot conversation", "Engineering calculators", "Setup and limitations"])
    with chat_tab:
        with st.expander("Engineering context", expanded=True):
            projects = st.session_state.get("cla_projects", [])
            labels = ["No project selected"] + [f'{p.get("name","Project")} · {p.get("id","")}' for p in projects]
            project = st.selectbox("Current project", labels, key="r2_project")
            circuit = st.text_area("Circuit description and component values", placeholder="Example: 12 V DC source, 1 kΩ resistor, red LED; target current 10 mA.", height=90, key="r2_circuit")
            schematic_file = st.file_uploader("Upload a CircuitJS/Falstad schematic (.txt)", type=["txt"], key="r2_schematic_upload", help="In CircuitJS, export or save the circuit as text, then upload that .txt file here.")
            schematic_summary = ""
            topology_summary = ""
            if schematic_file is not None:
                try:
                    schematic_text = schematic_file.getvalue().decode("utf-8-sig")
                    parsed_schematic = parse_circuitjs(schematic_text)
                    schematic_summary = parsed_schematic["summary"]
                    topology_result = analyze_topology(parsed_schematic)
                    topology_summary = topology_result["summary"]
                    st.success(f"Schematic read: {len(parsed_schematic['components'])} components, {parsed_schematic['wire_count']} wire segments, {parsed_schematic['net_count']} inferred nets.")
                    with st.expander("Review extracted schematic data"):
                        st.code(schematic_summary)
                    with st.expander("Review topology interpretation", expanded=True):
                        st.markdown(topology_summary.replace("\\n", "\n"))
                except Exception as exc:
                    st.error(f"Could not read this schematic file: {type(exc).__name__}: {exc}")
            level = st.selectbox("Student level", ["First-year / foundations", "Intermediate diploma", "Advanced engineering"], key="r2_level")
            task = st.selectbox("Task", ["Understand a concept", "Design a circuit", "Check a calculation", "Interpret simulation results", "Diagnose a fault", "Review a design"], key="r2_task")
        if "r2_messages" not in st.session_state:
            st.session_state.r2_messages = []
        for msg in st.session_state.r2_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        question = st.chat_input("Ask your engineering question…")
        if st.button("Clear conversation", key="r2_clear"):
            st.session_state.r2_messages = []
            st.rerun()
        if question:
            st.session_state.r2_messages.append({"role": "user", "content": question})
            if not api_key:
                st.warning("Your question is retained in this session, but AI replies require an API key. Configure OPENAI_API_KEY in Streamlit Secrets. Calculators work without it.")
            else:
                context = {"project": project, "circuit_description": circuit, "schematic_extraction": schematic_summary or "No schematic file uploaded.", "topology_interpretation": topology_summary or "No topology analysis available.", "student_level": level, "task": task}
                msgs = [{"role": "system", "content": SYSTEM_PROMPT + "\n\nStudent context:\n" + json.dumps(context, ensure_ascii=False)}]
                msgs.extend(st.session_state.r2_messages[-12:])
                payload = json.dumps({"model": model, "messages": msgs, "temperature": 0.25}).encode("utf-8")
                req = urllib.request.Request(endpoint, data=payload, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
                try:
                    with st.spinner("Reasoning through the engineering problem…"):
                        with urllib.request.urlopen(req, timeout=60) as response:
                            data = json.loads(response.read().decode("utf-8"))
                    answer = data["choices"][0]["message"]["content"]
                    st.session_state.r2_messages.append({"role": "assistant", "content": answer})
                except urllib.error.HTTPError as exc:
                    detail = exc.read().decode("utf-8", errors="replace")[:1000]
                    st.session_state.r2_messages.append({"role": "assistant", "content": f"AI service returned HTTP {exc.code}. Check the key, model and endpoint.\n\n{detail}"})
                except Exception as exc:
                    st.session_state.r2_messages.append({"role": "assistant", "content": f"Could not reach the AI service: {type(exc).__name__}: {exc}"})
            st.rerun()
        st.caption("The Copilot cannot inspect the live CircuitJS canvas directly yet. It can now read an exported CircuitJS/Falstad .txt schematic; paste simulator observations separately because extraction does not provide verified simulation measurements.")
    with calc_tab:
        _calculators()
    with guide_tab:
        st.subheader("Release 2 capabilities")
        st.markdown("""
        - Step-by-step engineering explanations and derivations.
        - Project-aware context using the brief and circuit details you provide.
        - Measurement-led troubleshooting and design review.
        - Interpretation of simulation results supplied by you.
        - First-pass extraction of component records and inferred connectivity from an uploaded CircuitJS/Falstad text schematic.
        - Heuristic topology recognition for series/parallel resistor relationships, voltage-divider candidates, RC networks, diode networks/rectifier candidates, and LC networks.
        - Local calculators for Ohm's law, power, voltage dividers, RC time constants and full-wave ripple estimates.
        """)
        st.subheader("Configure AI on the separate test deployment")
        st.markdown("""
        1. Create an API key with your chosen OpenAI API account.
        2. Open the separate Release 2 Streamlit test app settings and add these Secrets:
        
            OPENAI_API_KEY = "your-secret-key"
            OPENAI_MODEL = "gpt-4o-mini"
        
        3. Save and restart the test app. Never put keys in source code or GitHub.
        4. Optional compatible-provider overrides: OPENAI_BASE_URL and OPENAI_MODEL.
        """)
        st.warning("AI advice must be checked against circuit theory, manufacturer datasheets, lab procedures and lecturer requirements. It is not verified simulation output or safety approval.")
