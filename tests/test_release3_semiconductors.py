import unittest
import math

from release3_semiconductors import (
    diode_shockley_current, diode_curve, led_series_resistor,
    rectifier_estimate, rectifier_waveform, build_led_report, build_rectifier_report
)


class Release34SemiconductorTests(unittest.TestCase):
    def test_shockley_current_is_zero_at_zero_volts(self):
        self.assertAlmostEqual(diode_shockley_current(0.0), 0.0)

    def test_forward_current_exceeds_reverse_current(self):
        forward = diode_shockley_current(0.6)
        reverse = diode_shockley_current(-0.2)
        self.assertGreater(forward, 0)
        self.assertLess(reverse, 0)
        self.assertGreater(forward, abs(reverse))

    def test_diode_curve_has_expected_columns(self):
        curve = diode_curve(samples=101)
        self.assertEqual(len(curve), 101)
        self.assertIn("voltage_v", curve.columns)
        self.assertIn("current_a", curve.columns)

    def test_invalid_diode_parameters_rejected(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            diode_shockley_current(0.5, saturation_current_a=0)

    def test_led_resistor_rounds_up_and_limits_current(self):
        result = led_series_resistor(5, 2, 10)
        self.assertGreaterEqual(result["recommended_resistance_ohm"], result["minimum_resistance_ohm"])
        self.assertLessEqual(result["actual_current_ma"], 10.0)
        self.assertGreater(result["suggested_power_rating_w"], result["resistor_dissipation_w"])

    def test_led_requires_supply_above_forward_voltage(self):
        with self.assertRaisesRegex(ValueError, "must exceed"):
            led_series_resistor(2, 2, 10)

    def test_bridge_has_twice_line_frequency_ripple(self):
        bridge = rectifier_estimate(12, 50, 100, 1000, "Full-wave bridge")
        half = rectifier_estimate(12, 50, 100, 1000, "Half-wave")
        self.assertEqual(bridge["ripple_frequency_hz"], 100)
        self.assertEqual(half["ripple_frequency_hz"], 50)

    def test_bridge_accounts_for_two_diode_drops(self):
        result = rectifier_estimate(12, 50, 100, 1000, "Full-wave bridge", 0.7)
        self.assertAlmostEqual(result["peak_after_drops_v"], 12 * math.sqrt(2) - 1.4)

    def test_ripple_decreases_with_more_capacitance(self):
        small = rectifier_estimate(12, 50, 100, 470, "Full-wave bridge")
        large = rectifier_estimate(12, 50, 100, 1000, "Full-wave bridge")
        self.assertGreater(small["ripple_pp_v"], large["ripple_pp_v"])

    def test_rectifier_waveform_and_reports(self):
        result = rectifier_estimate(12, 50, 100, 1000, "Full-wave bridge")
        waveform = rectifier_waveform(result)
        self.assertEqual(len(waveform), 1001)
        self.assertIn("output_voltage_v", waveform.columns)
        self.assertIn("Limitations", build_rectifier_report(result))
        led = led_series_resistor(5, 2, 10)
        self.assertIn("datasheet", build_led_report(led).lower())

    def test_invalid_rectifier_inputs_rejected(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            rectifier_estimate(0, 50, 100, 1000)


if __name__ == "__main__":
    unittest.main()
