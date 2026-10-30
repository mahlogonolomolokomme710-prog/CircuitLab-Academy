import unittest

from release3_validation import (
    validate_netlist, validate_component_ratings, validate_power_supply_design
)
from release3_power_supply import design_power_supply


class CircuitValidationTests(unittest.TestCase):
    def test_valid_grounded_voltage_divider_passes_structure(self):
        records = [
            {"Ref":"V1","Type":"V","Node1":"N1","Node2":"0","Value":10},
            {"Ref":"R1","Type":"R","Node1":"N1","Node2":"N2","Value":1000},
            {"Ref":"R2","Type":"R","Node1":"N2","Node2":"0","Value":1000},
        ]
        findings = validate_netlist(records)
        self.assertTrue(any(x["code"] == "STRUCTURE_OK" for x in findings))
        self.assertFalse(any(x["level"] == "error" for x in findings))

    def test_missing_ground_is_error(self):
        records = [{"Ref":"R1","Type":"R","Node1":"A","Node2":"B","Value":1000}]
        self.assertTrue(any(x["code"] == "NO_GROUND" for x in validate_netlist(records)))

    def test_floating_component_is_detected(self):
        records = [
            {"Ref":"V1","Type":"V","Node1":"A","Node2":"0","Value":5},
            {"Ref":"R1","Type":"R","Node1":"B","Node2":"C","Value":1000},
        ]
        self.assertTrue(any(x["code"] == "FLOATING_NODES" for x in validate_netlist(records)))

    def test_duplicate_reference_is_error(self):
        records = [
            {"Ref":"R1","Type":"R","Node1":"A","Node2":"0","Value":1000},
            {"Ref":"R1","Type":"R","Node1":"B","Node2":"0","Value":2000},
        ]
        self.assertTrue(any(x["code"] == "DUPLICATE_REF" for x in validate_netlist(records)))

    def test_non_positive_resistor_is_error(self):
        records = [{"Ref":"R1","Type":"R","Node1":"A","Node2":"0","Value":0}]
        self.assertTrue(any(x["code"] == "INVALID_RESISTANCE" for x in validate_netlist(records)))

    def test_unsupported_element_is_reported(self):
        records = [{"Ref":"D1","Type":"D","Node1":"A","Node2":"0","Value":0.7}]
        self.assertTrue(any(x["code"] == "UNSUPPORTED_TYPE" for x in validate_netlist(records)))

    def test_component_rating_exceeded_is_error(self):
        solved = [{"Reference":"R1","Voltage (V)":8.0,"Current (A)":0.01,"Power (W)":0.08}]
        ratings = [{"Ref":"R1","Max voltage (V)":5.0,"Max current (A)":0.1,"Max power (W)":0.25}]
        findings = validate_component_ratings(solved, ratings)
        self.assertTrue(any(x["code"] == "RATING_EXCEEDED" for x in findings))

    def test_component_near_limit_is_warning(self):
        solved = [{"Reference":"R1","Voltage (V)":4.5,"Current (A)":0.01,"Power (W)":0.08}]
        ratings = [{"Ref":"R1","Max voltage (V)":5.0,"Max current (A)":0.1,"Max power (W)":0.25}]
        findings = validate_component_ratings(solved, ratings)
        self.assertTrue(any(x["code"] == "RATING_MARGIN" for x in findings))

    def test_missing_component_rating_is_not_assumed_safe(self):
        solved = [{"Reference":"R1","Voltage (V)":2.0,"Current (A)":0.01,"Power (W)":0.02}]
        findings = validate_component_ratings(solved, [{"Ref":"R1"}])
        self.assertTrue(any(x["code"] == "RATING_MISSING" for x in findings))

    def test_power_supply_headroom_failure_is_flagged(self):
        result = design_power_supply(secondary_rms_v=6.0, output_voltage_v=5.0,
                                     regulator_dropout_v=2.0, load_current_ma=500.0)
        findings = validate_power_supply_design(result)
        self.assertTrue(any(x["code"] == "REGULATOR_HEADROOM" for x in findings))

    def test_power_supply_review_always_discloses_model_limits(self):
        findings = validate_power_supply_design(design_power_supply())
        self.assertTrue(any(x["code"] == "MODEL_LIMITATIONS" for x in findings))


if __name__ == "__main__":
    unittest.main()
