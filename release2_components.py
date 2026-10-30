"""Curated educational component reference for CircuitLab Academy Release 2.5.

The catalogue deliberately avoids universal numeric ratings and fixed pinouts:
those depend on the exact manufacturer part, package and operating conditions.
"""


COMPONENTS = [
    {
        "id": "resistor", "name": "Fixed resistor", "family": "Passive components",
        "description": "A two-terminal component that opposes current and develops a voltage drop.",
        "principle": "Ohm's law: V = I × R. Dissipation: P = I²R = V²/R.",
        "uses": ["Current limiting", "Voltage division", "Bias networks", "Pull-up and pull-down networks"],
        "selection": ["Resistance value and tolerance", "Continuous power rating with thermal derating", "Maximum working voltage", "Temperature coefficient and pulse rating where relevant", "Package size and mounting method"],
        "failure_modes": ["Open circuit after overload or mechanical damage", "Resistance drift from heat or ageing", "Cracking or intermittent connection"],
        "verification": ["Measure resistance with power isolated and at least one terminal disconnected when parallel paths could affect the reading.", "Calculate worst-case dissipation and compare it with the exact datasheet rating.", "Inspect for discoloration, cracking or damaged terminations."],
        "pinout": "Usually non-polarized; verify the resistor technology and physical markings."
    },
    {
        "id": "electrolytic-capacitor", "name": "Aluminium electrolytic capacitor", "family": "Passive components",
        "description": "A polarized capacitor commonly used for bulk energy storage, smoothing and low-frequency coupling.",
        "principle": "i = C × dv/dt; stored energy E = ½CV².",
        "uses": ["Power-supply smoothing", "Bulk decoupling", "Low-frequency coupling"],
        "selection": ["Capacitance and tolerance", "Rated voltage with suitable margin", "Ripple-current rating", "ESR and impedance versus frequency", "Temperature rating, lifetime and polarity"],
        "failure_modes": ["Capacitance loss and ESR increase", "Leakage-current increase", "Vent opening or bulging after stress", "Reverse-polarity damage"],
        "verification": ["Isolate and safely discharge the capacitor before handling.", "Check polarity and voltage stress.", "Measure capacitance and ESR with suitable equipment; an in-circuit reading may be misleading."],
        "pinout": "Polarized. Identify positive and negative terminals from the exact part marking and datasheet; never infer polarity from lead length alone on an unknown part."
    },
    {
        "id": "ceramic-capacitor", "name": "Ceramic capacitor", "family": "Passive components",
        "description": "A non-polarized capacitor used widely for high-frequency bypassing, filtering and timing.",
        "principle": "Capacitive reactance Xc = 1/(2πfC); effective capacitance can depend on dielectric, DC bias, temperature and frequency.",
        "uses": ["Local supply decoupling", "High-frequency filtering", "Resonant and timing networks"],
        "selection": ["Capacitance and dielectric class", "Rated voltage and DC-bias derating", "Temperature coefficient", "Tolerance, package and frequency behaviour"],
        "failure_modes": ["Cracking from board flex or thermal stress", "Short circuit or capacitance shift", "Reduced effective capacitance under DC bias for some dielectric classes"],
        "verification": ["Inspect for cracks and board-flex damage.", "Check the exact dielectric and DC-bias curves in the datasheet.", "Measure out of circuit if accurate capacitance is required."],
        "pinout": "Normally non-polarized; package and dielectric markings vary."
    },
    {
        "id": "diode", "name": "Rectifier / signal diode", "family": "Semiconductors",
        "description": "A two-terminal semiconductor that conducts preferentially in one direction when forward biased.",
        "principle": "Check forward voltage, reverse leakage and reverse breakdown limits using the manufacturer's specified test conditions.",
        "uses": ["Rectification", "Reverse-polarity protection", "Clamping", "Signal steering"],
        "selection": ["Average and peak forward current", "Repetitive peak reverse voltage", "Surge current", "Forward voltage and reverse recovery", "Thermal resistance and package"],
        "failure_modes": ["Short circuit", "Open circuit", "Increased leakage", "Thermal damage from excess current or poor heat removal"],
        "verification": ["Confirm anode and cathode orientation from the exact part marking and datasheet.", "Use diode-test mode with power isolated.", "Check reverse-voltage and current stress in the actual circuit."],
        "pinout": "Polarized. The cathode band is common on many axial parts but package conventions differ; verify the part."
    },
    {
        "id": "led", "name": "Light-emitting diode (LED)", "family": "Optoelectronics",
        "description": "A diode that emits light under forward current; it requires current limiting or a suitable constant-current driver.",
        "principle": "Approximate series resistor: R = (Vsupply − Vf)/If, where Vf and If must come from the LED datasheet and design conditions.",
        "uses": ["Indicators", "Optical signalling", "Lighting modules"],
        "selection": ["Colour/wavelength and luminous intensity", "Forward current and forward-voltage range", "Reverse-voltage limit", "Viewing angle, thermal limits and optical requirements"],
        "failure_modes": ["Open circuit", "Reduced light output", "Colour shift", "Thermal degradation or bond-wire failure"],
        "verification": ["Check polarity and current-limiting design.", "Measure current rather than relying only on brightness.", "Compare junction-temperature and drive conditions with the datasheet."],
        "pinout": "Polarized. Do not rely solely on lead length or package shape for an unknown LED."
    },
    {
        "id": "bjt", "name": "Bipolar junction transistor (BJT)", "family": "Semiconductors",
        "description": "A three-terminal current-controlled semiconductor device available as NPN or PNP.",
        "principle": "Collector current depends on base drive and operating region; forced beta is a design choice for switching, not a guaranteed constant gain.",
        "uses": ["Low-side/high-side switching where appropriate", "Small-signal amplification", "Bias and driver stages"],
        "selection": ["NPN/PNP type and pin configuration", "Collector-emitter voltage and current limits", "Power dissipation and safe operating area", "Gain range at relevant current", "Saturation voltage, switching speed and thermal resistance"],
        "failure_modes": ["Collector-emitter short", "Open junction or bond wire", "Excess leakage", "Gain degradation after electrical or thermal overstress"],
        "verification": ["Identify base, collector and emitter from the exact datasheet.", "Check bias conditions and base-current limiting.", "Use a transistor tester or controlled diode-junction checks with the device isolated."],
        "pinout": "Pin order is not universal, even among similar packages. Confirm the exact manufacturer part and package drawing."
    },
    {
        "id": "mosfet", "name": "Power MOSFET", "family": "Semiconductors",
        "description": "A voltage-controlled field-effect transistor used for switching and power conversion.",
        "principle": "Conduction loss is approximately I² × RDS(on) under specified gate-drive and temperature conditions; switching losses also matter.",
        "uses": ["DC switching", "Motor and solenoid drivers", "Buck/boost converters", "Power stages"],
        "selection": ["N-channel/P-channel and enhancement/depletion type", "VDS, ID and safe operating area", "RDS(on) at the actual gate voltage and temperature", "Gate charge and drive requirements", "Thermal resistance, avalanche and body-diode behaviour"],
        "failure_modes": ["Drain-source short", "Gate oxide damage", "Excessive heating", "Avalanche or switching-stress damage"],
        "verification": ["Confirm gate, drain and source from the exact package datasheet.", "Check whether the gate driver reaches the required voltage under load.", "Inspect switching waveform, current, dissipation and thermal path."],
        "pinout": "Package pinouts vary. The metal tab may be electrically connected to a terminal; verify before mounting."
    },
    {
        "id": "op-amp", "name": "Operational amplifier", "family": "Integrated circuits",
        "description": "A high-gain differential amplifier used with feedback to implement amplification, filtering and signal conditioning.",
        "principle": "Closed-loop behaviour depends on feedback, gain-bandwidth, input common-mode range, output swing and stability.",
        "uses": ["Inverting/non-inverting amplifiers", "Active filters", "Buffers", "Sensor signal conditioning"],
        "selection": ["Supply voltage and single/dual-supply suitability", "Input common-mode range and offset", "Output swing and load drive", "Gain-bandwidth and slew rate", "Input/output noise, bias current and stability"],
        "failure_modes": ["Output saturation due to invalid input/common-mode conditions", "Oscillation from poor layout or capacitive loading", "Damage from overvoltage or output short", "Unexpected behaviour from incorrect supply pins"],
        "verification": ["Check supply pins and decoupling first.", "Confirm input common-mode and output-swing limits.", "Review feedback polarity, gain, load and stability guidance."],
        "pinout": "Pin functions and package orientation are part-specific; use the exact datasheet pin configuration."
    },
    {
        "id": "linear-regulator", "name": "Linear voltage regulator", "family": "Power management",
        "description": "A power-management IC that regulates an output voltage by dissipating excess input power as heat.",
        "principle": "Approximate dissipation: P = (Vin − Vout) × Iout; dropout and thermal limits constrain operation.",
        "uses": ["Low-noise rails", "Local regulated supplies", "Post-regulation"],
        "selection": ["Input/output voltage range and dropout", "Output current and current limit", "Power dissipation and thermal resistance", "Stability/capacitor ESR requirements", "Protection features and quiescent current"],
        "failure_modes": ["Thermal shutdown", "Output collapse from dropout/current limit", "Oscillation from unsuitable capacitors", "Permanent damage from excess input or reverse current"],
        "verification": ["Check input headroom under load.", "Calculate worst-case dissipation and junction temperature.", "Use the exact recommended input/output capacitors and layout."],
        "pinout": "Input, ground and output order varies by device and package; verify the datasheet."
    },
    {
        "id": "inductor", "name": "Inductor", "family": "Magnetics",
        "description": "A magnetic energy-storage component that opposes changes in current.",
        "principle": "v = L × di/dt; stored energy E = ½LI². Core saturation reduces effective inductance.",
        "uses": ["Switch-mode converters", "Filters", "Chokes", "Resonant circuits"],
        "selection": ["Inductance and tolerance", "Saturation current and RMS current", "DCR and copper loss", "Core loss versus frequency", "Shielding, temperature rise and footprint"],
        "failure_modes": ["Winding open circuit", "Insulation breakdown", "Core saturation and overheating", "Mechanical noise or damaged terminations"],
        "verification": ["Check inductance and DCR with suitable instruments.", "Check peak current against saturation rating.", "Inspect temperature rise and switching waveform."],
        "pinout": "Usually non-polarized as a passive two-terminal component; coupled windings and marked polarity dots require correct phasing."
    },
    {
        "id": "fuse", "name": "Fuse", "family": "Protection",
        "description": "An overcurrent protection device designed to interrupt a circuit under specified fault conditions.",
        "principle": "A fuse's time-current curve and I²t behaviour determine interruption under defined conditions.",
        "uses": ["Overcurrent protection", "Equipment input protection", "Branch protection"],
        "selection": ["Rated current and voltage", "AC/DC interrupting or breaking capacity", "Time-current characteristic", "I²t and inrush compatibility", "Environmental and approval requirements"],
        "failure_modes": ["Open after a fault or overload", "Incorrect nuisance operation", "Unsafe failure if interrupting rating is inadequate"],
        "verification": ["Replace only after identifying the cause of operation.", "Use the specified type, voltage and interrupting rating.", "Never bridge or uprate a fuse to suppress repeated operation."],
        "pinout": "Usually non-polarized. Holder, fuse type and certified rating must match the equipment design."
    },
    {
        "id": "potentiometer", "name": "Potentiometer", "family": "Passive components",
        "description": "A three-terminal variable resistor with two end terminals and a movable wiper.",
        "principle": "The wiper divides the total resistance; output depends on loading and taper.",
        "uses": ["Adjustable voltage dividers", "User controls", "Calibration and set-point adjustment"],
        "selection": ["Total resistance and tolerance", "Linear/logarithmic taper", "Power and maximum working voltage", "Wiper current, life and mechanical format"],
        "failure_modes": ["Intermittent wiper contact", "Track wear", "Open wiper", "Noise or resistance drift"],
        "verification": ["Identify both track ends and the wiper using the datasheet or resistance measurements.", "Check smooth resistance change through travel.", "Account for wiper current and output loading."],
        "pinout": "Three-terminal arrangement is not standardized by physical orientation; identify terminals electrically."
    },
    {
        "id": "relay", "name": "Electromechanical relay", "family": "Switching and control",
        "description": "An electrically operated switch that uses a coil to actuate one or more contacts.",
        "principle": "Coil energization moves contacts; coil and contact ratings are separate specifications.",
        "uses": ["Control isolation", "Load switching", "Interfacing low-power control with separate circuits"],
        "selection": ["Coil voltage, resistance/current and power", "Contact form and pole count", "AC/DC contact voltage and current ratings", "Inrush, motor/lamp load and electrical life", "Insulation, creepage/clearance and suppression"],
        "failure_modes": ["Coil open circuit", "Contacts welded or high resistance", "Mechanical wear", "Chatter from inadequate coil voltage"],
        "verification": ["Check coil voltage at the relay terminals.", "Confirm contact numbering from the exact datasheet.", "Use suitable coil suppression and verify contact ratings for the actual load."],
        "pinout": "Coil and contact terminal numbering is device-specific. Never assume pin positions from a generic relay drawing."
    },
]


def get_component(component_id):
    for item in COMPONENTS:
        if item["id"] == component_id:
            return item
    raise KeyError(f"Unknown component id: {component_id}")


def search_components(query="", family="All"):
    terms = [part for part in str(query or "").lower().split() if part]
    matches = []
    for item in COMPONENTS:
        if family != "All" and item["family"] != family:
            continue
        haystack = " ".join([
            item["name"], item["family"], item["description"], item["principle"],
            " ".join(item["uses"]), " ".join(item["selection"]), " ".join(item["failure_modes"]),
        ]).lower()
        if all(term in haystack for term in terms):
            matches.append(item)
    return matches


def selection_checklist(component_id):
    item = get_component(component_id)
    return [
        "Confirm the circuit function and operating conditions.",
        *[f"Check: {criterion}." for criterion in item["selection"]],
        "Verify every limit and pin assignment against the exact manufacturer's datasheet and package revision.",
        "Check worst-case voltage, current, power and temperature, including tolerances and transients.",
    ]


def catalogue_summary():
    return "\n".join(
        f'- {item["name"]} ({item["family"]}): {item["description"]}'
        for item in COMPONENTS
    )
