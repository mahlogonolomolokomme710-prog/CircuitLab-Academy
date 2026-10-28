# CircuitJS1 attribution and integration notes — v0.5

CircuitJS1 is an electronic circuit simulator originally created by Paul Falstad and adapted for browser use by Iain Sharp, with contributions from many others.

- Official upstream source: https://github.com/sharpie7/circuitjs1
- Upstream project documentation: https://github.com/sharpie7/circuitjs1/blob/master/README.md
- Licence: GNU General Public License, version 2 or (at your option) any later version.

## Self-hosting process

Run `python install_circuitjs.py` from the project root. The script clones the upstream repository, copies the compiled web assets from `war/` (excluding `WEB-INF`) into `static/circuitjs/`, and preserves available upstream licence/source notices. Streamlit serves the committed static files from this app using `.streamlit/config.toml`.

The compiled assets are not bundled in this starter ZIP because they must be obtained from the upstream repository. Do not claim the app is self-hosted until `static/circuitjs/circuitjs.html` and `static/circuitjs/circuitjs1/circuitjs1.nocache.js` exist and the app confirms it is using local assets.

## GPL compliance

Open source does not mean copyright-free. Before publishing a redistributed or modified copy, preserve all upstream notices, include the applicable GPL licence text, and comply with the licence's source-code and redistribution obligations. The project repository includes the upstream source URL and installation script; the installed output also copies upstream notices when present. Review the current upstream terms before public release.

## Project-authored prepared examples

The `prepared_circuits/` directory contains small CircuitJS-format educational examples authored for this project. They are loaded via the documented `cct` query parameter. Verify each circuit visually and numerically after installing the upstream compiled assets; the values shown in the learning text are ideal calculations, not a guarantee of physical performance.
