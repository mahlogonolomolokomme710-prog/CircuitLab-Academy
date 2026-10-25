# CircuitLab Academy v0.2

## What changed
- Added a visual circuit workspace with a component selector and schematic highlighting.
- Added component-specific learning cards and connection guidance.
- Added example load-resistor and regulator-dissipation calculations.
- Kept the guided project, component library, calculators, quiz, report builder and curriculum map.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Current limits
This is an educational prototype. The schematic is a guided schematic view and must not be treated as a verified production design. It is not yet a drag-and-drop editor and does not run a SPICE simulation. Exact regulator pinouts, component values and support components must be checked against datasheets. For physical work, use a suitable isolated, current-limited low-voltage source and never connect a beginner circuit directly to mains.

## Next development milestone
Implement a real editable schematic workspace, a verified component/model library, and integration with a circuit simulation engine.
