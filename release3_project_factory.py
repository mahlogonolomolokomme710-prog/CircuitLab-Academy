"""Release 3.8 — Engineering Project Factory.

Creates structured, editable learning briefs and first-pass calculations.
All calculations are transparent educational estimates, not design approval.
"""
from __future__ import annotations

from typing import Any
import math

PROJECTS: dict[str, dict[str, Any]] = {
    "regulated_supply": {
        "name": "Regulated low-voltage DC power supply",
        "level": "Intermediate",
        "goal": "Convert an isolated low-voltage AC secondary into a smoothed and regulated DC output for a defined load.",
        "outcomes": ["Explain transformer isolation, rectification, reservoir filtering and regulation.",
                     "Estimate load demand, ripple and regulator dissipation.",
                     "Compare half-wave and full-wave rectification and justify a design choice."],
        "requirements": ["Specify output voltage, maximum load current and permitted ripple.",
                        "Use an appropriately isolated low-voltage AC source in supervised laboratory work.",
                        "Check diode, capacitor, transformer and regulator datasheets."],
        "blocks": ["Isolated low-voltage AC source", "Rectifier", "Reservoir capacitor", "Linear regulator", "DC load"],
        "bom": [("T1", "Isolated low-voltage transformer", "Secondary voltage/current selected from load and headroom calculations"),
                ("D1–D4", "Rectifier diodes or bridge", "Verify IF(AV), IFSM, VRRM and thermal ratings"),
                ("C1", "Reservoir capacitor", "Calculate capacitance; verify voltage, ripple-current and ESR ratings"),
                ("U1", "Linear regulator", "Verify input range, dropout, current and thermal limits"),
                ("C2", "Regulator bypass/output capacitors", "Use regulator datasheet recommendations"),
                ("F1", "Protection", "Select only after a proper protection and safety assessment")],
        "workflow": ["Write electrical output and load requirements.",
                     "Estimate load power and regulator input headroom.",
                     "Use the Release 3.5 Power Supply Studio for ripple, transformer and thermal estimates.",
                     "Select components from manufacturer datasheets.",
                     "Draw the schematic and validate connections and ratings.",
                     "Simulate using suitable component models; compare with hand calculations.",
                     "Build only the supervised isolated low-voltage section and record measurements."],
        "tests": ["No-load output voltage", "Loaded output voltage at minimum and maximum load",
                  "Ripple at defined load", "Regulator temperature after thermal stabilisation",
                  "Protection and polarity checks"],
        "rubric": {"Requirements and specifications": 15, "Theory and calculations": 20,
                   "Component selection and datasheets": 15, "Schematic and simulation": 15,
                   "Testing and interpretation": 20, "Engineering report and safety": 15},
        "safety": "Educational planning only. No mains-side design, wiring or construction instructions are provided. Use a certified isolated low-voltage source under supervision."
    },
    "ldr_light": {
        "name": "Automatic LDR-controlled light",
        "level": "Beginner–Intermediate",
        "goal": "Design a light-sensitive control that switches an LED or low-voltage lamp according to ambient illumination.",
        "outcomes": ["Explain an LDR and voltage-divider behaviour.", "Predict how the divider output changes between bright and dark conditions.",
                     "Explain the role of a transistor or comparator as a switching stage."],
        "requirements": ["Define the intended bright/dark switching behaviour.", "Choose a low-voltage supply and a safe LED/load current.",
                        "Account for threshold adjustment and possible hysteresis to prevent flicker."],
        "blocks": ["Low-voltage DC supply", "LDR sensing divider", "Threshold/switching stage", "LED indicator or low-voltage lamp"],
        "bom": [("LDR1", "Light-dependent resistor", "Measure or obtain resistance range under stated illumination"),
                ("R1", "Divider resistor or potentiometer", "Choose with divider calculations"),
                ("Q1/U1", "Transistor or comparator stage", "Select using datasheet limits and switching requirements"),
                ("RLED", "LED current-limiting resistor", "Calculate from supply, LED forward voltage and target current"),
                ("LED1", "Indicator LED", "Verify polarity and current rating")],
        "workflow": ["Measure/record LDR resistance in bright and dark conditions.",
                     "Calculate divider voltage for both conditions.",
                     "Choose a switching threshold between the measured conditions.",
                     "Select a transistor/comparator stage and verify its datasheet limits.",
                     "Simulate the divider and switching stage with suitable models.",
                     "Test switching at several illumination levels and check for flicker."],
        "tests": ["Divider voltage in bright condition", "Divider voltage in dark condition",
                  "Switching threshold and repeatability", "LED current", "Behaviour near threshold"],
        "rubric": {"Sensor theory and requirements": 15, "Divider calculations": 20,
                   "Switching-stage design": 20, "Simulation and schematic": 15,
                   "Testing and interpretation": 20, "Report and safety": 10},
        "safety": "Use a low-voltage DC supply. Do not connect lighting circuits to building wiring or mains."
    },
    "rc_delay": {
        "name": "RC timing and delay circuit",
        "level": "Beginner",
        "goal": "Use a resistor-capacitor network to create a predictable charging delay and understand its transient response.",
        "outcomes": ["Derive the RC time constant.", "Interpret exponential capacitor charging.",
                     "Relate the time constant to a practical switching threshold."],
        "requirements": ["Define supply voltage and target delay.", "Select capacitor voltage/polarity/type correctly.",
                        "State the threshold assumption used to define the delay."],
        "blocks": ["Low-voltage DC supply", "Series resistor", "Timing capacitor", "High-impedance measurement or switching input"],
        "bom": [("R1", "Timing resistor", "Calculate from target time constant and selected capacitor"),
                ("C1", "Timing capacitor", "Check capacitance tolerance, leakage and voltage rating"),
                ("U1/Q1", "Optional threshold/switching stage", "Choose threshold and input characteristics"),
                ("S1", "Low-voltage switch", "For controlled charging/reset")],
        "workflow": ["Choose the timing threshold (e.g. 63.2% or 90% of final voltage).",
                     "Calculate the required RC time constant.",
                     "Select practical standard R and C values and calculate the resulting delay.",
                     "Plot the expected charging curve in the Dynamic Circuit Laboratory.",
                     "Measure capacitor voltage against time and compare with the model."],
        "tests": ["Initial capacitor voltage", "Voltage at one time constant", "Time to chosen threshold",
                  "Repeatability after discharge", "Effect of component tolerance"],
        "rubric": {"Theory and derivation": 20, "Component selection": 15,
                   "Calculations": 20, "Simulation": 15, "Measurements and analysis": 20, "Report": 10},
        "safety": "Use a low-voltage supply and observe capacitor polarity and voltage ratings. Discharge capacitors safely before handling."
    },
    "led_driver": {
        "name": "LED indicator and current-limiting driver",
        "level": "Beginner",
        "goal": "Design a low-voltage LED indicator with a calculated series resistor and verified operating current.",
        "outcomes": ["Explain LED forward voltage and current.", "Apply Ohm's law and power equations.",
                     "Choose a resistor with suitable power margin."],
        "requirements": ["Specify supply voltage, LED forward voltage and target current.",
                        "Use a current-limiting resistor unless a suitable driver is designed.",
                        "Verify LED and resistor ratings."],
        "blocks": ["Low-voltage DC supply", "Series current-limiting resistor", "LED load"],
        "bom": [("V1", "Low-voltage DC source", "Set within component ratings"),
                ("R1", "Series resistor", "Calculate R=(Vs−Vf)/If; choose a suitable standard value"),
                ("D1", "LED", "Check colour-specific Vf, maximum current and polarity")],
        "workflow": ["Obtain LED forward-voltage information from its datasheet.",
                     "Choose a conservative target current within the LED rating.",
                     "Calculate minimum series resistance and resistor dissipation.",
                     "Choose a standard resistor and recalculate actual current.",
                     "Simulate and validate current and resistor power.",
                     "Measure current and LED voltage with a current-limited supply."],
        "tests": ["LED polarity", "LED forward voltage", "Operating current", "Resistor dissipation and temperature"],
        "rubric": {"Theory": 15, "Current and resistor calculations": 25,
                   "Component ratings": 15, "Schematic/simulation": 15,
                   "Measurements": 20, "Report and safety": 10},
        "safety": "Use a current-limited low-voltage DC supply. Never connect an LED directly across a voltage source without current limiting."
    },
    "motor_pwm": {
        "name": "Low-voltage DC motor PWM controller",
        "level": "Intermediate",
        "goal": "Develop a conceptual PWM motor-control design and relate duty cycle to average applied voltage and load behaviour.",
        "outcomes": ["Explain PWM duty cycle and switching.", "Estimate average ideal motor-terminal voltage.",
                     "Identify driver current, thermal and inductive-energy requirements."],
        "requirements": ["Use a low-voltage DC motor with known rated voltage and stall current.",
                        "Select a driver rated for motor current and transient stress.",
                        "Include appropriate inductive-energy management and supply decoupling."],
        "blocks": ["Low-voltage DC source", "PWM control signal", "Power switching stage", "Motor and suppression path"],
        "bom": [("M1", "Low-voltage DC motor", "Record rated voltage, running current and stall current"),
                ("Q1", "MOSFET/motor driver", "Verify RDS(on), current, voltage, thermal and SOA limits"),
                ("D1", "Flyback/suppression device", "Select for motor current and switching behaviour where required"),
                ("C1", "Supply decoupling", "Select from driver and motor transient requirements"),
                ("CTRL", "PWM controller", "Define frequency and duty-cycle range")],
        "workflow": ["Record motor rated voltage, running current and stall current.",
                     "Define the required speed-control range and PWM frequency.",
                     "Estimate ideal average voltage from duty cycle.",
                     "Select a driver using stall current, transient and thermal ratings.",
                     "Review the inductive current path and decoupling.",
                     "Simulate using a suitable switching model and test under supervised current-limited conditions."],
        "tests": ["PWM frequency and duty cycle", "Motor terminal voltage", "Driver temperature",
                  "Start-up/stall current protection", "Response across load conditions"],
        "rubric": {"Requirements and motor data": 15, "PWM theory/calculations": 20,
                   "Driver and protection selection": 20, "Schematic/simulation": 15,
                   "Testing and interpretation": 20, "Report and safety": 10},
        "safety": "Use only a low-voltage motor supply with current limiting and suitable protection. Motor stall current can greatly exceed running current."
    },
    "astable_555": {
        "name": "555 timer astable oscillator",
        "level": "Intermediate",
        "goal": "Design a 555 timer astable circuit and predict its oscillation frequency and duty cycle.",
        "outcomes": ["Explain capacitor charge/discharge paths in astable operation.",
                     "Apply the approximate 555 frequency and duty-cycle equations.",
                     "Compare theoretical and measured timing."],
        "requirements": ["Specify target frequency and supply voltage within the selected timer datasheet limits.",
                        "Choose timing R and C values within manufacturer recommendations.",
                        "Check output loading and timing-component tolerances."],
        "blocks": ["Low-voltage DC supply", "555 timing network", "Timing capacitor", "Output/load"],
        "bom": [("U1", "555 timer", "Check exact bipolar/CMOS timer datasheet and supply limits"),
                ("RA/RB", "Timing resistors", "Choose from target frequency and duty cycle"),
                ("C1", "Timing capacitor", "Check tolerance, leakage and voltage rating"),
                ("C2", "Supply bypass capacitor", "Follow timer datasheet guidance"),
                ("RL", "Output load", "Keep within output current and thermal limits")],
        "workflow": ["Set a target oscillation frequency and desired duty cycle.",
                     "Choose a practical timing capacitor.",
                     "Calculate RA and RB using the approximate astable equations.",
                     "Check duty-cycle limitations of the standard two-resistor topology.",
                     "Simulate with the selected timer model and inspect output waveform.",
                     "Measure frequency and duty cycle and quantify error."],
        "tests": ["Oscillation starts reliably", "Measured frequency", "Measured duty cycle",
                  "Output high/low levels under load", "Frequency sensitivity to component tolerance"],
        "rubric": {"Operating principle": 15, "Timing calculations": 25,
                   "Component selection": 15, "Simulation": 15,
                   "Measurement and analysis": 20, "Report and safety": 10},
        "safety": "Use a low-voltage DC supply and observe the selected timer's datasheet limits."
    },
}


def _positive(inputs: dict[str, Any], key: str, default: float) -> float:
    try:
        value = float(inputs.get(key, default))
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be numeric.")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{key} must be finite and greater than zero.")
    return value


def calculate_project(project_id: str, inputs: dict[str, Any]) -> dict[str, float | str]:
    """Run transparent first-pass calculations for supported project templates."""
    if project_id not in PROJECTS:
        raise ValueError("Unknown project template.")
    if project_id == "led_driver":
        vs = _positive(inputs, "supply_v", 5.0)
        vf = _positive(inputs, "led_vf", 2.0)
        ma = _positive(inputs, "target_ma", 10.0)
        if vf >= vs:
            raise ValueError("LED forward voltage must be below the supply voltage.")
        current = ma / 1000.0
        rmin = (vs - vf) / current
        e12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
        decade = 10 ** math.floor(math.log10(rmin))
        standard = next((n * decade for n in e12 if n * decade >= rmin), None)
        if standard is None:
            standard = 10 * decade
        actual_ma = (vs - vf) / standard * 1000.0
        power = (vs - vf) ** 2 / standard
        return {"minimum_resistance_ohm": rmin, "selected_e12_ohm": standard,
                "actual_current_ma": actual_ma, "resistor_power_w": power,
                "suggested_power_rating_w": 2 * power}
    if project_id == "ldr_light":
        supply = _positive(inputs, "supply_v", 5.0)
        bright = _positive(inputs, "ldr_bright_ohm", 1000.0)
        dark = _positive(inputs, "ldr_dark_ohm", 100000.0)
        fixed = _positive(inputs, "fixed_ohm", 10000.0)
        # LDR is the upper divider leg; fixed resistor is the lower leg.
        vb = supply * fixed / (bright + fixed)
        vd = supply * fixed / (dark + fixed)
        return {"bright_output_v": vb, "dark_output_v": vd,
                "bright_dark_difference_v": abs(vb - vd),
                "divider_current_bright_ma": supply / (bright + fixed) * 1000.0,
                "divider_current_dark_ma": supply / (dark + fixed) * 1000.0}
    if project_id == "rc_delay":
        resistance = _positive(inputs, "resistance_ohm", 100000.0)
        capacitance_uf = _positive(inputs, "capacitance_uf", 100.0)
        supply = _positive(inputs, "supply_v", 5.0)
        threshold = float(inputs.get("threshold_fraction", 0.632))
        if not math.isfinite(threshold) or not 0 < threshold < 1:
            raise ValueError("Threshold fraction must be between 0 and 1.")
        tau = resistance * capacitance_uf * 1e-6
        delay = -tau * math.log(1 - threshold)
        return {"time_constant_s": tau, "threshold_fraction": threshold,
                "threshold_voltage_v": supply * threshold, "estimated_delay_s": delay,
                "voltage_at_one_tau_v": supply * (1 - math.exp(-1))}
    if project_id == "motor_pwm":
        supply = _positive(inputs, "supply_v", 12.0)
        duty = float(inputs.get("duty_percent", 50.0))
        current = _positive(inputs, "motor_current_a", 0.5)
        if not math.isfinite(duty) or not 0 <= duty <= 100:
            raise ValueError("Duty cycle must be between 0 and 100 percent.")
        return {"duty_percent": duty, "ideal_average_voltage_v": supply * duty / 100.0,
                "ideal_average_input_power_w": supply * current * duty / 100.0,
                "motor_current_a": current}
    if project_id == "astable_555":
        ra = _positive(inputs, "ra_ohm", 10000.0)
        rb = _positive(inputs, "rb_ohm", 47000.0)
        cap = _positive(inputs, "capacitance_nf", 10.0) * 1e-9
        high = 0.693 * (ra + rb) * cap
        low = 0.693 * rb * cap
        period = high + low
        return {"frequency_hz": 1.0 / period, "duty_percent": high / period * 100.0,
                "high_time_s": high, "low_time_s": low}
    if project_id == "regulated_supply":
        voltage = _positive(inputs, "output_v", 5.0)
        current = _positive(inputs, "load_current_ma", 100.0) / 1000.0
        ripple = _positive(inputs, "ripple_target_v", 1.0)
        return {"output_voltage_v": voltage, "load_current_a": current,
                "load_power_w": voltage * current,
                "equivalent_load_ohm": voltage / current,
                "ripple_target_v": ripple}
    raise ValueError("No calculator is available for this project template.")


def build_project_pack(project_id: str, inputs: dict[str, Any] | None = None,
                       title: str | None = None, student_level: str | None = None) -> dict[str, Any]:
    if project_id not in PROJECTS:
        raise ValueError("Choose a project from the catalogue.")
    template = PROJECTS[project_id]
    calculations = calculate_project(project_id, inputs or {})
    return {
        "project_id": project_id,
        "title": (title or template["name"]).strip() or template["name"],
        "student_level": student_level or template["level"],
        "goal": template["goal"],
        "outcomes": list(template["outcomes"]),
        "requirements": list(template["requirements"]),
        "blocks": list(template["blocks"]),
        "bom": list(template["bom"]),
        "workflow": list(template["workflow"]),
        "tests": list(template["tests"]),
        "rubric": dict(template["rubric"]),
        "calculations": calculations,
        "safety": template["safety"],
    }


def build_project_report(pack: dict[str, Any]) -> str:
    lines = ["# CircuitLab Academy — Engineering project pack", "",
             f"## {pack['title']}", "",
             f"- Project category: {pack['project_id']}",
             f"- Student level: {pack['student_level']}", "",
             "## Project goal", pack["goal"], "",
             "## Learning outcomes"]
    lines.extend(f"- {item}" for item in pack["outcomes"])
    lines.extend(["", "## Functional requirements"])
    lines.extend(f"- [ ] {item}" for item in pack["requirements"])
    lines.extend(["", "## System architecture"])
    lines.extend(f"{i}. {item}" for i, item in enumerate(pack["blocks"], 1))
    lines.extend(["", "## Preliminary bill of materials", "",
                  "| Ref | Component | Selection guidance |", "|---|---|---|"])
    lines.extend(f"| {ref} | {part} | {guidance} |" for ref, part, guidance in pack["bom"])
    lines.extend(["", "## First-pass calculations"])
    lines.extend(f"- {key.replace('_', ' ').title()}: {value:.6g}" if isinstance(value, (int, float)) else f"- {key}: {value}"
                 for key, value in pack["calculations"].items())
    lines.extend(["", "## Design and build workflow"])
    lines.extend(f"{i}. {item}" for i, item in enumerate(pack["workflow"], 1))
    lines.extend(["", "## Verification and test plan"])
    lines.extend(f"- [ ] {item}" for item in pack["tests"])
    lines.extend(["", "## Assessment rubric", "",
                  "| Criterion | Weight (%) |", "|---|---:|"])
    lines.extend(f"| {criterion} | {weight} |" for criterion, weight in pack["rubric"].items())
    lines.extend(["| **Total** | **100** |", "", "## Safety and limitations", pack["safety"],
                  "", "This pack is an educational starting point, not a complete construction-ready design. Verify calculations independently, use exact component datasheets, document assumptions, and obtain instructor approval before physical construction.", "",
                  "## Student reflection", "- What design trade-off did you make?",
                  "- Which result differed most between calculation, simulation and measurement?",
                  "- What evidence supports your final design decision?", ""])
    return "\n".join(lines)


def render_project_factory() -> None:
    import streamlit as st

    st.markdown("### Engineering Project Factory · Release 3.8")
    st.caption("Turn a project idea into a structured engineering brief, preliminary calculations, component plan, test strategy and assessment rubric.")
    ids = list(PROJECTS)
    labels = {key: value["name"] for key, value in PROJECTS.items()}
    selected = st.selectbox("Choose an engineering project", ids,
                            format_func=lambda key: labels[key], key="r38_project")
    template = PROJECTS[selected]
    p1, p2 = st.columns([2, 1])
    custom_title = p1.text_input("Project title", value=template["name"], key="r38_custom_title")
    level = p2.selectbox("Student level", ["Beginner", "Intermediate", "Advanced"],
                         index=1 if "Intermediate" in template["level"] else 0,
                         key="r38_student_level")
    st.markdown(f"**Suggested level:** {template['level']}")
    st.write(template["goal"])
    with st.expander("Project-specific inputs and first-pass calculations", expanded=True):
        values: dict[str, Any] = {}
        if selected == "regulated_supply":
            a, b, c = st.columns(3)
            values["output_v"] = a.number_input("Target output (V)", min_value=0.1, value=5.0, key="r38_ps_v")
            values["load_current_ma"] = b.number_input("Maximum load current (mA)", min_value=1.0, value=100.0, key="r38_ps_i")
            values["ripple_target_v"] = c.number_input("Ripple target (V p-p)", min_value=0.01, value=1.0, key="r38_ps_r")
            st.info("For detailed rectifier, reservoir capacitor, transformer and regulator estimates, continue in the Release 3.5 Power Supply Studio above.")
        elif selected == "ldr_light":
            a, b, c, d = st.columns(4)
            values["supply_v"] = a.number_input("Supply (V)", min_value=0.1, value=5.0, key="r38_ldr_v")
            values["ldr_bright_ohm"] = b.number_input("LDR bright (Ω)", min_value=1.0, value=1000.0, key="r38_ldr_b")
            values["ldr_dark_ohm"] = c.number_input("LDR dark (Ω)", min_value=1.0, value=100000.0, key="r38_ldr_d")
            values["fixed_ohm"] = d.number_input("Fixed resistor (Ω)", min_value=1.0, value=10000.0, key="r38_ldr_r")
            st.caption("Assumption: LDR is the upper divider leg and the fixed resistor is the lower leg.")
        elif selected == "rc_delay":
            a, b, c = st.columns(3)
            values["resistance_ohm"] = a.number_input("Resistance (Ω)", min_value=1.0, value=100000.0, key="r38_rc_r")
            values["capacitance_uf"] = b.number_input("Capacitance (µF)", min_value=0.01, value=100.0, key="r38_rc_c")
            values["supply_v"] = c.number_input("Supply (V)", min_value=0.1, value=5.0, key="r38_rc_v")
            values["threshold_fraction"] = st.slider("Switching threshold (% of final voltage)", 1, 99, 63, key="r38_rc_threshold") / 100.0
        elif selected == "led_driver":
            a, b, c = st.columns(3)
            values["supply_v"] = a.number_input("Supply (V)", min_value=0.1, value=5.0, key="r38_led_v")
            values["led_vf"] = b.number_input("LED forward voltage (V)", min_value=0.1, value=2.0, key="r38_led_vf")
            values["target_ma"] = c.number_input("Target current (mA)", min_value=0.1, value=10.0, key="r38_led_i")
        elif selected == "motor_pwm":
            a, b, c = st.columns(3)
            values["supply_v"] = a.number_input("Motor supply (V)", min_value=0.1, value=12.0, key="r38_motor_v")
            values["duty_percent"] = b.slider("PWM duty cycle (%)", 0, 100, 50, key="r38_motor_duty")
            values["motor_current_a"] = c.number_input("Assumed motor current (A)", min_value=0.01, value=0.5, key="r38_motor_i")
        else:
            a, b, c = st.columns(3)
            values["ra_ohm"] = a.number_input("RA (Ω)", min_value=1.0, value=10000.0, key="r38_555_ra")
            values["rb_ohm"] = b.number_input("RB (Ω)", min_value=1.0, value=47000.0, key="r38_555_rb")
            values["capacitance_nf"] = c.number_input("Timing capacitor (nF)", min_value=0.01, value=10.0, key="r38_555_c")
        st.caption("All outputs are first-pass educational calculations. Actual component behaviour, tolerances, switching losses and parasitics may change results.")
    try:
        pack = build_project_pack(selected, values, custom_title, level)
    except ValueError as exc:
        st.error(str(exc))
        return
    st.divider()
    st.markdown("#### Preliminary calculation results")
    cols = st.columns(min(4, max(1, len(pack["calculations"]))))
    for index, (name, value) in enumerate(pack["calculations"].items()):
        label = name.replace("_", " ").title()
        shown = f"{value:.4g}" if isinstance(value, (int, float)) else str(value)
        cols[index % len(cols)].metric(label, shown)
    st.divider()
    left, right = st.columns(2)
    with left:
        st.markdown("#### Learning outcomes")
        for item in pack["outcomes"]:
            st.markdown(f"- {item}")
        st.markdown("#### Functional requirements")
        for item in pack["requirements"]:
            st.markdown(f"- {item}")
        st.markdown("#### System architecture")
        for index, item in enumerate(pack["blocks"], 1):
            st.markdown(f"{index}. {item}")
    with right:
        st.markdown("#### Preliminary bill of materials")
        st.dataframe(pd.DataFrame(pack["bom"], columns=["Reference", "Component", "Selection guidance"]),
                     use_container_width=True, hide_index=True)
        st.markdown("#### Assessment rubric")
        st.dataframe(pd.DataFrame([{"Criterion": key, "Weight (%)": value}
                                   for key, value in pack["rubric"].items()]),
                     use_container_width=True, hide_index=True)
    st.markdown("#### Design and build workflow")
    for index, item in enumerate(pack["workflow"], 1):
        st.markdown(f"{index}. {item}")
    st.markdown("#### Verification and test plan")
    for item in pack["tests"]:
        st.markdown(f"- {item}")
    st.warning(pack["safety"])
    st.download_button("Download complete engineering project pack",
                       build_project_report(pack),
                       file_name=f"circuitlab_{selected}_project_pack.md",
                       mime="text/markdown", type="primary")
