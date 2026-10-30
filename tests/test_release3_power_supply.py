import unittest

from release3_power_supply import design_power_supply, thermal_analysis, build_design_report


class PowerSupplyDesignTests(unittest.TestCase):
    def test_full_wave_ripple_frequency_is_twice_line_frequency(self):
        result = design_power_supply(line_frequency_hz=50.0, topology="Full-wave bridge")
        self.assertEqual(result["ripple_frequency_hz"], 100.0)

    def test_half_wave_ripple_frequency_equals_line_frequency(self):
        result = design_power_supply(line_frequency_hz=50.0, topology="Half-wave")
        self.assertEqual(result["ripple_frequency_hz"], 50.0)

    def test_bridge_uses_two_diode_drops(self):
        result = design_power_supply(secondary_rms_v=12.0, diode_drop_v=0.7)
        self.assertAlmostEqual(result["nominal_peak_after_drops_v"], 12.0 * 2**0.5 - 1.4)

    def test_capacitance_increases_when_ripple_target_is_tighter(self):
        loose = design_power_supply(ripple_target_v=1.0)
        tight = design_power_supply(ripple_target_v=0.5)
        self.assertAlmostEqual(tight["required_capacitance_uf"], 2 * loose["required_capacitance_uf"])

    def test_full_wave_requires_less_capacitance_than_half_wave(self):
        bridge = design_power_supply(topology="Full-wave bridge")
        half = design_power_supply(topology="Half-wave")
        self.assertLess(bridge["required_capacitance_uf"], half["required_capacitance_uf"])

    def test_low_line_headroom_can_fail(self):
        result = design_power_supply(secondary_rms_v=6.0, output_voltage_v=5.0,
                                     regulator_dropout_v=2.0, load_current_ma=500.0)
        self.assertFalse(result["regulator_headroom_ok"])
        self.assertTrue(any("HEADROOM" in warning for warning in result["warnings"]))

    def test_higher_load_increases_regulator_dissipation(self):
        low = design_power_supply(load_current_ma=50.0)
        high = design_power_supply(load_current_ma=200.0)
        self.assertGreater(high["regulator_power_w"], low["regulator_power_w"])

    def test_thermal_analysis_returns_heatsink_target(self):
        result = design_power_supply(load_current_ma=500.0, secondary_rms_v=15.0)
        thermal = thermal_analysis(result)
        self.assertIn("maximum_heatsink_thermal_resistance_c_per_w", thermal)

    def test_report_contains_assumptions_and_safety_limitations(self):
        report = build_design_report(design_power_supply())
        self.assertIn("Assumptions and limitations", report)
        self.assertIn("Never connect student circuits directly to mains", report)

    def test_invalid_topology_is_rejected(self):
        with self.assertRaises(ValueError):
            design_power_supply(topology="Centre tap")

    def test_non_finite_input_is_rejected(self):
        with self.assertRaises(ValueError):
            design_power_supply(secondary_rms_v=float("nan"))

    def test_thermal_limit_must_exceed_ambient(self):
        with self.assertRaises(ValueError):
            design_power_supply(ambient_c=50.0, maximum_junction_c=50.0)


if __name__ == "__main__":
    unittest.main()
