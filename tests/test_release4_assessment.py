import unittest
from release4_assessment import ASSESSMENTS, LAB_MANUALS, grade_assessment, build_assessment_report, build_lab_manual

class Release42AssessmentTests(unittest.TestCase):
    def test_assessment_banks_have_four_questions_each(self):
        self.assertGreaterEqual(len(ASSESSMENTS),4)
        for questions in ASSESSMENTS.values():
            self.assertEqual(len(questions),4)
            self.assertTrue(all(q["marks"]>0 and q["options"] for q in questions))

    def test_all_correct_answers_score_full_marks(self):
        for topic, questions in ASSESSMENTS.items():
            answers={str(i):q["options"][q["answer"]] for i,q in enumerate(questions)}
            result=grade_assessment(topic,answers)
            self.assertEqual(result["percentage"],100)
            self.assertEqual(result["earned"],result["maximum"])

    def test_all_wrong_answers_score_zero(self):
        for topic, questions in ASSESSMENTS.items():
            answers={str(i):q["options"][(q["answer"]+1)%len(q["options"])] for i,q in enumerate(questions)}
            self.assertEqual(grade_assessment(topic,answers)["earned"],0)

    def test_unanswered_questions_are_marked(self):
        topic=next(iter(ASSESSMENTS))
        result=grade_assessment(topic,{})
        self.assertTrue(all(d["selected"]=="Not answered" for d in result["details"]))
        self.assertEqual(result["earned"],0)

    def test_unknown_assessment_rejected(self):
        with self.assertRaises(ValueError):
            grade_assessment("Unknown",{})

    def test_assessment_report_has_feedback(self):
        topic=next(iter(ASSESSMENTS))
        q=ASSESSMENTS[topic][0]
        result=grade_assessment(topic,{"0":q["options"][q["answer"]]})
        report=build_assessment_report(result)
        self.assertIn("Correct answer",report)
        self.assertIn("Explanation",report)

    def test_four_lab_manuals_are_complete(self):
        self.assertGreaterEqual(len(LAB_MANUALS),4)
        for manual in LAB_MANUALS.values():
            for key in ("purpose","outcomes","apparatus","procedure","tables","analysis","safety"):
                self.assertTrue(manual[key])

    def test_lab_manual_export_contains_procedure_and_safety(self):
        title,manual=next(iter(LAB_MANUALS.items()))
        report=build_lab_manual(title,manual,"Student A","2026-10-30")
        self.assertIn("## Procedure",report)
        self.assertIn("## Safety",report)
        self.assertIn("Student A",report)
        self.assertIn("|",report)

if __name__ == "__main__":
    unittest.main()
