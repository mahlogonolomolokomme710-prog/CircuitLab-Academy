import unittest

from release2_diagnostics import build_diagnosis


class FaultInvestigationTests(unittest.TestCase):
    def test_empty_evidence_requests_more_information(self):
        result = build_diagnosis(None)
        self.assertIn("Insufficient evidence", result["findings"][0])

    def test_out_of_tolerance_voltage_generates_targeted_checks(self):
        comparison = {"results": [{
            "measurement": "Output voltage", "theoretical": 5.0, "simulated": 4.0,
            "percentage_error": -20.0, "status": "OUTSIDE TOLERANCE",
        }]}
        result = build_diagnosis(comparison)
        self.assertTrue(any("output node" in x.lower() for x in result["checks"]))
        self.assertTrue(any("lower" in x.lower() for x in result["checks"]))

    def test_voltage_divider_topology_generates_loading_check(self):
        result = build_diagnosis(None, "Voltage-divider candidate detected.")
        self.assertTrue(any("connected load" in x.lower() for x in result["checks"]))

    def test_rectifier_symptom_checks_diode_orientation(self):
        result = build_diagnosis(None, symptoms="The rectifier output ripple is too high")
        self.assertTrue(any("diode orientation" in x.lower() for x in result["checks"]))

    def test_overheating_symptom_prioritizes_isolation(self):
        result = build_diagnosis(None, symptoms="The resistor is overheating")
        self.assertIn("STOP", result["checks"][0])

    def test_diagnosis_never_claims_confirmed_fault(self):
        result = build_diagnosis(None, "Possible series-resistor relationship.")
        self.assertTrue(any("not a confirmed diagnosis" in x.lower() for x in result["limitations"]))


if __name__ == "__main__":
    unittest.main()
