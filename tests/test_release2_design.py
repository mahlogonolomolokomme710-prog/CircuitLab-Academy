import unittest

from release2_design import design_linear_supply, build_design_report


class LinearSupplyDesignTests(unittest.TestCase):
    def base(self):
        return design_linear_supply(
            secondary_vac_rms=9.0,
            mains_frequency_hz=50,
            output_voltage_v=5.0,
            maximum_load_current_a=0.1,
            target_ripple_vpp=1.0,
            diode_forward_drop_v=0.7,
            regulator_dropout_v=2.0,
        )

    def test_full_wave_ripple_frequency(self):
        result = self.base()
        self.assertEqual(result["ripple_frequency_hz"], 100.0)

    def test_capacitance_estimate(self):
        result = self.base()
        self.assertAlmostEqual(result["minimum_capacitance_f"], 0.001, places=9)

    def test_load_equivalent_and_power(self):
        result = self.base()
        self.assertAlmostEqual(result["estimated_load_resistance_ohm"], 50.0)
        self.assertAlmostEqual(result["estimated_load_power_w"], 0.5)

    def test_headroom_warning_when_input_is_too_low(self):
        result = design_linear_supply(5, 50, 5, 0.1, 1, 0.7, 2)
        self.assertEqual(result["status"], "HEADROOM CHECK FAILED")
        self.assertTrue(any("Insufficient estimated regulator headroom" in w for w in result["warnings"]))

    def test_thermal_estimate_only_when_theta_is_supplied(self):
        no_theta = self.base()
        with_theta = design_linear_supply(9, 50, 5, 0.1, 1, 0.7, 2, 25, 50)
        self.assertIsNone(no_theta["estimated_junction_temperature_c"])
        self.assertIsNotNone(with_theta["estimated_junction_temperature_c"])

    def test_invalid_inputs_rejected(self):
        with self.assertRaises(ValueError):
            design_linear_supply(0, 50, 5, 0.1, 1)
        with self.assertRaises(ValueError):
            design_linear_supply(9, 50, 5, 0, 1)

    def test_report_contains_limits_and_datasheet_checks(self):
        report = build_design_report(self.base())
        self.assertIn("Component selection and datasheet checks", report)
        self.assertIn("not a certified design", report.lower())
        self.assertIn("transformer VA", report)


if __name__ == "__main__":
    unittest.main()
