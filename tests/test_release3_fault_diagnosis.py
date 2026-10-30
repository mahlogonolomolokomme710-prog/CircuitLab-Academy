import unittest

from release3_fault_diagnosis import (
    inject_fault, compare_operating_points, explain_fault, build_fault_report
)
from release3_studio import solve_dc_network

DIVIDER = [
    {"Ref":"V1","Type":"V","Node1":"N1","Node2":"0","Value":10.0},
    {"Ref":"R1","Type":"R","Node1":"N1","Node2":"N2","Value":1000.0},
    {"Ref":"R2","Type":"R","Node1":"N2","Node2":"0","Value":1000.0},
]


class FaultDiagnosisTests(unittest.TestCase):
    def test_open_component_removes_selected_part(self):
        changed = inject_fault(DIVIDER, "R2", "Open component")
        self.assertNotIn("R2", [row["Ref"] for row in changed])

    def test_short_resistor_reduces_resistance(self):
        changed = inject_fault(DIVIDER, "R2", "Short resistor", short_resistance_ohm=0.001)
        self.assertEqual(next(row for row in changed if row["Ref"] == "R2")["Value"], 0.001)

    def test_wrong_value_applies_multiplier(self):
        changed = inject_fault(DIVIDER, "R2", "Wrong component value", wrong_value_factor=3)
        self.assertEqual(next(row for row in changed if row["Ref"] == "R2")["Value"], 3000.0)

    def test_reversed_source_changes_sign(self):
        changed = inject_fault(DIVIDER, "V1", "Reversed voltage source")
        self.assertEqual(changed[0]["Value"], -10.0)

    def test_short_fault_rejects_voltage_source(self):
        with self.assertRaises(ValueError):
            inject_fault(DIVIDER, "V1", "Short resistor")

    def test_reversed_source_rejects_resistor(self):
        with self.assertRaises(ValueError):
            inject_fault(DIVIDER, "R1", "Reversed voltage source")

    def test_invalid_multiplier_rejected(self):
        with self.assertRaises(ValueError):
            inject_fault(DIVIDER, "R1", "Wrong component value", wrong_value_factor=1)

    def test_faulted_divider_changes_node_voltage(self):
        baseline = solve_dc_network(DIVIDER)
        altered = solve_dc_network(inject_fault(DIVIDER, "R2", "Wrong component value", 3))
        comparison = compare_operating_points(baseline, altered)
        n2 = comparison["nodes"].set_index("Node").loc["N2"]
        self.assertNotAlmostEqual(n2["Baseline (V)"], n2["Faulted (V)"])

    def test_open_branch_is_reported_in_comparison(self):
        baseline = solve_dc_network(DIVIDER)
        altered = solve_dc_network(inject_fault(DIVIDER, "R2", "Open component"))
        comparison = compare_operating_points(baseline, altered)
        row = comparison["components"].set_index("Reference").loc["R2"]
        self.assertEqual(row["Status"], "Removed (open)")

    def test_diagnostic_steps_and_report(self):
        diagnosis = explain_fault("Wrong component value", "R1", "R")
        self.assertGreaterEqual(len(diagnosis["steps"]), 3)
        comparison = compare_operating_points(solve_dc_network(DIVIDER), solve_dc_network(DIVIDER))
        report = build_fault_report("R1", "Wrong component value", diagnosis["explanation"], comparison)
        self.assertIn("Safety and limitations", report)
        self.assertIn("R1", report)


if __name__ == "__main__":
    unittest.main()
