"""Read the text-based circuit format exported by CircuitJS/Falstad.

This first-pass reader extracts component records and reconstructs connectivity
from orthogonal wire segments. It is an educational aid, not a SPICE solver.
"""
from collections import defaultdict

NAMES = {
    "r": "Resistor", "c": "Capacitor", "l": "Inductor",
    "v": "Voltage source", "i": "Current source", "d": "Diode",
    "t": "Transistor", "q": "Transistor", "z": "Zener diode",
    "g": "Ground", "w": "Wire", "s": "Switch",
    "f": "Fuse", "p": "Potentiometer", "a": "Ammeter",
    "o": "Op-amp", "x": "Subcircuit / other element",
}

def _on_segment(point, segment):
    x, y = point
    x1, y1, x2, y2 = segment
    if x1 == x2 == x:
        return min(y1, y2) <= y <= max(y1, y2)
    if y1 == y2 == y:
        return min(x1, x2) <= x <= max(x1, x2)
    return False

def parse_circuitjs(text):
    """Return component inventory, approximate nets, and parser warnings."""
    records, wires, warnings = [], [], []
    header = None
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if parts[0] == "$":
            header = line
            continue
        if len(parts) < 5:
            warnings.append(f"Line {line_no}: ignored incomplete record.")
            continue
        kind = parts[0].lower()
        try:
            x1, y1, x2, y2 = map(int, parts[1:5])
        except ValueError:
            warnings.append(f"Line {line_no}: could not read terminal coordinates.")
            continue
        item = {"type_code": kind, "type": NAMES.get(kind, f"Unknown ({kind})"),
                "terminals": [(x1, y1), (x2, y2)], "parameters": parts[5:],
                "line": line_no}
        if kind == "w":
            wires.append((x1, y1, x2, y2))
        else:
            records.append(item)
            if kind not in NAMES:
                warnings.append(f"Line {line_no}: unsupported component code '{kind}'.")
    # Build connectivity by joining component terminals and wire endpoints that
    # lie on the same orthogonal wire segment, including wire intersections.
    points = set()
    for item in records:
        points.update(item["terminals"])
    for x1, y1, x2, y2 in wires:
        points.add((x1, y1)); points.add((x2, y2))
    parent = {p: p for p in points}
    def find(p):
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    for seg in wires:
        attached = [p for p in points if _on_segment(p, seg)]
        if attached:
            anchor = attached[0]
            for p in attached[1:]:
                union(anchor, p)
    # Orthogonal wire crossings are treated as junctions in this first-pass model.
    for i, a in enumerate(wires):
        for b in wires[i + 1:]:
            ax1, ay1, ax2, ay2 = a
            bx1, by1, bx2, by2 = b
            if ax1 == ax2 and by1 == by2:
                cross = (ax1, by1)
                if _on_segment(cross, a) and _on_segment(cross, b):
                    points.add(cross)
                    if cross not in parent:
                        parent[cross] = cross
                    for seg in (a, b):
                        ends = [(seg[0], seg[1]), (seg[2], seg[3])]
                        for end in ends:
                            if _on_segment(cross, seg):
                                union(cross, end)
            elif ay1 == ay2 and bx1 == bx2:
                cross = (bx1, ay1)
                if _on_segment(cross, a) and _on_segment(cross, b):
                    if cross not in parent:
                        parent[cross] = cross
                    for seg in (a, b):
                        for end in ((seg[0], seg[1]), (seg[2], seg[3])):
                            if _on_segment(cross, seg):
                                union(cross, end)
    roots = {}
    for p in list(parent):
        root = find(p)
        roots.setdefault(root, len(roots) + 1)
    for item in records:
        item["nets"] = [roots.get(find(p), None) for p in item["terminals"]]
    counts = defaultdict(int)
    for item in records:
        counts[item["type"]] += 1
    lines = ["CircuitJS schematic extraction (first-pass; verify against the simulator):",
             f"Components: {len(records)} · wire segments: {len(wires)} · inferred nets: {len(roots)}"]
    for kind, count in sorted(counts.items()):
        lines.append(f"- {kind}: {count}")
    lines.append("Component details:")
    for index, item in enumerate(records, 1):
        params = " ".join(item["parameters"]) or "no parameters decoded"
        lines.append(f"{index}. {item['type']} | terminals/nets {item['nets']} | raw parameters: {params}")
    if warnings:
        lines.append("Parser warnings:")
        lines.extend(f"- {w}" for w in warnings[:20])
    lines.append("Connectivity is inferred from exported coordinates and wire geometry; confirm ambiguous crossings and component pin semantics in CircuitJS.")
    return {"header": header, "components": records, "wire_count": len(wires),
            "net_count": len(roots), "warnings": warnings, "summary": "\n".join(lines)}
