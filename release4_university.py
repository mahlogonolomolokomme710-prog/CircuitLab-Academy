"""Release 4.0 — Electronics University: structured lessons and component reference."""
from __future__ import annotations

from typing import Any

LESSONS: dict[str, dict[str, Any]] = {
"dc_fundamentals": {
"title":"DC circuit fundamentals","stage":"Foundation","summary":"Charge, voltage, current, resistance, power and measurement.",
"outcomes":["Distinguish voltage, current and resistance.","Apply Ohm's law with SI units.","Calculate power and energy.","Select correct meter connections."],
"content":[
("Voltage","Voltage is electrical potential-energy difference per unit charge, measured in volts (V). A voltmeter measures the difference between two points and is connected in parallel."),
("Current","Current is the rate of charge flow: I = dQ/dt, measured in amperes (A). An ammeter is inserted in series. Conventional current direction is opposite to electron drift in a metal."),
("Resistance and Ohm's law","For an ohmic resistor under approximately constant conditions, V = IR. This linear model does not describe every component; diodes and many semiconductor devices are nonlinear."),
("Power and energy","For a resistor, P = VI = I²R = V²/R. Energy is E = Pt for constant power. Check component power and voltage ratings, tolerance and operating conditions."),
("Measurement","A voltmeter is connected in parallel; a current meter is inserted in series. Never place a current meter directly across a voltage source.")],
"equations":["V = IR","I = Q/t (constant current)","P = VI = I²R = V²/R","E = Pt"],
"example":"A 1 kΩ resistor across 5 V draws I = 5/1000 = 5 mA. Its dissipation is P = 5 × 0.005 = 25 mW. Select a practical resistor using its rating and operating conditions.",
"activity":"Predict current and power for 2.2 kΩ at 9 V, then compare with the Ohm's-law CircuitJS exercise.",
"misconceptions":["Voltage is not consumed; energy is transferred.","Current is not consumed by a series resistor.","Ohm's law is not a universal linear law for all devices."],
"questions":[
{"q":"A 2 kΩ resistor is connected to 10 V. What current flows?","options":["5 mA","20 mA","0.2 mA","5 A"],"answer":0,"why":"I = V/R = 10/2000 = 5 mA."},
{"q":"How should a voltmeter measure voltage across a resistor?","options":["In series","In parallel","Across the supply only","With terminals shorted"],"answer":1,"why":"A voltmeter measures potential difference between two points and is connected in parallel."}]},
"network_analysis":{
"title":"Series, parallel and network analysis","stage":"Foundation → intermediate","summary":"Equivalent resistance, Kirchhoff's laws and voltage division.",
"outcomes":["Reduce series and parallel resistor networks.","Apply KCL and KVL.","Use voltage-divider equations.","Recognise loading effects."],
"content":[
("Series networks","Series components share the same branch current. For ideal resistors, Req = R1 + R2 + … ."),
("Parallel networks","Parallel components share the same two nodes and voltage. 1/Req = Σ(1/Ri); for two resistors Req = R1R2/(R1+R2)."),
("Kirchhoff's current law","KCL follows conservation of charge: the algebraic sum of currents at a node is zero."),
("Kirchhoff's voltage law","KVL follows conservation of energy in a lumped circuit: the algebraic sum of voltage rises and drops around a closed loop is zero."),
("Voltage divider","For two series resistors, unloaded Vout across R2 = Vin × R2/(R1+R2). A load across R2 changes the effective lower-leg resistance and the output.")],
"equations":["Rseries = R1 + R2 + …","1/Rparallel = 1/R1 + 1/R2 + …","ΣI at a node = 0","ΣV around a closed loop = 0","Vout = Vin × R2/(R1+R2) (unloaded)"],
"example":"A 12 V source feeds 2 kΩ and 4 kΩ in series. Total resistance is 6 kΩ, current is 2 mA and voltage across 4 kΩ is 8 V.",
"activity":"Build a 2 kΩ / 4 kΩ divider, calculate node voltages, solve it, then add a load across the output and explain the change.",
"misconceptions":["Parallel components share both connection nodes.","KCL is a node law; KVL is a loop law.","A loaded divider differs from the unloaded calculation."],
"questions":[
{"q":"Two 1 kΩ resistors in parallel have what equivalent resistance?","options":["2 kΩ","1 kΩ","500 Ω","100 Ω"],"answer":2,"why":"Two equal resistors in parallel have half the resistance."},
{"q":"Which law expresses conservation of charge at a node?","options":["KVL","KCL","Ohm's law","Faraday's law"],"answer":1,"why":"KCL states the algebraic current sum at a node is zero."}]},
"capacitors_transients":{
"title":"Capacitors, inductors and transient response","stage":"Intermediate","summary":"Energy storage, RC/RL time constants and first-order responses.",
"outcomes":["Explain capacitor and inductor energy storage.","Calculate RC and RL time constants.","Interpret charging/discharging curves.","Apply initial and final conditions."],
"content":[
("Capacitors","A capacitor stores energy in an electric field. i = C dv/dt and E = ½CV². Ideal capacitor voltage cannot change instantaneously under finite current. Real devices have ESR, leakage and voltage/temperature limits."),
("Inductors","An inductor stores magnetic energy. v = L di/dt and E = ½LI². Ideal inductor current cannot change instantaneously under finite voltage. Real devices have winding resistance and saturation limits."),
("RC response","For a first-order RC circuit τ = RC. Charging from zero toward Vs: vC(t)=Vs(1−e^(−t/RC)); discharge from V0: vC(t)=V0e^(−t/RC). At one τ, charging reaches about 63.2% and discharging falls to about 36.8%."),
("RL response","For a first-order series RL circuit τ = L/R. A zero-initial-current step response approaches Vs/R exponentially."),
("Settling","A simple first-order response is close to final value after about five time constants. This is an approximation; tolerances and non-ideal effects matter.")],
"equations":["iC = C dvC/dt","vL = L diL/dt","EC = ½CV²","EL = ½LI²","τRC = RC","τRL = L/R"],
"example":"For 10 kΩ and 100 µF, τ = 10,000 × 0.0001 = 1 s. After 1 s, ideal charging toward 5 V reaches about 3.16 V.",
"activity":"Use the Dynamic Circuit Laboratory. Measure the cursor voltage at t=τ, then double C and compare the response.",
"misconceptions":["Capacitor voltage and inductor current are continuous in ideal finite-energy switching.","One time constant is not full charge.","Five time constants is an approximation for a first-order response."],
"questions":[
{"q":"What is τ for 4.7 kΩ and 100 µF?","options":["0.047 s","0.47 s","4.7 s","47 s"],"answer":1,"why":"τ = 4700 × 0.0001 = 0.47 s."},
{"q":"Which quantity is continuous for an ideal inductor at a switching instant?","options":["Voltage","Current","Resistance","Frequency"],"answer":1,"why":"An instantaneous current change would require unbounded voltage in the ideal model."}]},
"semiconductors":{
"title":"Semiconductor fundamentals and diodes","stage":"Intermediate","summary":"PN junctions, diode I–V behaviour, LEDs and rectification.",
"outcomes":["Describe forward and reverse bias.","Interpret diode I–V behaviour.","Calculate a first-pass LED resistor.","Explain half-wave and bridge rectification."],
"content":[
("PN junction","A PN junction forms where p-type and n-type regions meet. Diffusion and recombination create a depletion region and built-in field. Forward bias reduces the barrier; reverse bias normally leaves small leakage until breakdown."),
("Diode I–V model","The Shockley model is I = IS(exp(V/(nVT))−1), where IS is saturation current, n ideality factor and VT=kT/q. Real devices also have series resistance, breakdown, capacitance and thermal effects."),
("LED current limiting","For a simple supply and series resistor, R ≈ (Vs−Vf)/If. Choose a standard value at or above the nominal minimum, then check worst-case supply, Vf, tolerance and resistor power."),
("Rectification","A half-wave rectifier uses one diode. A full-wave bridge uses four diodes, with two normally conducting in each half-cycle; load current retains one direction."),
("Filtering","A reservoir capacitor supplies load current between rectified peaks. A first-pass estimate is ΔV≈Iload/(fripple C), where fripple is f for half-wave and 2f for full-wave.")],
"equations":["I = IS(exp(V/(nVT))−1)","VT = kT/q","RLED ≈ (Vs−Vf)/If","PR = I²R","ΔV ≈ Iload/(fripple C)"],
"example":"For 9 V, Vf=2 V and If=10 mA, Rmin=(9−2)/0.01=700 Ω. Consider a next-higher standard value and verify actual current, power and worst-case conditions.",
"activity":"Use the Diode Characteristics and LED Resistor Design labs. Predict changes with temperature and supply voltage, and state model limitations.",
"misconceptions":["A diode is not always a fixed 0.7 V drop.","Two bridge diodes conduct in the usual bridge path.","A smoothing capacitor does not itself regulate output voltage."],
"questions":[
{"q":"How many bridge diodes normally conduct in each half-cycle?","options":["One","Two","Three","Four"],"answer":1,"why":"Two diodes conduct in each half-cycle."},
{"q":"Full-wave rectification of 50 Hz gives what ideal ripple frequency?","options":["25 Hz","50 Hz","100 Hz","200 Hz"],"answer":2,"why":"Two output pulses per input cycle gives 100 Hz."}]},
"power_electronics":{
"title":"Power supplies and linear regulation","stage":"Intermediate → advanced","summary":"Rectifier, reservoir, regulator, headroom and thermal design.",
"outcomes":["Trace the functional stages of a linear supply.","Estimate peak voltage and ripple.","Assess regulator headroom.","Identify thermal and component-rating constraints."],
"content":[
("Functional stages","A basic linear supply may use an isolated low-voltage AC source, rectifier, reservoir capacitor, linear regulator and load. Each stage performs a distinct function."),
("Rectified peak","For a sinusoidal secondary, ideal peak is Vrms√2. Subtract approximately two conducting diode drops for a bridge first-pass estimate. Transformer regulation and impedance reduce loaded peak."),
("Reservoir ripple","For approximately constant load current, ΔV≈I/(fripple C). Assess regulator input at the estimated valley, not only the peak."),
("Regulator headroom","The regulator input must remain above output by the required dropout/headroom under relevant load and temperature conditions. Use the exact datasheet."),
("Thermal design","A linear regulator's first-pass dissipation is P≈(Vin−Vout)Iout. Junction temperature depends on ambient and the complete thermal path."),
("Design review","Consider low-line input, transformer regulation, ripple, capacitor voltage/ripple-current ratings, diode ratings, regulator dropout/thermal behaviour and qualified protection requirements.")],
"equations":["Vpeak ≈ √2 Vrms","Vvalley ≈ Vpeak − diode drops − ΔV","ΔV ≈ Iload/(fripple C)","Plinear ≈ (Vin−Vout)Iout","Tj ≈ Ta + P×θJA (simplified)"],
"example":"A full-wave 50 Hz supply has 100 Hz ripple. At 0.10 A with 2200 µF, ΔV≈0.10/(100×0.0022)=0.455 V peak-to-peak. Real ripple depends on impedance, ESR and charging pulses.",
"activity":"Use the Power Supply Studio to compare half-wave/full-wave ripple, regulator headroom and thermal estimates. List three omitted real-world effects.",
"misconceptions":["A regulator cannot maintain output if its input valley is below required headroom.","Check capacitor rating against maximum expected voltage.","A simplified thermal pass is not safety certification."],
"questions":[
{"q":"At 50 Hz, ideal full-wave ripple frequency is?","options":["50 Hz","100 Hz","150 Hz","300 Hz"],"answer":1,"why":"Full-wave rectification produces two peaks per input cycle."},
{"q":"Which input value matters for dropout at low line?","options":["Only unloaded peak","Minimum expected input valley","LED forward voltage","Transformer VA alone"],"answer":1,"why":"Headroom must be adequate at the lowest expected input under load."}]},
"transistors_amplifiers":{
"title":"Transistors and basic amplifiers","stage":"Intermediate → advanced","summary":"BJT, MOSFET, switching, bias and amplifier fundamentals.",
"outcomes":["Identify BJT terminals and operating regions.","Explain MOSFET gate control.","Distinguish switching and linear operation.","Recognise bias and thermal constraints."],
"content":[
("BJT","A BJT has emitter, base and collector. In a simplified forward-active model IC≈βIB, but β varies with device, current and temperature."),
("Operating regions","Cutoff is substantially off; forward-active is commonly used for amplification; saturation is commonly used for switching. Switching design must account for drive and losses."),
("MOSFET","Gate-source voltage controls channel conduction. RDS(on) is specified at particular gate drive and temperature. Threshold voltage does not mean the MOSFET is fully enhanced."),
("Amplifier bias","An amplifier is biased at a Q-point so a signal can vary without immediately driving the device into cutoff or saturation. Gain depends on topology, device, load and frequency."),
("Inductive loads","When a transistor switches off an inductive load, current needs a suitable path, such as a correctly selected flyback diode for an appropriate DC load.")],
"equations":["IC≈βIB (rough active-region model)","VGS=VG−VS","Av=Δvout/Δvin","P=VI"],
"example":"For a low-side MOSFET motor switch, verify RDS(on) at the available gate voltage, drain rating, current, thermal limits and inductive-current path. VGS(th) alone is not a gate-drive specification.",
"activity":"Compare BJT and logic-level MOSFET low-side switches. List control requirements, conduction losses, protection and datasheet parameters.",
"misconceptions":["MOSFET threshold is not the fully-on gate voltage.","BJT β is not fixed.","A transistor switch is not lossless."],
"questions":[
{"q":"What does MOSFET VGS(th) represent?","options":["Guaranteed fully-on voltage","Specified threshold condition at small drain current","Maximum drain current","Gate breakdown voltage"],"answer":1,"why":"Threshold is measured under specified low-current conditions."},
{"q":"Why may a motor need a flyback path?","options":["Increase resistance","Provide a path for inductive current at switch-off","Remove the supply","Convert DC to AC"],"answer":1,"why":"Inductor current cannot change instantaneously."}]},
"opamps":{
"title":"Operational amplifiers and analogue interfaces","stage":"Intermediate → advanced","summary":"Ideal assumptions, negative feedback, gain and real-device limits.",
"outcomes":["State ideal op-amp assumptions.","Explain negative feedback.","Calculate inverting and non-inverting gain.","Identify practical limitations."],
"content":[
("Ideal model","An ideal op-amp has infinite open-loop gain, infinite input impedance, zero output impedance and unlimited bandwidth. These are simplifying assumptions."),
("Negative feedback","With negative feedback and linear operation, the output reduces differential input voltage. In ideal analysis V+≈V− and input currents≈0. These assumptions fail in saturation or instability."),
("Inverting amplifier","For an ideal inverting amplifier Av=−Rf/Rin. The negative sign indicates inversion."),
("Non-inverting amplifier","For a standard non-inverting amplifier Av=1+Rf/Rg."),
("Real-device checks","Check supply range, input common-mode range, output swing, offset, bias current, slew rate, gain-bandwidth, output current and stability.")],
"equations":["Av(inverting)=−Rf/Rin","Av(non-inverting)=1+Rf/Rg","V+≈V− (linear negative feedback)","I+≈I−≈0 (ideal model)"],
"example":"With Rin=10 kΩ and Rf=100 kΩ, ideal inverting gain is −10. A 0.1 V input gives −1 V only if supply rails and device limits permit it.",
"activity":"Calculate gain for Rin=4.7 kΩ and Rf=47 kΩ. Identify supply and output-swing checks before assuming the output is achievable.",
"misconceptions":["A virtual short is not a physical short.","Output cannot exceed real device limits.","Infinite gain and bandwidth are ideal assumptions."],
"questions":[
{"q":"Ideal inverting gain with Rf=100 kΩ and Rin=10 kΩ?","options":["+10","−10","+0.1","−0.1"],"answer":1,"why":"Av=−Rf/Rin=−10."},
{"q":"When is V+≈V− useful?","options":["Power off","Negative feedback and linear operation","Output saturated","Every comparator"],"answer":1,"why":"Negative feedback in the linear region drives differential input close to zero."}]},
"digital_electronics":{
"title":"Digital electronics and logic systems","stage":"Foundation → intermediate","summary":"Binary, logic gates, Boolean algebra and sequential logic.",
"outcomes":["Convert binary and decimal values.","Construct logic truth tables.","Apply De Morgan's laws.","Distinguish combinational and sequential logic."],
"content":[
("Binary","Unsigned binary bits have powers-of-two weights. 1011₂ = 8+0+2+1 = 11₁₀."),
("Logic gates","AND is 1 only when all inputs are 1; OR is 1 when at least one input is 1; NOT inverts. NAND and NOR are functionally complete."),
("Truth tables","A truth table lists outputs for all input combinations. De Morgan: NOT(A AND B)=NOT A OR NOT B; NOT(A OR B)=NOT A AND NOT B."),
("Combinational logic","Output depends on present inputs after propagation delay. Examples include adders, multiplexers and decoders."),
("Sequential logic","Sequential circuits store state. Latches and flip-flops are storage elements; timing includes setup, hold and propagation delay.")],
"equations":["1011₂=11₁₀","AND: Y=A·B","OR: Y=A+B","NAND: Y=NOT(A·B)","NOT(A·B)=NOT A + NOT B"],
"example":"A two-input AND gate outputs 0 for 00, 01 and 10, and 1 only for 11. NAND gives the inverse output.",
"activity":"Write truth tables for AND, OR, NAND and XOR. Simplify a Boolean expression and verify all input combinations.",
"misconceptions":["Logic 0 and 1 are voltage ranges defined by a logic family.","Combinational logic does not intentionally store state.","Sequential logic requires state and timing analysis."],
"questions":[
{"q":"What is decimal 1010₂?","options":["8","10","12","14"],"answer":1,"why":"1010₂=8+0+2+0=10."},
{"q":"Which gate outputs 1 only when both inputs are 1?","options":["OR","XOR","AND","NOR"],"answer":2,"why":"AND is true only when every input is true."}]}
}

COMPONENTS: dict[str, dict[str,str]] = {
"Resistor":{"family":"Passive","function":"Limits current, develops voltage drops, sets bias and forms dividers.","principle":"V=IR; P=I²R=V²/R.","selection":"Resistance, tolerance, power, working voltage, temperature coefficient and pulse rating.","failure":"Overload can cause drift, cracking or open circuit.","verification":"Measure with power removed and isolate from parallel paths where needed.","caution":"Check both power and voltage ratings; resistance alone is insufficient."},
"Capacitor":{"family":"Passive","function":"Stores charge; used for filtering, coupling, decoupling and timing.","principle":"i=C dv/dt; E=½CV²; real parts have ESR and leakage.","selection":"Capacitance, tolerance, voltage, dielectric, polarity, ESR, ripple current and temperature.","failure":"Overvoltage, reverse polarity, heat or ripple can cause leakage, venting or failure.","verification":"Observe polarity; safely discharge; measure capacitance/ESR with suitable equipment.","caution":"Capacitors can retain charge after power removal; follow approved discharge procedures."},
"Inductor":{"family":"Passive","function":"Stores magnetic energy and opposes rapid current change.","principle":"v=L di/dt; E=½LI²; core saturation reduces inductance.","selection":"Inductance, saturation/RMS current, DCR, core loss, frequency and temperature.","failure":"Overcurrent can saturate or overheat winding/core.","verification":"Check inductance and DCR; verify saturation and thermal ratings.","caution":"Stored magnetic energy can create switching transients."},
"Diode":{"family":"Semiconductor","function":"Conducts preferentially in one direction; rectification and protection.","principle":"Nonlinear I–V curve; leakage and breakdown depend on device and temperature.","selection":"Forward current/drop, reverse voltage, surge current, recovery, capacitance and thermal limits.","failure":"Overcurrent, reverse overvoltage or heat can cause short/open failure.","verification":"Use diode-test mode with circuit de-energised; confirm polarity and datasheet.","caution":"Do not assume every diode has a 0.7 V drop."},
"LED":{"family":"Semiconductor","function":"Emits light when forward current flows.","principle":"Electroluminescence; Vf depends on material, current and temperature.","selection":"Current, Vf range, luminous intensity, wavelength, viewing angle and thermal path.","failure":"Excess current or temperature degrades output or damages junction.","verification":"Check polarity/datasheet; use current-limited supply or driver.","caution":"Do not connect directly across a voltage source without current control."},
"Zener diode":{"family":"Semiconductor","function":"Approximate voltage clamp/reference in specified reverse-breakdown region.","principle":"Reverse current rises around Zener voltage; dynamic resistance and power affect regulation.","selection":"Voltage, tolerance, test current, dynamic impedance, power and temperature coefficient.","failure":"Excess current/power overheats junction.","verification":"Use current-limited test arrangement at datasheet test current.","caution":"Requires current limiting; voltage is not maintained at arbitrary current."},
"BJT":{"family":"Semiconductor","function":"Amplifies or switches current using base-emitter drive.","principle":"In forward-active operation IC≈βIB; β varies substantially.","selection":"Polarity, VCEO, IC, power, gain, saturation voltage, SOA and thermal resistance.","failure":"Overvoltage, excess current, secondary breakdown or heat.","verification":"Confirm pinout and polarity; test under controlled conditions.","caution":"Do not size switching base drive from typical gain alone."},
"MOSFET":{"family":"Semiconductor","function":"Voltage-controlled switch used in power conversion and control.","principle":"VGS controls channel; conduction loss often estimated I²RDS(on).","selection":"VDS, ID, RDS(on) at actual gate voltage, gate charge, SOA and thermal data.","failure":"Gate overvoltage, drain overvoltage, avalanche or thermal stress.","verification":"Check datasheet conditions, gate drive, waveform and temperature.","caution":"VGS(th) is not a fully-on gate-drive specification."},
"Operational amplifier":{"family":"Analogue IC","function":"Amplifies differential input, usually with external feedback.","principle":"Negative feedback sets closed-loop behaviour; virtual-short assumptions apply in linear operation.","selection":"Supply, common-mode range, output swing, GBW, slew rate, offset, noise and output drive.","failure":"Overvoltage, common-mode violation, output overload or heat.","verification":"Check supply pins, datasheet, feedback stability and load.","caution":"Output cannot swing arbitrarily beyond supply rails."},
"555 timer":{"family":"Mixed-signal IC","function":"Generates timing pulses, oscillation and threshold control.","principle":"Comparators monitor supply fractions and control a latch/discharge transistor.","selection":"Supply, timing range, output current, frequency, type and pinout.","failure":"Supply/pin overvoltage, output overload or incorrect connections.","verification":"Check exact pinout and measure frequency/duty cycle.","caution":"Bipolar and CMOS variants differ in performance."},
"Transformer":{"family":"Magnetic component","function":"Transfers AC energy; can provide voltage conversion and galvanic isolation when designed for it.","principle":"Ideal ratio Vs/Vp≈Ns/Np; real parts have regulation and losses.","selection":"Primary/secondary ratings, frequency, VA, regulation, isolation and temperature.","failure":"Overload and overheating damage insulation.","verification":"Use certified equipment and approved inspection procedures.","caution":"Mains-side work is not a beginner activity; use certified isolated low-voltage supplies."},
"Voltage regulator":{"family":"Power IC","function":"Maintains output within specified input, load and thermal limits.","principle":"Linear loss ≈(Vin−Vout)I; switching regulators transfer energy through switched elements.","selection":"Input/output, current, dropout, efficiency, thermal data, capacitors and protection.","failure":"Insufficient headroom, excess dissipation, short circuit or unsuitable capacitors/layout.","verification":"Check exact datasheet application circuit, dropout and thermal data.","caution":"Nominal output setting does not prove regulation under low-line/load extremes."},
"Relay":{"family":"Electromechanical","function":"Coil-operated contacts switch a circuit.","principle":"Coil magnetic field actuates mechanical contacts.","selection":"Coil voltage/current, contact form, load category, isolation and switching life.","failure":"Contact wear/welding, coil heat or mechanical sticking.","verification":"Check coil resistance and contact continuity with power removed.","caution":"Contact ratings depend on load; mains switching requires qualified design."},
"Fuse":{"family":"Protection","function":"Interrupts excessive current to reduce fire/equipment damage risk.","principle":"Calibrated element melts under specified current/time conditions.","selection":"Current/voltage, breaking capacity, time-current curve and AC/DC use.","failure":"Opens under overload or fault; incorrect replacement defeats protection.","verification":"Check continuity after isolation and identify cause before replacement.","caution":"Never bypass a fuse or arbitrarily increase its rating."},
"Potentiometer":{"family":"Passive","function":"Adjustable resistance or voltage divider.","principle":"Wiper position changes resistance ratio; loading affects output.","selection":"Total resistance, taper, power, voltage, track and wiper current.","failure":"Track wear or contamination causes noise/intermittence.","verification":"Measure end-to-end and wiper resistance with circuit isolated.","caution":"Observe power and wiper-current limits."}
}


def get_lesson(lesson_id: str) -> dict[str, Any]:
    if lesson_id not in LESSONS:
        raise ValueError(f"Unknown lesson: {lesson_id}")
    return LESSONS[lesson_id]


def search_knowledge(query: str, scope: str = "All") -> list[dict[str,str]]:
    term = str(query or "").strip().lower()
    if not term:
        return []
    results=[]
    if scope in ("All","Lessons"):
        for key, lesson in LESSONS.items():
            blob=" ".join([lesson["title"],lesson["summary"],lesson["stage"],*lesson["outcomes"],*lesson["equations"],*(v for _,v in lesson["content"]),lesson["example"],lesson["activity"],*lesson["misconceptions"]]).lower()
            if term in blob:
                results.append({"kind":"Lesson","id":key,"title":lesson["title"],"summary":lesson["summary"]})
    if scope in ("All","Components"):
        for name,item in COMPONENTS.items():
            if term in " ".join([name,*item.values()]).lower():
                results.append({"kind":"Component","id":name,"title":name,"summary":item["function"]})
    return results


def build_lesson_markdown(lesson_id: str) -> str:
    lesson=get_lesson(lesson_id)
    lines=[f"# {lesson['title']}","",f"**Stage:** {lesson['stage']}","",lesson["summary"],"","## Learning outcomes"]
    lines += [f"- {x}" for x in lesson["outcomes"]]
    lines += ["","## Lesson"]
    for heading,body in lesson["content"]:
        lines += [f"### {heading}",body,""]
    lines += ["## Key equations",""]+[f"- {x}" for x in lesson["equations"]]
    lines += ["","## Worked example",lesson["example"],"","## Practical activity",lesson["activity"],"","## Common misconceptions"]
    lines += [f"- {x}" for x in lesson["misconceptions"]]
    lines += ["","## Knowledge check"]
    for i,q in enumerate(lesson["questions"],1):
        lines.append(f"{i}. {q['q']}")
        lines += [f"   - {letter}. {option}" for letter,option in zip("ABCD",q["options"])]
        lines.append(f"   - Answer: {chr(65+q['answer'])}. {q['why']}")
    return "\n".join(lines)+"\n"


def build_component_markdown(name: str) -> str:
    if name not in COMPONENTS:
        raise ValueError(f"Unknown component: {name}")
    item=COMPONENTS[name]
    labels=[("Category","family"),("Function","function"),("Operating principle","principle"),("Selection parameters","selection"),("Common failure modes","failure"),("Verification","verification"),("Caution","caution")]
    return "\n".join([f"# {name}",""]+[f"**{label}:** {item[key]}" for label,key in labels]+[""])


def render_university_hub() -> None:
    import streamlit as st
    import pandas as pd
    st.markdown("""
    <div style="padding:22px 26px;border-radius:18px;background:linear-gradient(115deg,#101d32,#145b69);color:#f3fbff;margin-bottom:16px">
      <div style="letter-spacing:.14em;font-size:.72rem;color:#69dfd0;font-weight:700">RELEASE 4.0 · ELECTRONICS UNIVERSITY</div>
      <h2 style="color:#f3fbff;margin:.35rem 0">Learn the principles. Master the components.</h2>
      <p style="color:#d3e5ee;margin:0">Structured lessons, worked examples, knowledge checks and a practical component reference.</p>
    </div>
    """,unsafe_allow_html=True)
    st.info("General educational foundation, not an official TUT curriculum map. Follow your current module guide and lecturer instructions.")
    lesson_tab,component_tab,search_tab=st.tabs(["Learning pathways","Component library","Knowledge search"])
    with lesson_tab:
        stages=["All stages","Foundation","Intermediate","Advanced"]
        stage=st.selectbox("Learning pathway",stages,key="r40_stage")
        available=[(k,v) for k,v in LESSONS.items() if stage=="All stages" or stage.lower() in v["stage"].lower()]
        ids=[k for k,_ in available]
        chosen=st.selectbox("Choose a lesson",ids,format_func=lambda k: next(v["title"] for x,v in available if x==k),key="r40_lesson")
        lesson=get_lesson(chosen)
        st.caption(lesson["summary"])
        left,right=st.columns([1.5,1])
        with left:
            st.markdown("#### Learning outcomes")
            for x in lesson["outcomes"]: st.write("• "+x)
            st.markdown("#### Lesson content")
            for heading,body in lesson["content"]:
                with st.expander(heading,expanded=False): st.write(body)
            st.markdown("#### Key equations")
            for eq in lesson["equations"]: st.code(eq)
            with st.expander("Worked example",expanded=True): st.write(lesson["example"])
            with st.expander("Practical activity"): st.write(lesson["activity"])
            with st.expander("Common misconceptions"):
                for x in lesson["misconceptions"]: st.write("• "+x)
        with right:
            st.markdown("#### Knowledge check")
            selected=[]
            for i,q in enumerate(lesson["questions"]):
                selected.append(st.radio(q["q"],q["options"],key=f"r40_{chosen}_q{i}"))
            if st.button("Mark knowledge check",key=f"r40_mark_{chosen}"):
                score=0
                for i,q in enumerate(lesson["questions"]):
                    ok=q["options"].index(selected[i])==q["answer"]
                    score+=int(ok)
                    (st.success if ok else st.error)(f"Question {i+1}: {'Correct.' if ok else 'Not quite.'} {q['why']}")
                st.metric("Knowledge check",f"{score}/{len(lesson['questions'])}")
                st.session_state["r40_last_quiz"]={"lesson":chosen,"score":score,"total":len(lesson["questions"])}
            st.download_button("Download lesson notes",build_lesson_markdown(chosen),file_name=f"circuitlab_{chosen}_notes.md",mime="text/markdown")
            last=st.session_state.get("r40_last_quiz")
            if last and last["lesson"]==chosen: st.caption(f"Latest session result: {last['score']}/{last['total']} (session only).")
    with component_tab:
        families=["All families"]+sorted({v["family"] for v in COMPONENTS.values()})
        family=st.selectbox("Component family",families,key="r40_family")
        names=[n for n,v in COMPONENTS.items() if family=="All families" or v["family"]==family]
        name=st.selectbox("Component",names,key="r40_component")
        item=COMPONENTS[name]
        st.subheader(name); st.caption(item["family"]); st.write(item["function"])
        for label,key in [("Operating principle","principle"),("Selection parameters","selection"),("Common failure modes","failure"),("How to verify","verification"),("Safety / design caution","caution")]:
            st.markdown(f"**{label}**"); st.write(item[key])
        st.download_button("Download component reference",build_component_markdown(name),file_name=f"circuitlab_{name.lower().replace(' ','_')}.md",mime="text/markdown")
    with search_tab:
        query=st.text_input("Search lessons and components",placeholder="Try ripple, MOSFET, time constant…")
        scope=st.selectbox("Search within",["All","Lessons","Components"])
        if query.strip():
            matches=search_knowledge(query,scope)
            st.write(f"{len(matches)} result(s)")
            if matches: st.dataframe(pd.DataFrame(matches),use_container_width=True,hide_index=True)
            else: st.info("No matching content found. Try a component name or lesson topic.")
    st.caption("Learning aid only. Verify equations, component ratings and practical procedures against textbooks, manufacturer datasheets, your current module guide and instructor direction. Physical experiments require approved, supervised, isolated low-voltage equipment.")
