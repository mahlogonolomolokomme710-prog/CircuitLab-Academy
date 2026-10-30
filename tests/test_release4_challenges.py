import unittest

from release4_challenges import CHALLENGES, build_submission, evidence_completion, rubric_total


class DesignChallengeTests(unittest.TestCase):
    def test_five_challenges_available(self):
        self.assertEqual(len(CHALLENGES), 5)

    def test_every_rubric_totals_one_hundred(self):
        for challenge_id in CHALLENGES:
            with self.subTest(challenge=challenge_id):
                self.assertEqual(rubric_total(challenge_id), 100)

    def test_all_challenges_have_requirements_constraints_and_deliverables(self):
        for challenge_id, challenge in CHALLENGES.items():
            with self.subTest(challenge=challenge_id):
                self.assertTrue(challenge["requirements"])
                self.assertTrue(challenge["constraints"])
                self.assertTrue(challenge["deliverables"])
                self.assertTrue(challenge["milestones"])

    def test_evidence_completion_empty(self):
        result = evidence_completion("rc_timer", [])
        self.assertEqual(result["points"], 0)
        self.assertEqual(result["percentage"], 0)
        self.assertTrue(result["missing_categories"])

    def test_evidence_completion_full(self):
        challenge = CHALLENGES["555_oscillator"]
        result = evidence_completion("555_oscillator", list(challenge["rubric"]))
        self.assertEqual(result["points"], 100)
        self.assertEqual(result["percentage"], 100)

    def test_unknown_challenge_rejected(self):
        with self.assertRaises(ValueError):
            rubric_total("unknown")
        with self.assertRaises(ValueError):
            evidence_completion("unknown", [])

    def test_submission_contains_student_evidence_and_safety(self):
        text = build_submission("automatic_light", "Student A", "Electronics", {}, [], "Review reflection")
        self.assertIn("Student A", text)
        self.assertIn("Student evidence", text)
        self.assertIn("mains", text.lower())
        self.assertIn("Review reflection", text)

    def test_submission_labels_completeness_not_grade(self):
        text = build_submission("regulated_supply", "", "", {}, [], "")
        self.assertIn("not a technical grade", text.lower())
        self.assertIn("Evidence completeness review", text)


if __name__ == "__main__":
    unittest.main()
