import unittest

from release3_transient import (
    simulate_first_order, sample_at, waveform_frame, build_transient_report
)


class Release33TransientTests(unittest.TestCase):
    def test_rc_time_constant(self):
        r = simulate_first_order("RC", 1000, 100e-6, 5, 1)
        self.assertAlmostEqual(r["tau_s"], 0.1)

    def test_rc_initial_and_final_conditions(self):
        r = simulate_first_order("RC", 1000, 100e-6, 5, 0.5, initial_value=1)
        self.assertAlmostEqual(r["response"][0], 1)
        self.assertAlmostEqual(r["response"][-1], 5, places=2)

    def test_rc_one_time_constant_reaches_632_percent(self):
        r = simulate_first_order("RC", 1000, 100e-6, 5, 0.1)
        self.assertAlmostEqual(r["response"][-1], 5 * (1 - 2.718281828459045**-1), places=4)

    def test_rl_time_constant(self):
        r = simulate_first_order("RL", 10, 0.1, 5, 0.5)
        self.assertAlmostEqual(r["tau_s"], 0.01)

    def test_rl_final_current(self):
        r = simulate_first_order("RL", 10, 0.1, 5, 0.2)
        self.assertAlmostEqual(r["final_value"], 0.5)
        self.assertAlmostEqual(r["response"][-1], 0.5, places=4)

    def test_cursor_interpolation(self):
        r = simulate_first_order("RC", 1000, 100e-6, 5, 1)
        point = sample_at(r, 0.5)
        self.assertGreater(point["response"], 0)
        self.assertLess(point["response"], 5)

    def test_cursor_rejects_out_of_range(self):
        r = simulate_first_order("RC", 1000, 100e-6, 5, 1)
        with self.assertRaisesRegex(ValueError, "time range"):
            sample_at(r, 1.1)

    def test_invalid_component_values_rejected(self):
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            simulate_first_order("RC", 0, 100e-6, 5, 1)

    def test_invalid_model_rejected(self):
        with self.assertRaisesRegex(ValueError, "Choose RC or RL"):
            simulate_first_order("RLC", 1000, 1e-6, 5, 1)

    def test_waveform_export_and_report(self):
        r = simulate_first_order("RC", 1000, 100e-6, 5, 1)
        point = sample_at(r, .5)
        frame = waveform_frame(r)
        report = build_transient_report(r, point)
        self.assertEqual(len(frame), 501)
        self.assertIn("time_s", frame.columns)
        self.assertIn("Model limitations", report)


if __name__ == "__main__":
    unittest.main()
