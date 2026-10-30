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
