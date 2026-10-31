import unittest

from release4_lecturer import (
    add_assignment, add_class, add_student, new_workspace, record_submission,
)
from release4_analytics import (
    analytics_markdown, build_class_analytics, student_analytics_csv,
)


def make_workspace():
    data = add_class(new_workspace(), {
        "id": "class-a", "name": "Electronics Group A", "module": "Electronics 1",
        "cohort": "2026", "students": []
    })
    for sid, name in [("S1", "Student One"), ("S2", "Student Two"), ("S3", "Student Three")]:
        data = add_student(data, "class-a", {"id": sid, "name": name})
    rubric = [{"criterion": "Theory", "weight": 40}, {"criterion": "Design", "weight": 60}]
    for aid, title, due in [("a1", "DC Networks", "2026-10-20"), ("a2", "Power Supply", "2026-10-27")]:
        data = add_assignment(data, {
            "id": aid, "class_id": "class-a", "title": title, "brief": "Low-voltage task",
            "due_date": due, "rubric": rubric, "records": []
        })
    data = record_submission(data, "a1", {
        "student_id": "S1", "status": "Reviewed", "submitted_on": "2026-10-19",
        "marks": {"Theory": 30, "Design": 45}, "feedback": "Good."
    })
    data = record_submission(data, "a1", {
        "student_id": "S2", "status": "Late", "submitted_on": "2026-10-21",
        "marks": {"Theory": 0, "Design": 0}, "feedback": ""
    })
    data = record_submission(data, "a2", {
        "student_id": "S1", "status": "Reviewed", "submitted_on": "2026-10-26",
        "marks": {"Theory": 20, "Design": 20}, "feedback": "Revise design."
    })
    data = record_submission(data, "a2", {
        "student_id": "S2", "status": "Reviewed", "submitted_on": "2026-10-27",
        "marks": {"Theory": 35, "Design": 45}, "feedback": "Strong."
    })
    return data


class EngineeringAnalyticsTests(unittest.TestCase):
    def test_class_summary_counts_and_reviewed_average(self):
        result = build_class_analytics(make_workspace(), "class-a")
        self.assertEqual(result["student_count"], 3)
        self.assertEqual(result["assignment_count"], 2)
        self.assertEqual(result["reviewed_assessment_count"], 3)
        self.assertAlmostEqual(result["overall_reviewed_average"], (75 + 40 + 80) / 3)

    def test_unreviewed_and_missing_work_are_not_zero(self):
        result = build_class_analytics(make_workspace(), "class-a")
        student3 = next(x for x in result["students"] if x["student_id"] == "S3")
        self.assertIsNone(student3["reviewed_average_percent"])
        self.assertEqual(student3["not_received_or_unrecorded"], 2)
        student2 = next(x for x in result["students"] if x["student_id"] == "S2")
        self.assertEqual(student2["reviewed_average_percent"], 80)
        self.assertEqual(student2["late_records"], 1)

    def test_criterion_scores_normalised_to_criterion_maximum(self):
        result = build_class_analytics(make_workspace(), "class-a")
        by_name = {x["criterion"]: x for x in result["criteria"]}
        self.assertAlmostEqual(by_name["Theory"]["mean_percent_of_criterion"], (75 + 50 + 87.5) / 3)
        self.assertEqual(by_name["Theory"]["observations"], 3)

    def test_assignment_summaries_only_include_reviewed_marks(self):
        result = build_class_analytics(make_workspace(), "class-a")
        first = next(x for x in result["assignments"] if x["assignment"] == "DC Networks")
        self.assertEqual(first["reviewed"], 1)
        self.assertEqual(first["records_received"], 2)
        self.assertEqual(first["average_reviewed_mark"], 75)

    def test_missing_class_rejected(self):
        with self.assertRaises(ValueError):
            build_class_analytics(make_workspace(), "unknown")

    def test_empty_class_assignments_are_reported_without_division_error(self):
        data = add_class(new_workspace(), {"id": "empty", "name": "Empty", "students": []})
        result = build_class_analytics(data, "empty")
        self.assertIsNone(result["overall_reviewed_average"])
        self.assertEqual(result["assignments"], [])

    def test_csv_and_markdown_exports(self):
        result = build_class_analytics(make_workspace(), "class-a")
        csv_text = student_analytics_csv(result)
        report = analytics_markdown(result)
        self.assertIn("S1", csv_text)
        self.assertIn("Engineering performance overview", report)
        self.assertIn("not treated as a zero", report.lower())

    def test_low_average_flag_is_descriptive(self):
        data = make_workspace()
        data = record_submission(data, "a1", {
            "student_id": "S3", "status": "Reviewed", "submitted_on": "2026-10-20",
            "marks": {"Theory": 10, "Design": 10}, "feedback": ""
        })
        result = build_class_analytics(data, "class-a")
        student3 = next(x for x in result["students"] if x["student_id"] == "S3")
        self.assertEqual(student3["support_flag"], "Review low average")


if __name__ == "__main__":
    unittest.main()
