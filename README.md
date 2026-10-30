# CircuitLab Academy v0.5 — Self-hosted simulator and prepared circuit library

## What's new
- Bundles the compiled CircuitJS1 browser assets in `static/circuitjs/` for self-hosted simulation.
- Adds prepared examples for Ohm's law, series resistors, parallel resistors, RC charging, and a diode half-wave rectifier.
- Loads prepared circuits into CircuitJS using the `cct` query parameter.
- Adds a Prepared Circuit Library workspace and downloadable student investigation notes.
- Enables Streamlit static-file serving through `.streamlit/config.toml`.

## Requirements
- Python and the project dependencies listed in `requirements.txt`.
- The compiled CircuitJS1 files included in this release under `static/circuitjs/`.

The release already includes the compiled browser assets. You do not need to run `install_circuitjs.py`.

## Windows setup
Open Command Prompt in the project folder:

```bat
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If you do not already have a `.venv` environment, create one first:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Verify the self-hosted simulator
Confirm these files exist:

```text
static\circuitjs\circuitjs.html
static\circuitjs\circuitjs1\circuitjs1.nocache.js
```

Open the app and check:
1. The home page loads.
2. The Simulator workspace opens and displays a circuit.
3. The RC charging circuit appears and can be edited.
4. The Prepared Circuit Library loads all five examples.
5. Switching between tabs does not produce errors.

The self-hosted simulator should open from the app's local static assets. If the app reports that it is using a hosted fallback instead, investigate before describing the release as self-hosted.

## Safe release workflow
Keep the existing deployed v0.4 version on `main` unchanged while preparing and testing v0.5 on a separate branch.

Check the current branch and working tree before committing:

```bat
git branch --show-current
git status -sb
git diff --cached --check
```

Stage the v0.5 files and commit on the release branch only after confirming the branch is `v0.5-self-hosted-simulator` and the local checks pass:

```bat
git add .gitignore README.md app.py requirements.txt CIRCUITJS1_ATTRIBUTION.md V0_5_TEST_CHECKLIST.md .streamlit prepared_circuits static/circuitjs
```

Do not run `git push origin main` as part of this release-preparation workflow. Review the staged changes and push the release branch only when ready for a separate deployment/review. Pushing to a branch does not by itself guarantee that a separate Streamlit Community Cloud app is configured; verify the deployment's repository and branch settings before deploying.

## Simulator licensing and safety
CircuitJS1 is distributed under GPL version 2 or later. Preserve upstream copyright and licence notices and comply with applicable source-distribution obligations. See `CIRCUITJS1_ATTRIBUTION.md` and the upstream repository: https://github.com/sharpie7/circuitjs1.

These prepared circuits are educational examples. Simulation models may idealize components; verify values and circuit operation. Never connect a beginner circuit directly to mains electricity.


## Release 1 — Engineering Interface (development branch)

Release 1 introduces a project-first Engineering Command Center while preserving the existing specialist workspaces and CircuitJS simulator.

### What's new
- New Engineering Command Center as the default home workspace.
- Project manager to create engineering projects with domain, level, objective and status.
- Project notes and selected-project JSON export.
- Project register and recent activity export.
- Central shortcuts to the existing simulator, prepared circuits, design bench, component library, fault detective, guided build and report builder.
- Existing specialist pages remain available; this release does not replace the current simulator implementation.

### Important limitations
- Project records are stored in Streamlit session state in Release 1. They are not yet account-based or persistent across sessions. Export the project register before closing the session.
- The new command center is an additive interface layer. It does not yet provide a drag-and-drop schematic editor, integrated AI copilot, or new simulation engine; those belong to later releases.
- The existing hosted CircuitJS integration is retained and must be regression-tested before any deployment.

### Safe development workflow
- Development branch: `release-1/engineering-interface`
- Stable baseline: `stable/working-deployment-2026-10-30`
- Do not merge this branch into `main` or change the live deployment until local and preview tests pass and the owner approves.


## Release 2 — AI Engineering Copilot (development branch)

Release 2 adds an AI-assisted engineering workspace while retaining all Release 1 and legacy workspaces.

### What's new
- AI Engineering Copilot for concept explanations, design reasoning, calculation checks, simulation interpretation and fault diagnosis.
- Student context fields for project, circuit description, level and task.
- Deterministic local calculators for Ohm's law, electrical power, voltage dividers, RC time constants and a first-pass full-wave smoothing-capacitor estimate.
- Explicit distinction between calculated information, user-supplied evidence and simulated/physical measurements.
- API credentials are read from Streamlit Secrets or an optional session-only password field. No key is stored in source code.

### AI configuration
Add these values to the separate Streamlit Release 2 test app's Secrets:

    OPENAI_API_KEY = "your-secret-key"
    OPENAI_MODEL = "gpt-4o-mini"

Optional compatible-provider overrides: OPENAI_BASE_URL and OPENAI_MODEL. Do not commit secrets to GitHub. AI service usage may incur separate API charges and requires an account with API access.

### Release 2.1 — Circuit-aware Copilot foundation

The Copilot now accepts an exported CircuitJS/Falstad text schematic (`.txt`) and performs a first-pass extraction of:
- Recognized component records and their raw parameter fields.
- Component terminal coordinates.
- Wire segments and inferred electrical nets from orthogonal wire geometry.
- A readable extraction summary that is included in the AI conversation context when the API is configured.

This is an initial circuit-awareness layer, not a full schematic interpreter or simulator. It does not inspect the live embedded canvas, guarantee that every CircuitJS element type is decoded, or provide measured voltages/currents. Connectivity inference is deliberately labelled as approximate and must be checked against CircuitJS. Crossings, special components, multi-terminal devices, switches, semiconductor pin semantics and uncommon element formats require further validation.

### Safe test for the schematic reader
1. Open the separate Release 2 test deployment.
2. In CircuitJS, open one of the prepared examples and export/save its circuit as a text `.txt` file.
3. Open AI Engineering Copilot and upload that file in Engineering context.
4. Check the component count, wire count, inferred net count and extracted component details.
5. Compare the extracted inventory and connections with the actual CircuitJS schematic.
6. Do not treat the extraction as simulation output. The local reader can be tested without an API key; an API key is needed for the AI to discuss the extracted context.

### Release 2.2 — Circuit Understanding

Release 2.2 adds a heuristic topology interpretation layer on top of the Release 2.1 CircuitJS text reader.

Recognized candidate patterns include:
- Resistor pairs sharing the same two inferred nets (possible parallel resistors).
- Resistors meeting at a node with no third resistor branch (possible series relationship in the resistor-only subgraph).
- A two-resistor voltage-divider candidate when the inferred graph also matches a voltage-source/ground path.
- Resistor-capacitor shared-node relationships (RC network candidate).
- Diode networks and possible bridge-rectifier candidates.
- LC networks and transistor-device presence, with explicit limitations.

The topology summary is displayed separately from the raw extraction and is also passed to the AI Copilot as context. The Copilot is instructed to describe these as candidates, explain the evidence and identify what must be verified. The analysis does not solve the circuit or provide simulation measurements.

### Release 2.2 regression tests

A small Python unittest suite covers the prepared-style series/voltage-divider, parallel-resistor and RC examples, plus the requirement that interpretation carries a caution. Run from the project root:

    python -m unittest discover -s tests -v

Review each detected topology against the actual CircuitJS drawing. In particular, series relationships are evaluated in the resistor-only subgraph; another component attached to a shared node can materially change circuit behaviour. Diode bridge recognition is only a candidate based on device count until diode orientation and full connectivity are interpreted.

### Current limitations
- The Copilot does not yet read the live CircuitJS canvas or automatically extract schematic topology/component values. Students must provide circuit descriptions and simulator observations.
- Conversation and project context remain session-based; persistent user accounts and cloud history are not included.
- AI-generated advice is not verified simulation output, a safety approval or a substitute for datasheet, lecturer and laboratory checks.
- This is a development branch. Runtime testing and a separate Streamlit preview deployment are still required.

### Safe development workflow
- Release 2 branch: `release-2/ai-engineering-copilot`
- Parent: `release-1/engineering-interface`
- Do not merge to `main`, alter the stable backup or change the working deployment until tests pass and the owner approves.


### Release 2.3 — Simulation Intelligence

Release 2.3 adds a deterministic comparison workflow for student-supplied theoretical and CircuitJS simulation values.

#### Capabilities
- Upload a CSV with `measurement,theoretical,simulated` columns.
- Optionally provide units, row-specific percentage tolerance and absolute tolerance for zero-reference measurements.
- Calculate signed absolute difference and percentage error when the theoretical reference is non-zero.
- Flag each comparison as within tolerance, outside tolerance or requiring review.
- Download a text comparison summary.
- Include the comparison summary in the AI Copilot context when an API key is configured.

#### CSV format
Download the in-app template or create a CSV with these columns:

```csv
measurement,theoretical,simulated,unit,tolerance_pct,tolerance_abs
Output voltage,5.0,4.92,V,5,
Resistor current,0.005,0.00495,A,5,
Capacitor final voltage,0,0.02,V,,0.05
```

#### Important interpretation limits
This workflow compares values entered by the student. It does not connect to, control or read the live CircuitJS simulation; it does not solve the circuit or prove that a measurement is correct. A tolerance flag is a prompt to investigate, not proof of a fault. Check units, measurement points, loading, component tolerances, simulator model assumptions, initial conditions and rounding. Percentage error is undefined for a zero theoretical reference, so an absolute tolerance is required for a pass/fail decision.

#### Release 2.3 regression tests
Run all Release 2 tests from the project root:

    python -m unittest discover -s tests -v

The tests cover CSV validation, percentage error, tolerance classification and zero-reference handling. They must be executed locally before describing the release as runtime-verified.


### Release 2.4 — Intelligent Fault Diagnosis

Release 2.4 adds an evidence-led troubleshooting workflow. Students can provide a Release 2.3 comparison CSV, paste topology interpretation notes, and describe observed symptoms. The rule-based engine produces evidence statements and a prioritized list of checks.

#### Supported investigation cues
- Out-of-tolerance output voltage and current measurements.
- Possible voltage-divider loading or node/reference problems.
- Series/parallel resistor topology notes.
- RC charging/discharging and time-constant checks.
- Diode/rectifier orientation and ripple checks.
- Missing output/current and overheating symptoms.

#### Important limits
This is a transparent rules-based investigation aid, not a SPICE solver, autonomous diagnosis model or confirmation that a component has failed. It only reasons from student-supplied values, notes and symptoms. It does not inspect the live CircuitJS canvas or collect measurements. Heuristic topology notes must be checked against the actual circuit. For physical builds, isolate power before rewiring and use appropriate isolated, current-limited low-voltage supplies for student experiments.

#### Release 2.4 regression tests
Run from the project root:

    python -m unittest discover -s tests -v

Tests cover missing evidence, targeted voltage checks, voltage-divider loading, rectifier diode-orientation checks, overheating safety priority and diagnostic uncertainty.


### Release 2.5 — Component Intelligence

Release 2.5 adds a searchable educational component reference library in the AI Engineering Copilot.

#### Initial catalogue coverage
- Passive components: fixed resistors, aluminium electrolytic capacitors, ceramic capacitors and potentiometers.
- Semiconductors: rectifier/signal diodes, BJTs and power MOSFETs.
- Optoelectronics: LEDs.
- Integrated circuits and power: operational amplifiers and linear voltage regulators.
- Magnetics, protection and switching: inductors, fuses and electromechanical relays.

#### Component reference features
- Operating principle and common applications.
- Design-selection criteria including electrical, thermal, dynamic and package considerations where relevant.
- Common failure modes and verification guidance.
- Pinout and polarity cautions.
- Downloadable component-selection checklist.
- Optional session-only transfer of the selected component reference into AI Copilot context.

#### Specification and safety policy
The catalogue intentionally does not assign universal numeric ratings or assume universal pinouts. These depend on the exact manufacturer part number, package, revision and operating conditions. Students must verify voltage, current, power, thermal, safe-operating-area, frequency, derating and pin configuration against the exact manufacturer's datasheet. Generic catalogue entries are educational guidance, not a component approval or substitute for laboratory review.

#### Release 2.5 regression tests
Run from the project root:

    python -m unittest discover -s tests -v

Tests cover catalogue integrity, keyword search, family filtering, profile completeness, unknown identifiers, checklist generation and summary generation.


### Release 2.6 — Engineering Design Assistant

Release 2.6 adds a first-pass design workflow for a low-voltage regulated DC supply using an isolated AC source, full-wave bridge rectifier, smoothing capacitor and linear regulator.

#### Design inputs
- Isolated secondary RMS voltage and AC frequency.
- Target DC output voltage and maximum load current.
- Target peak-to-peak ripple.
- Assumed diode forward drop and regulator dropout.
- Ambient temperature and optional user-supplied regulator thermal resistance.

#### Calculations
- Secondary peak and estimated rectified peak after two diode drops.
- Full-wave ripple frequency.
- First-order minimum smoothing capacitance using C ≈ I/(fripple × Vripple).
- Estimated ripple-valley and average unregulated voltage.
- Regulator input headroom against the stated dropout assumption.
- Approximate regulator dissipation.
- Equivalent load resistance and load power.
- Optional indicative junction temperature using the thermal resistance entered by the user.

#### Outputs
- Headroom screening status and engineering warnings.
- Component selection and exact-datasheet verification checklist.
- Validation sequence and downloadable Markdown preliminary design report.
- Optional session-only transfer of the design summary into Copilot context.

#### Engineering limitations
This is a first-pass educational calculation, not a SPICE solver, transformer-sizing tool, certified design or safety approval. It does not model transformer regulation/winding resistance, mains variation, diode dynamics, capacitor ESR/ripple heating/inrush, regulator stability, load transients or real thermal paths. It does not select exact manufacturer part numbers or certify component ratings. Students must verify all limits using the exact component datasheets and recalculate worst-case conditions. Any physical prototype must follow approved laboratory procedures and use a suitable isolated, current-limited low-voltage source. Never connect a beginner circuit directly to mains electricity.

#### Release 2.6 regression tests
Run from the project root:

    python -m unittest discover -s tests -v

Tests cover ripple frequency, capacitance estimate, load calculations, insufficient headroom warnings, optional thermal estimation, invalid inputs and report limitations.


## Release 3.1 — Interactive Engineering Studio

Release 3 begins with a local, structured circuit editor and transparent DC operating-point solver.

### Included
- Editable component network table with reference, type, terminal nodes and value.
- Initial supported elements: ideal DC voltage sources and resistors.
- Visual topology map generated from the entered node connections.
- Modified nodal analysis (MNA) solver for DC node voltages and source currents.
- Per-component voltage, current and power calculations.
- Positive/negative voltage probe between any two solved nodes.
- Downloadable SPICE-style operating-point netlist and Markdown analysis report.
- Example 10 V resistive divider.

### Scope and limitations
This is not yet a drag-and-drop schematic canvas, CircuitJS bridge, or full SPICE implementation. It does not model capacitors, inductors, AC/transient behaviour, diodes, transistors, parasitics, thermal effects or physical safety. The topology drawing is a connectivity overview, not a standards-compliant schematic. Solver output is ideal-model calculation, not simulator or bench measurement. Never treat a calculated result as approval to build a physical circuit.

### Release 3.1 tests
Run `python -m unittest discover -s tests -p "test_release3*.py" -v`.


## Release 3.2 — Visual schematic and CircuitJS bridge

Release 3.2 builds on the local DC editor with a component palette and a simulator hand-off.

### What's new
- Component palette for adding ideal resistors and DC voltage sources by reference, terminal nodes and value.
- Schematic-style view with resistor and source symbols and shared node markers.
- CircuitJS text export for the supported resistor and ideal DC voltage-source subset.
- Encoded CircuitJS preview embedded in the Studio, using the existing hosted CircuitJS service.
- Downloadable CircuitJS circuit text for independent opening/import.

### Compatibility and limits
The CircuitJS bridge currently translates only ideal resistors and ideal DC voltage sources from this Studio. It does not yet translate capacitors, inductors, diodes, transistors, dependent sources, or other SPICE elements. The generated schematic layout is an automatically arranged topology view, not a manual drag-and-drop editor; parallel branches and dense networks may need layout refinement. Check the CircuitJS result independently against the local MNA calculations. The embedded preview requires access to the upstream hosted CircuitJS service.

### Release 3.2 tests
The Release 3 test module now includes checks for CircuitJS text generation, URL encoding and ground-node validation. Run:
`python -m unittest discover -s tests -p "test_release3*.py" -v`


## Release 3.3 — Dynamic circuit laboratory and virtual instruments

Release 3.3 adds analytical first-order transient experiments alongside the DC network editor.

### New capabilities
- Ideal series RC capacitor-voltage step response, including configurable initial capacitor voltage.
- Ideal series RL inductor-current step response, including configurable initial inductor current.
- Calculated time constant, final response and approximate five-time-constant settling time.
- Waveform plot with a movable time cursor and interpolated readings.
- Virtual DMM readout for response voltage/current and series current at the cursor.
- CSV waveform export and downloadable transient analysis report.
- Ten dedicated regression tests for RC/RL time constants, initial/final conditions, cursor behaviour, validation and exports.

### Model boundaries
These are closed-form first-order ideal circuit models, not a general-purpose transient solver and not live CircuitJS measurements. They assume a constant ideal step source and constant component values. They omit parasitics, ESR, leakage, inductor saturation/core loss, switching effects, nonlinear semiconductor behaviour, probe loading, noise and measurement uncertainty. The virtual instruments are software readouts of calculated values, not hardware interfaces.

### Release 3.3 tests
Run:
`python -m unittest discover -s tests -p "test_release3_transient.py" -v`


## Release 3.4 — Semiconductor and rectifier laboratory

Release 3.4 adds three educational workbenches to the Interactive Engineering Studio.

### Diode characteristics
- Interactive ideal Shockley diode I–V curve.
- Adjustable saturation current, ideality factor and temperature.
- Voltage probe for calculated diode current.
- Explicit exclusion of series resistance, reverse breakdown, junction capacitance and self-heating.

### LED series-resistor design
- Supply voltage, assumed LED forward voltage and target current inputs.
- Minimum series resistance calculation.
- Suggested E12 resistor rounded upward so the nominal calculated current does not exceed the target.
- Estimated LED current and resistor dissipation.
- Suggested resistor power rating with a 2x design margin; verify the exact LED and resistor datasheets.

### Rectifier and smoothing-capacitor estimator
- Half-wave and full-wave bridge configurations.
- Transformer secondary RMS voltage, 50/60 Hz frequency, load current, capacitance and assumed diode-drop inputs.
- Peak voltage after assumed diode drops, ripple frequency, estimated ripple, valley and average output.
- Approximate capacitor-discharge waveform, CSV export and design-note report.
- Uses the first-order estimate ΔV ≈ I/(f_ripple C); full-wave bridge ripple frequency is twice the AC frequency.

### Model and safety boundaries
These are educational first-pass models, not a general semiconductor SPICE model or a validated power-supply design. The Shockley curve omits series resistance, reverse breakdown and thermal effects. Rectifier estimates omit transformer regulation/resistance, diode dynamics/heating, capacitor ESR and ripple-current rating, inrush, mains variation, regulator behaviour and load transients. The waveform is an approximate capacitor-discharge ramp, not a simulated diode conduction waveform. Verify component datasheets and supervise experiments using isolated low-voltage AC only; never connect student circuits directly to mains.

### Release 3.4 tests
Eleven regression tests cover Shockley current direction, diode curve output, LED resistor sizing, bridge ripple frequency, diode-drop accounting, capacitance/ripple relationship, waveform/report generation and input validation. They have been added but not executed. Run:
`python -m unittest discover -s tests -p "test_release3_semiconductors.py" -v`


### Release 3.5 — Advanced Power Supply Design Studio

Release 3.5 extends the semiconductor and rectifier laboratory into a system-level, first-pass design workflow for an isolated low-voltage AC supply.

#### Capabilities
- Define regulated output voltage, maximum load current and reservoir-ripple target.
- Compare half-wave and full-wave bridge rectification.
- Estimate transformer secondary current and apparent-power (VA) requirements using an adjustable current form factor.
- Include transformer regulation and low-line allowances in a simplified worst-case estimate.
- Calculate reservoir capacitance, ripple frequency, capacitor-discharge ripple and a separate ESR ripple estimate.
- Screen the capacitor voltage rating against a simple margin.
- Estimate regulator headroom, steady-state dissipation and junction temperature.
- Estimate a heatsink thermal-resistance target from entered thermal parameters.
- Display a functional block diagram and download a detailed Markdown design report or CSV results.

#### Engineering assumptions and limitations
This is a transparent educational estimate, not a validated or construction-ready power supply. Transformer current form factor is user-adjustable because capacitor-input rectifier RMS current depends on transformer impedance and charging conduction angle. Ripple uses a first-order constant-load-current approximation; diode loss, regulator thermal behaviour and heatsink estimates are simplified. It does not model mains-side circuitry, transformer winding waveforms, inrush, fuse selection, insulation coordination, PCB creepage/clearance, detailed semiconductor stress, or regulator safe operating area. Verify exact manufacturer datasheets and independently simulate and measure the design.

Use only an appropriately isolated, current-limited low-voltage AC source for supervised student experiments. Never connect student circuits directly to mains electricity.

#### Regression tests
Run from the repository root:

    python -m unittest discover -s tests -p "test_release3_power_supply.py" -v

The tests cover rectifier ripple frequency, diode-drop accounting, capacitance/ripple relationships, low-line headroom, thermal calculations, report content and input validation. They must be executed locally before describing the release as runtime-verified.

#### Safe release workflow
- Development branch: `release-3/interactive-engineering-studio`
- Release 3.5 is additive to the Release 3.4 Studio.
- Do not merge to `main` or alter the stable deployment until local tests, runtime preview and owner approval are complete.


### Release 3.6 — Intelligent Circuit Design Validation

Release 3.6 adds a deterministic, rule-based validation layer to the Interactive Engineering Studio. It complements the Release 3.1 DC network solver and Release 3.5 power-supply estimator; it does not use an AI model or replace a SPICE simulator.

#### Validation capabilities
- **Circuit structure:** checks empty networks, missing/duplicate references, missing terminals, same-node connections, unsupported element types, non-finite values, non-positive resistor values, explicit ground node and disconnected/floating nodes.
- **Operating-point component ratings:** allows students to enter datasheet maximum voltage, current and power for each solved component. Calculated absolute operating-point magnitudes are compared with those supplied limits; exceeded limits are errors and values at or above 80% of a supplied limit are warnings.
- **Power-supply review:** reviews Release 3.5 low-line regulator headroom, reservoir valley, ripple target, ESR-inclusive ripple estimate, simplified thermal status, capacitor voltage screening and transformer VA estimate.
- **Actionable findings:** results are grouped into errors, warnings, information and passed checks. Missing component ratings are explicitly reported as unverified, never silently treated as safe.

#### Important limitations
Validation is only as good as the entered circuit, solved model and component ratings. The local DC solver currently supports ideal DC voltage sources and resistors. Component rating checks compare DC operating-point magnitudes only; they do not evaluate transient or surge stress, tolerance distributions, temperature derating, safe operating area, frequency response, insulation, creepage/clearance, fuse coordination or applicable standards. The power-supply review inherits all Release 3.5 model limitations. A passed check is not a safety approval or proof of construction readiness.

#### Regression tests
Run from the repository root:

    python -m unittest discover -s tests -p "test_release3_validation.py" -v

The tests cover circuit structure, ground connectivity, floating nodes, unsupported elements, component rating exceedance/margins, missing ratings and power-supply review flags. Execute locally and complete a Streamlit preview test before describing the release as runtime-verified.

#### Safe release workflow
- Development branch: `release-3/interactive-engineering-studio`
- Release 3.6 is integrated additively after Release 3.5 in the Studio.
- Do not merge to `main` or change the stable deployment until local tests, runtime preview and owner approval are complete.


### Release 3.7 — Fault Detective and Troubleshooting Laboratory

Release 3.7 adds a virtual fault-injection exercise to the Interactive Engineering Studio. Students select a component and introduce a controlled software-only fault into a copy of the circuit, then compare the baseline and faulted ideal DC operating points.

#### Supported virtual fault scenarios
- Open component: removes the selected component from the virtual network.
- Short resistor: substitutes a configurable very-low resistance for a selected resistor.
- Wrong component value: multiplies the selected component value by a configurable factor.
- Reversed voltage source: reverses the sign of a selected ideal DC voltage source.

#### Learning workflow
- Select a component from the current Studio network.
- Choose a compatible fault type and inject it into a virtual copy; the student's original circuit is not changed.
- Compare baseline and faulted node voltages, component currents and power.
- Review a fault-mechanism explanation and a safe, measurement-led troubleshooting sequence.
- Download a fault diagnosis exercise report.

#### Scope and limitations
Fault injection is supported only for the current ideal DC resistor and ideal voltage-source solver. The virtual short is represented by a small nonzero resistance, not a physical zero-ohm short. An open or other injected fault may make the network disconnected or mathematically singular; in that case the solver error is shown rather than inventing operating values. The lab does not simulate diodes, transistors, capacitors, inductors, AC behaviour, transients, thermal failure, noise, component tolerances or real instrument measurements. It does not automatically identify an unknown physical fault from measurements; students select the fault scenario for this guided exercise.

The comparisons are simulated ideal-model results, not measured data. Never deliberately short a live circuit. Use only supervised, isolated, current-limited low-voltage equipment for physical work, and power down before rewiring.

#### Regression tests
Run from the repository root:

    python -m unittest discover -s tests -p "test_release3_fault_diagnosis.py" -v

The tests cover fault injection, invalid fault/component combinations, value changes, polarity reversal, operating-point comparison and report generation. Execute locally and complete a Streamlit preview test before describing the release as runtime-verified.

#### Safe release workflow
- Development branch: `release-3/interactive-engineering-studio`
- Release 3.7 is integrated additively after Release 3.6.
- Do not merge to `main` or alter the stable deployment until local tests, runtime preview and owner approval are complete.


### Release 3.8 — Engineering Project Factory

Release 3.8 connects the learning and analysis capabilities into a structured project-planning workflow. Students select a project template, customise its title and level, enter project-specific design inputs, review preliminary calculations, and generate a downloadable project pack.

#### Included project templates
- **Regulated low-voltage DC power supply:** requirements, rectification/filtering/regulation architecture, preliminary load estimates and a hand-off to the Release 3.5 Power Supply Studio for more detailed first-pass estimates.
- **Automatic LDR-controlled light:** bright/dark divider calculations, sensor and switching-stage planning.
- **RC timing and delay circuit:** time constant and selected threshold-delay calculations, with a hand-off to the Release 3.3 Dynamic Circuit Laboratory.
- **LED indicator/current-limiting driver:** minimum resistor, next-higher E12 resistor, actual current and resistor dissipation estimates.
- **Low-voltage DC motor PWM controller:** ideal average-voltage and first-pass power estimates with driver/protection design guidance.
- **555 timer astable oscillator:** approximate frequency, high/low times and duty-cycle calculations.

#### Generated project pack
Each project pack contains a goal, learning outcomes, functional requirements, system block architecture, preliminary bill of materials with selection guidance, first-pass calculations, a sequenced design workflow, verification/test plan, 100-point assessment rubric, safety notes and student reflection prompts. The title and student level can be customised before export.

#### Engineering scope and limitations
These are guided educational templates, not complete circuit schematics, validated designs or construction-ready instructions. Calculations are simplified and disclose key assumptions. For example, the LDR calculation assumes the LDR is the upper divider leg; the motor PWM calculation is an ideal average-value estimate and excludes switching losses and motor dynamics; the 555 equations are approximate; and the LED resistor recommendation does not replace datasheet verification. The regulated supply template does not replace the detailed Release 3.5 estimator. Students must select exact parts from datasheets, independently verify calculations, simulate with appropriate models, and obtain instructor approval before construction.

Use supervised, isolated, current-limited low-voltage equipment only. The project factory does not provide mains-side design or safety certification.

#### Regression tests
Run from the repository root:

    python -m unittest discover -s tests -p "test_release3_project_factory.py" -v

The tests cover template completeness, assessment rubric totals, calculation outputs, invalid inputs, custom project metadata and report sections. Execute locally and complete a Streamlit preview test before describing the release as runtime-verified.

#### Safe release workflow
- Development branch: `release-3/interactive-engineering-studio`
- Release 3.8 is integrated additively after Release 3.7.
- Do not merge to `main` or alter the stable deployment until local tests, runtime preview and owner approval are complete.


### Release 3.9 — AI Project Tutor and Design Reviewer

Release 3.9 adds a project-specific tutoring and evidence-review workflow for the six Release 3.8 project templates.

#### Offline project reviewer
- Students organise their evidence into requirements, theory/calculations, component selection and datasheets, schematic/simulation, testing, discussion and safety.
- A transparent completeness rubric assigns partial evidence points and identifies missing sections.
- Project-specific keyword checks highlight topics that have not yet been mentioned.
- A Markdown review report can be downloaded.

The score is an **evidence-completeness indicator**, not a technical grade. It does not solve or verify equations, inspect schematic files, confirm datasheet values, assess standards compliance or approve a physical design.

#### Socratic tutor
- Five guided questions for each of the six project types.
- Questions encourage students to explain principles, derive equations, justify choices, consider tolerances and plan verification.
- An offline self-check prompts students to state the governing principle, equation, units, assumptions and next verification step.

#### Optional live AI tutor
- An optional OpenAI-compatible chat-completions connection uses `OPENAI_API_KEY`, optional `OPENAI_MODEL` (default `gpt-4o-mini`) and optional `OPENAI_BASE_URL` Streamlit Secrets.
- No API request is made unless the student presses the live tutor button and a key is configured.
- The offline reviewer and Socratic question bank remain available without an API key or API expenditure.
- API usage is billed separately by the API provider; a ChatGPT subscription does not fund API calls.

#### Safety and limitations
AI responses can be incomplete or incorrect. Students must independently derive and verify calculations, check exact manufacturer datasheets, and obtain instructor approval. The AI tutor is instructed not to certify safety or invent component ratings. Use supervised, isolated, current-limited low-voltage equipment only; never connect student circuits directly to mains electricity.

#### Regression tests
Run:
`python -m unittest discover -s tests -p "test_release3_tutor.py" -v`

The tests cover all six question banks, evidence scoring, project-specific topic gaps, unknown-project validation and tutor-context construction. Tests have been added but must be executed locally before runtime verification.

#### Safe release workflow
- Development branch: `release-3/interactive-engineering-studio`
- Release 3.9 is additive to the existing Release 3.1–3.8 workflows.
- Do not merge to `main` or change the stable deployment until tests, local Streamlit preview and owner approval are complete.


### Release 4.0 — Electronics University

Release 4.0 introduces a structured general electronics learning hub alongside the engineering studio.

#### Learning pathways
Eight lesson areas provide learning outcomes, explanatory content, key equations, worked examples, practical activities, common misconceptions and short knowledge checks:
- DC circuit fundamentals
- Series, parallel and network analysis
- Capacitors, inductors and transient response
- Semiconductor fundamentals and diodes
- Power supplies and linear regulation
- Transistors and basic amplifiers
- Operational amplifiers and analogue interfaces
- Digital electronics and logic systems

#### Component library
The searchable reference includes resistors, capacitors, inductors, diodes, LEDs, Zener diodes, BJTs, MOSFETs, operational amplifiers, 555 timers, transformers, voltage regulators, relays, fuses and potentiometers. Entries cover function, operating principle, selection parameters, common failure modes, verification and cautions.

#### Learning tools
- Filter lessons by learning stage.
- Search lesson and component knowledge.
- Complete short knowledge checks with explanations.
- Download lesson notes and component reference sheets in Markdown.

#### Scope and limitations
This is a general educational foundation, not an official TUT curriculum map and not a replacement for current module guides, prescribed textbooks or lecturer instructions. It does not yet contain a complete semester-by-semester TUT syllabus, institution-specific outcomes, laboratory manuals, assessment banks or persistent student progress. Equations and component information must be checked against authoritative references and exact manufacturer datasheets. Physical experiments require approved, supervised, isolated low-voltage equipment.

#### Regression tests
Run from the repository root:

    python -m unittest discover -s tests -p "test_release4_university.py" -v

The tests cover lesson completeness, component reference structure, search, exports and invalid lookups. Execute locally and complete a Streamlit preview before describing Release 4.0 as runtime-verified.

#### Safe release workflow
- Development branch: `release-4/electronics-university`
- Release 4.0 is integrated after Release 3.9 in the development Studio.
- Do not merge to `main` or alter the stable deployment until tests, local preview and owner approval are complete.


### Release 4.1 — Interactive Electronics Classroom

Release 4.1 adds a guided classroom layer alongside the Release 4.0 Electronics University content.

#### Guided classrooms
- Ohm's law: from prediction to measurement.
- Voltage divider: calculate and investigate loading.
- RC charging: read the transient waveform.
- Kirchhoff's laws: reason about a network.

Each classroom includes a learning goal, sequenced instructional steps, key equations, an activity and a knowledge check with worked feedback.

#### Interactive experiments
- Live Ohm's-law current and power calculator.
- Loaded/unloaded voltage-divider calculator.
- Ideal RC charging waveform with adjustable resistance, capacitance and supply voltage; waveform CSV export.
- KCL node-current investigation.

#### Knowledge checks
Students can select Foundation, Intermediate or Advanced difficulty where questions are available. Each answer can be checked for immediate explanatory feedback. Progress and answer feedback are session-only and are not yet saved to a student account.

#### Model boundaries
The RC curve and circuit calculations are idealised educational models. They do not represent live CircuitJS measurements, physical instruments, component tolerances, parasitics, thermal behaviour or a complete SPICE solver. The classroom is general electronics content, not an official TUT syllabus mapping.

#### Regression tests
Run from the repository root:

    python -m unittest discover -s tests -p "test_release4_classroom.py" -v

Complete a local Streamlit preview before describing the classroom as runtime-verified. Physical experiments require approved, supervised, isolated and current-limited low-voltage equipment. Never connect student-built circuits directly to mains.

Development branch: `release-4/electronics-university`. Stable `main` and the existing deployed application remain unchanged.


### Release 4.2 — Engineering Assessment Centre and Practical Laboratory

Release 4.2 adds formative assessment and structured practical-laboratory resources to the Electronics University.

#### Assessment centre
Four topic banks provide four multiple-choice questions each:
- DC fundamentals
- Capacitors and transients
- Diodes and power supplies
- Semiconductor and transistor basics

Students submit a topic assessment and receive a score, correct answers, explanations and a downloadable Markdown review. Unanswered questions receive no marks. The score is formative practice, not an accredited examination result.

#### Practical laboratory manuals
Four editable/downloadable practical templates are included:
- Resistor network verification
- RC charging and discharging
- Diode rectifier investigation
- Transistor switching investigation

Each manual contains a purpose, learning outcomes, apparatus list, sequenced procedure, results-table templates, analysis prompts and safety guidance. Student name and practical date can be added to the export.

#### Session learning record
Assessment attempts are listed during the active Streamlit session, with the latest result by topic and CSV export. Data is not persisted across sessions and is not connected to an institutional student account or gradebook.

#### Scope, assumptions and safety
Assessment questions are introductory formative examples, not a complete curriculum assessment bank. Practical manuals are templates and must be reviewed and approved by a qualified instructor before use. The manuals do not certify circuit designs, component ratings, instrument setups or laboratory safety. Use only instructor-approved, isolated, current-limited low-voltage equipment; never use mains electricity for student-built experiments. Observe exact manufacturer datasheets and local laboratory procedures.

#### Regression tests
Run from the repository root:

    python -m unittest discover -s tests -p "test_release4_assessment.py" -v

The tests cover assessment bank structure, scoring, unanswered questions, feedback reports, manual completeness and manual exports. Execute tests and complete a local Streamlit preview before describing the feature as runtime-verified.

Development branch: `release-4/electronics-university`. Stable `main` and the existing deployed application remain unchanged.


### Release 4.3 — Visual Electronics Learning Engine

Release 4.3 adds four interactive, parameter-driven visual demonstrations to the Electronics University.

#### Current flow and voltage drops
- A visual series-resistor circuit diagram.
- Adjustable DC source voltage and two resistor values.
- Calculated shared series current, individual voltage drops and resistor power.
- Voltage-drop table, bar chart and CSV export.
- A Kirchhoff voltage-law sum check.

#### Diode behaviour
- Diode symbol with anode/cathode labels and forward direction.
- Adjustable junction voltage, temperature and ideality factor.
- Ideal Shockley-equation current estimate and I–V curve.
- Downloadable I–V data.

The Shockley model omits series resistance, reverse breakdown, junction capacitance, self-heating and high-level injection. It is not a complete diode model.

#### Transistor switching
- Visual low-side switch representation.
- Interactive ON/OFF control.
- Adjustable supply and resistive load.
- First-pass load current, load voltage and state display.

The demonstration uses a fixed saturation-drop approximation. It does not calculate base/gate drive, switching transients, device safe operating area or heating.

#### Capacitor charging
- Adjustable source voltage, series resistance and capacitance.
- RC time constant and capacitor/resistor voltage waveforms.
- CSV export and 63.2% at one time constant explanation.

#### Model boundaries
These are deterministic mathematical teaching models, not live CircuitJS canvas inspection, a general-purpose SPICE engine, physical measurements or safety certification. Idealisations and omissions are shown in the interface. Component datasheets and instructor-approved laboratory procedures remain authoritative.

Use only supervised, isolated, current-limited low-voltage equipment for physical experiments. De-energise before rewiring. Never connect student-built circuits directly to mains.

#### Regression tests
Run from the repository root:

    python -m unittest discover -s tests -p "test_release4_visual_engine.py" -v

The tests cover Ohm's law, series voltage division, diode current/curve, transistor switch states, RC waveform values, invalid inputs and report labelling. Execute tests and complete a local Streamlit preview before describing the release as runtime-verified.

Development branch: `release-4/electronics-university`. Stable `main` and the existing deployed application remain unchanged.


### Release 4.4 — Engineering Design Challenge Centre

Release 4.4 adds five structured engineering design challenges that ask students to turn theory into a documented, evidence-led design.

#### Challenge briefs
- **Regulated 5 V DC supply:** requirements, rectifier/filter/regulator architecture, ripple and thermal estimates, datasheet selection and verification planning.
- **Automatic streetlight controller:** bright/dark LDR characterisation, divider calculations, threshold selection, switching-stage justification and flicker/hysteresis investigation.
- **Low-voltage PWM motor controller:** motor running/stall data, PWM requirements, average-voltage estimates, driver/protection selection and thermal verification.
- **RC delay circuit:** threshold definition, derivation of the exponential response, practical R/C selection, waveform evidence and tolerance/loading discussion.
- **555 astable oscillator:** timing derivation, RA/RB/C selection, topology and duty-cycle limitations, timer-variant datasheet checks and waveform verification.

#### Student design workspace
Each challenge includes a scenario, measurable requirements, design constraints, milestones, deliverables and a weighted 100-point rubric. Students can organise evidence under each rubric criterion, record a reflection, mark evidence categories as reviewed and export a Markdown submission pack. A separate challenge brief can also be downloaded.

#### Evidence indicator and limitations
The displayed percentage is a **self-reported evidence-completeness indicator only**. It awards the rubric weight of categories the student marks complete; it does not assess technical correctness, independently verify calculations or datasheets, grade academic work, or approve safety. Submission data is session-based; students must download their work before leaving the app. There are no student accounts, persistent records, institutional submission links or lecturer gradebook integration.

The challenge templates are educational starting points, not official TUT assessments or complete module specifications. Instructors should adapt and approve briefs, rubrics and practical work for the relevant module. Use only instructor-approved, supervised, isolated and current-limited low-voltage equipment. Never connect student-built circuits directly to mains. Verify equations, exact manufacturer datasheets and simulation assumptions.

#### Regression tests
Run from the repository root:

    python -m unittest discover -s tests -p "test_release4_challenges.py" -v

The tests cover challenge completeness, rubric totals, evidence-completion behaviour, unknown challenge handling and submission-pack content. Execute tests and complete a local Streamlit preview before describing Release 4.4 as runtime-verified.

Development branch: \`release-4/electronics-university\`. Stable \`main\` and the existing deployed application remain unchanged.
