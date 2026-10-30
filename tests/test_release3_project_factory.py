import unittest

from release3_project_factory import (
    PROJECTS, calculate_project, build_project_pack, build_project_report
)


class EngineeringProjectFactoryTests(unittest.TestCase):
    def test_catalog_contains_six_complete_templates(self):
        self.assertEqual(len(PROJECTS), 6)
        for project_id, template in PROJECTS.items():
            self.assertTrue(template["requirements"], project_id)
            self.assertTrue(template["bom"], project_id)
            self.assertTrue(template["workflow"], project_id)
            self.assertTrue(template["tests"], project_id)
            self.assertEqual(sum(template["rubric"].values()), 100)

    def test_led_driver_selects_standard_resistor_above_minimum(self):
        result = calculate_project("led_driver", {
            "supply_v": 5, "led_vf": 2, "target_ma": 10
        })
        self.assertGreaterEqual(result["selected_e12_ohm"], result["minimum_resistance_ohm"])
        self.assertAlmostEqual(result["actual_current_ma"], 3 / result["selected_e12_ohm"] * 1000)

    def test_led_driver_rejects_forward_voltage_at_or_above_supply(self):
        with self.assertRaises(ValueError):
            calculate_project("led_driver", {"supply_v": 2, "led_vf": 2, "target_ma": 10})

    def test_ldr_divider_has_expected_light_dark_response(self):
        result = calculate_project("ldr_light", {
            "supply_v": 5, "ldr_bright_ohm": 1000,
            "ldr_dark_ohm": 100000, "fixed_ohm": 10000
        })
        self.assertGreater(result["bright_output_v"], result["dark_output_v"])

    def test_rc_delay_calculates_one_tau_at_632_percent(self):
        result = calculate_project("rc_delay", {
            "resistance_ohm": 100000, "capacitance_uf": 100,
            "supply_v": 5, "threshold_fraction": 0.632
        })
        self.assertAlmostEqual(result["time_constant_s"], 10.0)
        self.assertAlmostEqual(result["estimated_delay_s"], 10.0, delta=0.02)

    def test_rc_delay_rejects_invalid_threshold(self):
        with self.assertRaises(ValueError):
            calculate_project("rc_delay", {"threshold_fraction": 1})

    def test_motor_pwm_average_voltage(self):
        result = calculate_project("motor_pwm", {
            "supply_v": 12, "duty_percent": 25, "motor_current_a": 2
        })
        self.assertAlmostEqual(result["ideal_average_voltage_v"], 3)
        self.assertAlmostEqual(result["ideal_average_input_power_w"], 6)

    def test_motor_pwm_rejects_out_of_range_duty(self):
        with self.assertRaises(ValueError):
            calculate_project("motor_pwm", {"duty_percent": 101})

    def test_555_astable_frequency_and_duty_are_positive(self):
        result = calculate_project("astable_555", {
            "ra_ohm": 10000, "rb_ohm": 47000, "capacitance_nf": 10
        })
        self.assertGreater(result["frequency_hz"], 0)
        self.assertGreater(result["duty_percent"], 50)
        self.assertLess(result["duty_percent"], 100)

    def test_power_supply_load_estimates(self):
        result = calculate_project("regulated_supply", {
            "output_v": 5, "load_current_ma": 100, "ripple_target_v": 1
        })
        self.assertAlmostEqual(result["load_power_w"], 0.5)
        self.assertAlmostEqual(result["equivalent_load_ohm"], 50)

    def test_pack_supports_custom_title_and_level(self):
        pack = build_project_pack("led_driver", {}, "My LED project", "Advanced")
        self.assertEqual(pack["title"], "My LED project")
        self.assertEqual(pack["student_level"], "Advanced")

    def test_report_contains_bom_workflow_rubric_and_safety(self):
        pack = build_project_pack("ldr_light", {})
        report = build_project_report(pack)
        for section in ("Preliminary bill of materials", "Design and build workflow",
                        "Verification and test plan", "Assessment rubric",
                        "Safety and limitations"):
            self.assertIn(section, report)


if __name__ == "__main__":
    unittest.main()
