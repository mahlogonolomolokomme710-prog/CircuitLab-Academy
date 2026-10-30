import streamlit as st
from pathlib import Path
from urllib.parse import quote
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from datetime import date

st.set_page_config(page_title="CircuitLab Academy", page_icon="⚡", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
CIRCUITJS_DIR = BASE_DIR / "static" / "circuitjs"
CIRCUITJS_ENTRY = CIRCUITJS_DIR / "circuitjs.html"
PREPARED_DIR = BASE_DIR / "prepared_circuits"

SIMULATIONS = {
    "1. Ohm’s law — DC resistor": {
        "file": "ohms_law.txt",
        "goal": "Explore V = IR using a 5 V DC source and a 1 kΩ resistor.",
        "build": ["Inspect the source and resistor in the loaded circuit.", "Run or pause the simulation and inspect the current display.", "Change the resistor value by double-clicking it, then predict the current before observing the result."],
        "expected": "Ideal current is about 5 mA (I = 5 V / 1,000 Ω).",
        "topic": "Voltage, current and resistance"
    },
    "2. Series resistors": {
        "file": "series_resistors.txt",
        "goal": "Observe how resistances add in a series path.",
        "build": ["Identify both 1 kΩ resistors in the same current path.", "Inspect the total current from the 5 V source.", "Change one resistor and compare the current with your calculation."],
        "expected": "Equivalent resistance is 2 kΩ and ideal source current is about 2.5 mA.",
        "topic": "Series networks"
    },
    "3. Parallel resistors": {
        "file": "parallel_resistors.txt",
        "goal": "Compare current through two parallel 1 kΩ branches.",
        "build": ["Identify the two shared nodes across the resistor branches.", "Compare branch currents and total source current.", "Predict the equivalent resistance before changing component values."],
        "expected": "Equivalent resistance is 500 Ω and ideal total source current is about 10 mA.",
        "topic": "Parallel networks"
    },
    "4. RC charging concept": {
        "file": "rc_charging.txt",
        "goal": "Study a resistor-capacitor network and the time constant concept.",
        "build": ["Identify the resistor and capacitor connected in the circuit.", "Observe the capacitor voltage behaviour in the simulator.", "Use τ = RC to calculate the time constant for the displayed values."],
        "expected": "For 10 kΩ and 100 µF, τ = 1 second. Confirm the source waveform and capacitor response in the simulator; this prepared circuit is an introductory model.",
        "topic": "Capacitors and transients"
    },
    "5. Diode half-wave rectifier": {
        "file": "diode_rectifier.txt",
        "goal": "Observe one-way diode conduction with a low-voltage AC source and load resistor.",
        "build": ["Identify the AC source, diode orientation and load resistor.", "Compare input and load behaviour over positive and negative half-cycles.", "Reverse the diode in a copy of the circuit and predict what changes."],
        "expected": "A single diode provides half-wave rectification in a simple resistive load; it is not a full-wave bridge rectifier.",
        "topic": "Diodes and rectification"
    },
}

def circuit_simulator_url(circuit_key):
    """Return the same-origin CircuitJS URL when bundled assets exist, otherwise use hosted fallback."""
    meta = SIMULATIONS[circuit_key]
    circuit_file = PREPARED_DIR / meta["file"]
    circuit_text = circuit_file.read_text(encoding="utf-8")
    encoded = quote(circuit_text, safe="")
    if CIRCUITJS_ENTRY.is_file():
        return f"/app/static/circuitjs/circuitjs.html?cct={encoded}", True
    return f"https://www.falstad.com/circuit/circuitjs.html?cct={encoded}", False


st.markdown("""
<style>
.block-container {max-width:1450px;padding-top:1.1rem}
.hero {padding:1.3rem 1.5rem;border-radius:16px;background:linear-gradient(120deg,#102a43,#176b87);color:white;margin-bottom:1rem}
.hero h1 {color:white;margin:0 0 .25rem 0}
.hero p {color:#e5f5ff;margin:0;font-size:1.05rem}
.panel {padding:1rem;border:1px solid #d9e2ec;border-radius:12px;background:#f8fbfd}
.warning {padding:.8rem 1rem;border-left:5px solid #e09f3e;background:#fff8e8;border-radius:8px}
</style>
""", unsafe_allow_html=True)

if "done" not in st.session_state:
    st.session_state.done = []
if "project_notes" not in st.session_state:
    st.session_state.project_notes = ""

COMPONENTS = {
    "AC input source": {
        "role": "Provides the low-voltage AC input for the educational supply.",
        "key_specs": "RMS voltage, frequency, isolation, current capability and source impedance.",
        "connection": "The two AC terminals connect to the two AC inputs of the bridge rectifier.",
        "failure": "An unsuitable source can cause insufficient voltage, excessive current or an unsafe build.",
        "level": "Beginner: AC voltage alternates direction. Advanced: source impedance and transformer regulation affect the rectifier's peak voltage and ripple."
    },
    "Bridge rectifier (D1–D4)": {
        "role": "Uses four diodes to make current through the load flow in the same direction on both AC half-cycles.",
        "key_specs": "Repetitive reverse-voltage rating, average forward current, surge current, forward drop and thermal limits.",
        "connection": "The two AC terminals connect to the source. The positive and negative DC terminals feed the smoothing stage.",
        "failure": "Incorrect wiring or inadequate diode ratings can cause incorrect output or component failure.",
        "level": "Beginner: it converts AC to pulsating DC. Advanced: account for two conducting diode drops, peak inverse voltage and surge current."
    },
    "Smoothing capacitor C1": {
        "role": "Stores charge near rectified peaks and supplies the load between peaks to reduce ripple.",
        "key_specs": "Capacitance, voltage rating, polarity, ripple-current rating, ESR and temperature rating.",
        "connection": "Connect across the rectifier's positive and negative DC rails, observing electrolytic polarity.",
        "failure": "Reverse polarity or excessive voltage/ripple current can cause damage.",
        "level": "Beginner: a larger capacitor usually reduces ripple. Advanced: ESR, source impedance, load current and capacitor charging pulses affect real behaviour."
    },
    "Voltage regulator U1": {
        "role": "Maintains an approximately constant output voltage within its specified operating limits.",
        "key_specs": "Input voltage range, output current, dropout/headroom, thermal resistance, protection and pinout.",
        "connection": "Connect input to the smoothed positive rail, ground to the negative rail, and output to the regulated output node. Verify the exact part's datasheet pinout.",
        "failure": "Insufficient input headroom or excessive power dissipation can cause poor regulation or thermal shutdown.",
        "level": "Beginner: it helps hold the output near 5 V. Advanced: estimate dissipation using (Vin − Vout) × Iout and check junction temperature."
    },
    "Output capacitor C2": {
        "role": "May improve regulator stability and transient response when required by the regulator datasheet.",
        "key_specs": "Capacitance, voltage rating, ESR, polarity and placement requirements.",
        "connection": "Place at the regulator output as recommended in the exact regulator datasheet.",
        "failure": "An inappropriate capacitor or layout can affect regulator stability for some devices.",
        "level": "Use the manufacturer's recommended values and placement; do not assume every regulator has identical requirements."
    },
    "Load resistor RLOAD": {
        "role": "Represents a simple load so output current and power can be estimated.",
        "key_specs": "Resistance, tolerance and power rating.",
        "connection": "Connect between the regulated output and the return/ground node.",
        "failure": "Power dissipation above its rating can overheat or damage the resistor.",
        "level": "Use I = V/R and P = V²/R. Choose a rated part with suitable margin."
    },
}
PROJECT_STEPS = [
    ("1. Read the brief", "Set the target output and load requirements before choosing components.", "Write down output voltage, maximum current, acceptable ripple and any lecturer-specified parts."),
    ("2. Follow the energy path", "Trace the functional chain from the isolated AC source through rectification, smoothing and regulation.", "Explain why the regulator cannot replace the rectifier or smoothing capacitor."),
    ("3. Inspect components", "Select each item on the schematic to view its role, key specifications and connection guidance.", "Verify exact part numbers and datasheets before using physical components."),
    ("4. Estimate ripple", "Use the calculator to estimate a starting capacitance for the chosen current and ripple target.", "State the assumptions and confirm the result using simulation or measurement."),
    ("5. Verify the design", "Identify test points and expected waveform changes at each stage.", "Separate calculated, simulated and physically measured results in your notes."),
    ("6. Pre-power inspection", "Check polarity, connections, ratings and source isolation with power disconnected.", "Use a suitable isolated, current-limited low-voltage source; never connect a beginner circuit directly to mains."),
    ("7. Document findings", "Prepare a reproducible report using the report builder.", "Record your own validated results and note any differences from expected behaviour."),
]

def draw_schematic(selected):
    fig, ax = plt.subplots(figsize=(13, 5.2))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6)
    ax.axis("off")
    blue = "#176b87"
    dark = "#243b53"
    focus = "#d62828"

    # Input source
    ax.plot([0.7, 1.35], [3.5, 3.5], color=dark, lw=2)
    ax.plot([0.7, 1.35], [2.3, 2.3], color=dark, lw=2)
    ax.add_patch(Circle((1.35, 2.9), .6, fill=False, lw=2, edgecolor=focus if selected=="AC input source" else dark))
    ax.text(1.35, 2.9, "~", ha="center", va="center", fontsize=24, color=dark)
    ax.text(1.35, 1.85, "AC source", ha="center", fontsize=10, color=dark)
    ax.text(.4, 3.5, "AC1", fontsize=9, va="center")
    ax.text(.4, 2.3, "AC2", fontsize=9, va="center")

    # Bridge block and wires
    ax.plot([1.95, 2.55], [3.5, 3.5], color=dark, lw=2)
    ax.plot([1.95, 2.55], [2.3, 2.3], color=dark, lw=2)
    bridge_color = focus if selected=="Bridge rectifier (D1–D4)" else dark
    ax.add_patch(Rectangle((2.55, 1.85), 1.65, 2.1, fill=False, lw=2, edgecolor=bridge_color))
    ax.text(3.375, 3.05, "BRIDGE", ha="center", va="center", fontsize=11, weight="bold", color=bridge_color)
    ax.text(3.375, 2.62, "D1–D4", ha="center", va="center", fontsize=11, color=bridge_color)
    ax.text(2.7, 2.05, "~  ~", ha="left", fontsize=11, color=bridge_color)
    ax.text(3.95, 3.72, "+", ha="center", fontsize=15, color=bridge_color)
    ax.text(3.95, 2.0, "−", ha="center", fontsize=15, color=bridge_color)

    # DC rails
    ax.plot([4.2, 5.05], [3.5, 3.5], color=dark, lw=2)
    ax.plot([4.2, 5.05], [2.3, 2.3], color=dark, lw=2)
    ax.text(4.45, 3.72, "+DC", fontsize=9, color=dark)
    ax.text(4.45, 2.0, "0 V", fontsize=9, color=dark)

    # C1 across rails
    c_color = focus if selected=="Smoothing capacitor C1" else dark
    ax.plot([5.05, 5.55], [3.5, 3.5], color=dark, lw=2)
    ax.plot([5.05, 5.55], [2.3, 2.3], color=dark, lw=2)
    ax.plot([5.55, 5.55], [3.5, 3.08], color=dark, lw=2)
    ax.plot([5.25, 5.85], [3.08, 3.08], color=c_color, lw=2.5)
    ax.plot([5.25, 5.85], [2.85, 2.85], color=c_color, lw=2.5)
    ax.plot([5.55, 5.55], [2.85, 2.3], color=dark, lw=2)
    ax.text(5.55, 4.05, "C1", ha="center", fontsize=11, weight="bold", color=c_color)
    ax.text(5.55, 2.55, "+", ha="center", fontsize=10, color=c_color)
    ax.text(5.55, 1.95, "Smoothing", ha="center", fontsize=9, color=dark)

    # Regulator block
    ax.plot([5.55, 6.45], [3.5, 3.5], color=dark, lw=2)
    reg_color = focus if selected=="Voltage regulator U1" else dark
    ax.add_patch(Rectangle((6.45, 2.35), 1.8, 1.5, fill=False, lw=2, edgecolor=reg_color))
    ax.text(7.35, 3.25, "U1", ha="center", fontsize=12, weight="bold", color=reg_color)
    ax.text(7.35, 2.85, "5 V regulator", ha="center", fontsize=9, color=reg_color)
    ax.text(6.55, 3.62, "IN", fontsize=8, color=dark)
    ax.text(7.2, 2.15, "GND", fontsize=8, color=dark)
    ax.text(7.85, 3.62, "OUT", fontsize=8, color=dark)
    ax.plot([7.35, 7.35], [2.35, 2.3], color=dark, lw=2)
    ax.plot([5.05, 8.9], [2.3, 2.3], color=dark, lw=2)

    # Output rail and C2
    ax.plot([8.25, 9.0], [3.5, 3.5], color=dark, lw=2)
    ax.plot([9.0, 9.0], [3.5, 3.05], color=dark, lw=2)
    c2_color = focus if selected=="Output capacitor C2" else dark
    ax.plot([8.7, 9.3], [3.05, 3.05], color=c2_color, lw=2.5)
    ax.plot([8.7, 9.3], [2.82, 2.82], color=c2_color, lw=2.5)
    ax.plot([9.0, 9.0], [2.82, 2.3], color=dark, lw=2)
    ax.text(9.0, 4.05, "C2*", ha="center", fontsize=11, weight="bold", color=c2_color)

    # Load resistor simplified zig-zag
    load_color = focus if selected=="Load resistor RLOAD" else dark
    ax.plot([9.0, 10.25], [3.5, 3.5], color=dark, lw=2)
    ax.plot([10.25, 10.25], [3.5, 3.25], color=dark, lw=2)
    zigx = [10.25,10.05,10.45,10.05,10.45,10.05,10.25]
    zigy = [3.25,3.08,2.9,2.72,2.54,2.36,2.2]
    ax.plot(zigx, zigy, color=load_color, lw=2.5)
    ax.plot([10.25, 10.25], [2.2, 2.0], color=dark, lw=2)
    ax.plot([10.25, 10.25], [2.0, 2.3], color=dark, lw=2)
    ax.text(10.7, 2.8, "RLOAD", fontsize=10, weight="bold", color=load_color)
    ax.text(10.7, 2.48, "Load", fontsize=9, color=dark)
    ax.text(9.0, 1.75, "Regulated output", ha="center", fontsize=9, color=dark)

    ax.text(6.5, 5.25, "Guided power-supply schematic view", ha="center", fontsize=16, weight="bold", color=dark)
    ax.text(6.5, 4.8, "Select a component in the app to highlight it and open its learning card.", ha="center", fontsize=10, color=blue)
    ax.text(6.5, .8, "*C2 and exact regulator support components must follow the selected regulator datasheet.", ha="center", fontsize=9, color="#9b2226")
    ax.text(6.5, .45, "Educational schematic view — verify exact pinouts, values and topology before physical construction.", ha="center", fontsize=9, color="#9b2226")
    fig.tight_layout()
    return fig

def report_text(title, aim, requirements, parts, calc, method, results, discussion, conclusion):
    return f"""# {title}

**Date:** {date.today().isoformat()}

## Aim
{aim}

## Design requirements
{requirements}

## Theory
A typical regulated DC supply uses rectification to convert AC to pulsating DC, filtering to reduce ripple, and regulation to maintain the output within the regulator's operating limits. Confirm the theory and topology against the assigned practical.

## Components and specifications
{parts}

## Design calculations
{calc}

## Method
{method}

## Results and observations
{results}

## Discussion
{discussion}

## Conclusion
{conclusion}

## Verification checklist
- [ ] Exact component part numbers and datasheets verified.
- [ ] Pinouts and polarities checked.
- [ ] Source isolation and current limit verified.
- [ ] Calculations and units checked.
- [ ] Simulated results distinguished from physical measurements.
- [ ] Design reviewed against lecturer instructions and relevant safety practices.
"""

st.sidebar.title("⚡ CircuitLab Academy")
st.sidebar.caption("TUT Electrical Engineering • Prototype v0.5")
page = st.sidebar.radio("Workspace", [
    "Dashboard", "Circuit Workspace", "Circuit Simulator", "Prepared Circuit Library", "Guided Build", "Component Library",
    "Calculators", "Knowledge Check", "Project Report", "Curriculum Map"
])
st.sidebar.markdown("---")
st.sidebar.caption("Guided circuits and simulator • v0.5 preview")

if page == "Dashboard":
    st.markdown("""<div class="hero"><h1>CircuitLab Academy</h1><p>Understand the theory. Explore the schematic. Learn to build circuits.</p></div>""", unsafe_allow_html=True)
    a,b,c = st.columns(3)
    a.metric("Flagship project", "Regulated DC supply")
    b.metric("Guided stages", "7")
    c.metric("Build progress", f"{len(st.session_state.done)}/7")
    st.subheader("Start your first project")
    st.write("Explore a guided 5 V DC power-supply design. Select components, learn their purpose, estimate values and prepare a practical report.")
    if st.button("Open Circuit Workspace", type="primary"):
        st.session_state["nav_hint"] = "Circuit Workspace"
        st.info("Choose **Circuit Workspace** from the sidebar.")
    st.subheader("Learning pathway")
    cols = st.columns(4)
    for col, title, body in zip(cols,
        ["Foundations","Analogue","Digital","Design & testing"],
        ["Circuit laws, passive parts and diodes","Transistors, amplifiers and filters","Logic, sequential circuits and embedded basics","Power electronics, measurements and PCB workflow"]):
        with col:
            st.markdown(f'<div class="panel"><h4>{title}</h4>{body}</div>', unsafe_allow_html=True)
    st.info("Curriculum coverage is an initial plan. Current TUT module guides and practical outcomes must be verified before claiming complete coverage.")

elif page == "Circuit Workspace":
    st.title("Interactive circuit workspace")
    st.write("Select a component to highlight it on the schematic and open a focused explanation. This is the concept schematic for guided learning. For live electrical behaviour, open the Circuit Simulator workspace below.")
    chosen = st.selectbox("Inspect a component", list(COMPONENTS.keys()))
    fig = draw_schematic(chosen)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    info = COMPONENTS[chosen]
    left, right = st.columns([1.2,1])
    with left:
        st.subheader(chosen)
        st.markdown("**Function**")
        st.write(info["role"])
        st.markdown("**How it connects**")
        st.write(info["connection"])
    with right:
        st.markdown("**Ratings / datasheet checks**")
        st.write(info["key_specs"])
        st.markdown("**Learning levels**")
        st.write(info["level"])
        st.warning(info["failure"])
    st.subheader("Design values (learning inputs)")
    if chosen == "Smoothing capacitor C1":
        cap = st.number_input("Example capacitance (µF)", min_value=10, max_value=100000, value=1000, step=100)
        st.caption(f"Selected learning value: {cap} µF. Suitability depends on load, ripple target, voltage rating, ripple current and source characteristics.")
    elif chosen == "Load resistor RLOAD":
        resistance = st.number_input("Example load resistance (Ω)", min_value=1.0, max_value=100000.0, value=50.0, step=5.0)
        output_v = st.number_input("Assumed output voltage (V)", min_value=0.1, max_value=50.0, value=5.0, step=0.5)
        st.metric("Estimated load current", f"{output_v/resistance*1000:.1f} mA")
        st.metric("Estimated resistor dissipation", f"{output_v**2/resistance:.3f} W")
    elif chosen == "Voltage regulator U1":
        vin = st.number_input("Illustrative regulator input (V DC)", min_value=5.1, max_value=30.0, value=9.0, step=0.5)
        iout = st.number_input("Illustrative output current (mA)", min_value=1.0, max_value=1000.0, value=100.0, step=10.0)
        vout = 5.0
        p = max(0.0, vin-vout) * iout/1000
        st.metric("Approx. linear-regulator dissipation", f"{p:.2f} W")
        st.caption("Illustrative estimate only. Confirm input limits, dropout/headroom, package thermal resistance and junction temperature from the exact datasheet.")
    else:
        st.caption("Component values and part numbers must be selected from the project brief and verified against manufacturer datasheets.")

elif page == "Circuit Simulator" or page == "Prepared Circuit Library":
    if page == "Circuit Simulator":
        st.title("Interactive Circuit Simulator")
        st.write("Choose a prepared example, inspect the circuit, and change component values to test your predictions.")
    else:
        st.title("Prepared Circuit Library")
        st.write("A starter library of editable examples for core electronics concepts. Select a circuit to load it directly into the simulator.")

    st.markdown('<div class="warning"><b>Learning and safety:</b> Simulation is a model, not proof that a physical design is safe. Verify component ratings and lecturer requirements. Never connect a beginner circuit directly to mains electricity.</div>', unsafe_allow_html=True)
    selected = st.selectbox("Choose a prepared circuit", list(SIMULATIONS.keys()), key="prepared_circuit_choice")
    ex = SIMULATIONS[selected]
    st.subheader("Learning objective")
    st.write(ex["goal"])
    st.caption("Topic: " + ex["topic"])
    st.subheader("Guided investigation")
    for i, step in enumerate(ex["build"], 1):
        st.markdown(f"**{i}.** {step}")
    st.info("**Expected ideal result:** " + ex["expected"])

    circuit_url, is_self_hosted = circuit_simulator_url(selected)
    if is_self_hosted:
        st.success("Self-hosted CircuitJS assets detected. The simulator is being served from this app's own static folder.")
    else:
        st.warning("Self-hosted assets are not installed in this working copy yet. This session is using the hosted fallback. Run `python install_circuitjs.py`, then commit the generated `static/circuitjs/` assets to GitHub to enable self-hosting in Streamlit Cloud.")
    st.subheader("Live circuit")
    st.iframe(circuit_url, height=760)

    st.subheader("Circuit notes")
    notes = st.text_area("Record your prediction, observations and explanation", key="circuit_notes", placeholder="Prediction → observation → explanation")
    st.download_button("Download investigation notes", data=(f"CircuitLab Academy — {selected}\n\nObjective: {ex['goal']}\n\nExpected result: {ex['expected']}\n\nStudent notes:\n{notes}\n"), file_name=ex["file"].replace(".txt", "_notes.txt"), mime="text/plain")

    with st.expander("Basic simulator controls"):
        st.markdown("""- Click or drag components to inspect and reposition them. Double-click a component to edit its value.
- Use the simulator's run/pause and scope controls to inspect behaviour.
- Make a prediction before changing a value, then record what changed.
- Save/export a copy using CircuitJS controls where available.""")
    with st.expander("Source and licence"):
        st.markdown("CircuitJS1 is an upstream open-source project by Paul Falstad and contributors, adapted for browser use by Iain Sharp. See the [official repository](https://github.com/sharpie7/circuitjs1). It is distributed under GPL version 2 or later. Preserve copyright/licence notices and comply with the applicable source-distribution terms when redistributing it.")

elif page == "Guided Build":
    st.title("Guided build: regulated 5 V DC supply")
    st.markdown('<div class="warning"><b>Safety:</b> For any physical beginner build, use a suitable isolated, current-limited low-voltage source. Never connect a breadboard or beginner circuit directly to mains electricity.</div>', unsafe_allow_html=True)
    step_index = st.selectbox("Choose a project stage", range(len(PROJECT_STEPS)), format_func=lambda i: PROJECT_STEPS[i][0])
    title, goal, action = PROJECT_STEPS[step_index]
    st.header(title)
    st.markdown(f"**Goal:** {goal}")
    st.write(action)
    st.markdown("**Suggested evidence to record**")
    evidence = [
        "A written requirement table with voltage, current and ripple targets.",
        "A labelled diagram identifying each functional stage.",
        "A component table with part number, value and key ratings.",
        "The capacitor calculation with assumptions and units.",
        "A test-point table showing what will be measured or simulated.",
        "A signed-off pre-power inspection checklist.",
        "A report separating calculations, simulated values and measured results."
    ][step_index]
    st.info(evidence)
    checked = step_index in st.session_state.done
    if st.button("Mark stage complete" if not checked else "Undo completion"):
        if checked:
            st.session_state.done.remove(step_index)
        else:
            st.session_state.done.append(step_index)
        st.rerun()
    st.progress(len(st.session_state.done)/len(PROJECT_STEPS), text=f"{len(st.session_state.done)} of {len(PROJECT_STEPS)} stages completed")
    if step_index < len(PROJECT_STEPS)-1:
        st.caption(f"Next: {PROJECT_STEPS[step_index+1][0]}")

elif page == "Component Library":
    st.title("Component library")
    search = st.text_input("Search by component or topic", placeholder="diode, capacitor, regulator…")
    for name, info in COMPONENTS.items():
        if search.lower() in (name + " " + " ".join(info.values())).lower():
            with st.expander(name, expanded=bool(search)):
                st.markdown(f"**Function:** {info['role']}")
                st.markdown(f"**Connection guidance:** {info['connection']}")
                st.markdown(f"**Key specifications:** {info['key_specs']}")
                st.markdown(f"**Learning levels:** {info['level']}")
                st.warning(info["failure"])
    st.info("Future library additions: resistor colour codes, semiconductor pinouts, package photos, schematic symbols, manufacturer datasheets and simulation models.")

elif page == "Calculators":
    st.title("Engineering calculators")
    st.subheader("Smoothing capacitor — first-order estimate")
    st.latex(r"C \\approx \\frac{I_{load}}{f_{ripple} V_{ripple(pp)}}")
    c1,c2,c3 = st.columns(3)
    with c1:
        current_ma = st.number_input("Load current (mA)", min_value=1.0, max_value=5000.0, value=100.0, step=10.0)
    with c2:
        frequency = st.selectbox("AC frequency (Hz)", [50,60], index=0)
    with c3:
        ripple = st.number_input("Target ripple (V peak-to-peak)", min_value=0.01, max_value=10.0, value=1.0, step=0.1)
    fripple = 2*frequency
    capacitance = (current_ma/1000)/(fripple*ripple)
    st.metric("Estimated capacitance", f"{capacitance*1_000_000:,.0f} µF")
    st.caption(f"Assumes a full-wave rectifier, so ripple frequency ≈ {fripple} Hz. This approximation does not verify regulator headroom, ESR, inrush current, capacitor ripple-current rating or diode stress.")
    st.divider()
    st.subheader("Resistor current and power")
    voltage = st.number_input("Voltage across resistor (V)", min_value=0.0, max_value=1000.0, value=5.0, step=0.5)
    resistance = st.number_input("Resistance (Ω)", min_value=0.1, max_value=1_000_000.0, value=50.0, step=5.0)
    st.metric("Current", f"{voltage/resistance*1000:.2f} mA")
    st.metric("Power", f"{voltage**2/resistance:.3f} W")
    st.caption("Choose a suitable resistor rating with thermal margin; verify the actual circuit conditions.")

elif page == "Knowledge Check":
    st.title("Knowledge check")
    with st.form("quiz"):
        q1 = st.radio("1. What does a bridge rectifier do?", ["Regulates voltage exactly", "Converts AC to pulsating DC", "Stores charge", "Measures current"])
        q2 = st.radio("2. What does the smoothing capacitor mainly do?", ["Reduces ripple", "Increases source frequency", "Replaces all regulators", "Provides mains isolation"])
        q3 = st.radio("3. What must be checked for a linear regulator?", ["Only its colour", "Input headroom, load current and thermal limits", "Nothing if output is 5 V", "Only its physical size"])
        q4 = st.radio("4. What is appropriate for a beginner physical project?", ["Mains on a breadboard", "Isolated current-limited low-voltage source", "Any transformer", "A wall outlet connected to a capacitor"])
        submit = st.form_submit_button("Check answers", type="primary")
    if submit:
        results = [
            q1 == "Converts AC to pulsating DC",
            q2 == "Reduces ripple",
            q3 == "Input headroom, load current and thermal limits",
            q4 == "Isolated current-limited low-voltage source"
        ]
        score = sum(results)
        st.metric("Score", f"{score}/4")
        if score == 4: st.success("All correct — excellent.")
        else: st.info("Review the relevant component cards and try again.")

elif page == "Project Report":
    st.title("Practical report builder")
    st.write("This produces a report draft. Replace prompts with your own work and validated results.")
    with st.form("report"):
        title = st.text_input("Practical title", "Regulated DC power supply")
        aim = st.text_area("Aim", "To study the stages of a regulated DC power supply.")
        requirements = st.text_area("Requirements", "Target: 5 V DC, up to 100 mA. Verify against the assigned brief.")
        parts = st.text_area("Components and ratings", "Enter exact part numbers, values, ratings and datasheet sources.")
        calc = st.text_area("Calculations", "Show equations, substitutions, assumptions and units.")
        method = st.text_area("Method", "Describe the actual simulation or physical procedure followed.")
        results = st.text_area("Results", "Enter your own measured or simulated results and label them correctly.")
        discussion = st.text_area("Discussion", "")
        conclusion = st.text_area("Conclusion", "")
        submit_report = st.form_submit_button("Prepare downloadable report", type="primary")
    if submit_report:
        content = report_text(title, aim, requirements, parts, calc, method, results, discussion, conclusion)
        st.download_button("Download Markdown report", content, file_name="circuitlab_practical_report.md", mime="text/markdown")
        st.success("Report draft ready. Check it carefully before submission.")

elif page == "Curriculum Map":
    st.title("Initial curriculum map")
    st.write("Proposed coverage for the first release. This is not yet a verified mapping to every current TUT module descriptor.")
    mapdata = {
        "Foundational": ["Electrical quantities and measurement","Ohm's law and Kirchhoff's laws","DC network analysis","Resistors, capacitors and inductors","Diodes, rectification and power supplies","Introductory BJT/FET operation"],
        "Intermediate": ["Transistor biasing and amplifiers","Operational amplifiers and feedback","Filters and oscillators","Switching circuits","Waveforms, gain and frequency response","Practical fault diagnosis"],
        "Advanced expansion": ["Multistage analogue design","Power conversion","Digital logic and sequential circuits","Embedded interfaces","Sensors and instrumentation","PCB design and design-rule checking"]
    }
    for level, topics in mapdata.items():
        with st.expander(level, expanded=True):
            for topic in topics:
                st.checkbox(topic, key="map_"+topic)
    st.subheader("To validate against TUT")
    st.markdown("- Obtain the current module descriptors and practical manuals.")
    st.markdown("- Map each official learning outcome to a lesson, project and assessment.")
    st.markdown("- Record module code, year, prerequisites and document version.")
    st.markdown("- Have a subject specialist review calculations, schematics and safety guidance.")

st.sidebar.markdown("---")
st.sidebar.caption("Prototype name. Verify all physical designs against datasheets, lecturer instructions and appropriate safety practices.")
