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
