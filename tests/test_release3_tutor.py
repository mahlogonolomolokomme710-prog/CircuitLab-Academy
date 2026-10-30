import unittest

from release3_tutor import review_project_evidence, build_tutor_context, TUTOR_PROMPTS
from release3_project_factory import PROJECTS


class Release39TutorTests(unittest.TestCase):
    def test_all_projects_have_socratic_prompts(self):
        self.assertEqual(set(TUTOR_PROMPTS), set(PROJECTS))
        self.assertTrue(all(len(items) >= 5 for items in TUTOR_PROMPTS.values()))

    def test_empty_evidence_scores_zero(self):
        result = review_project_evidence("led_driver")
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["percentage"], 0)
        self.assertEqual(len(result["missing"]), 7)

    def test_complete_evidence_scores_full_completeness(self):
        result = review_project_evidence(
            "regulated_supply",
            "5 V output at 100 mA with 1 V ripple target and defined low-line condition.",
            "C = I divided by ripple frequency times ripple voltage; units and assumptions are shown.",
            "Bridge diodes, reservoir capacitor and regulator selected with datasheet voltage current and thermal ratings.",
            "Annotated bridge, capacitor and regulator schematic with CircuitJS simulation and node observations.",
            "No-load and loaded voltage, ripple and temperature measured with units and compared with estimates.",
            "Full-wave rectification chosen because ripple frequency is twice supply frequency; deviations discussed.",
            "Isolated current-limited low-voltage source, power-off inspection and datasheet limits documented.",
        )
        self.assertEqual(result["percentage"], 100)
        self.assertEqual(result["score"], result["maximum"])

    def test_short_evidence_is_partial(self):
        result = review_project_evidence("rc_delay", requirements="Target delay is 5 seconds.")
        row = next(x for x in result["criteria"] if x["criterion"] == "Requirements and specifications")
        self.assertEqual(row["status"], "Develop")
        self.assertGreater(row["score"], 0)

    def test_project_specific_gap_detection(self):
        result = review_project_evidence("motor_pwm", requirements="PWM motor design")
        self.assertIn("stall current", result["domain_gaps"])
        self.assertTrue(any(x["item"] == "duty" and x["present"] for x in result["domain_checks"]))

    def test_unknown_project_rejected(self):
        with self.assertRaises(ValueError):
            review_project_evidence("unknown")

    def test_tutor_context_contains_project_and_question(self):
        context = build_tutor_context("astable_555", "Final year", "How is frequency calculated?", "RA=1k, RB=10k")
        self.assertIn("555 timer", context)
        self.assertIn("How is frequency calculated?", context)
        self.assertIn("RA=1k", context)

    def test_context_rejects_unknown_project(self):
        with self.assertRaises(ValueError):
            build_tutor_context("bad", "First year", "Question", "")
