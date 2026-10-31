import unittest
import json

from release4_lecturer import (
    add_assignment, add_class, add_student, assignment_csv, assignment_markdown,
    assignment_summary, import_roster_csv, new_workspace, parse_rubric_text,
    record_submission, validate_workspace, workspace_json,
)


def setup_workspace():
    workspace = add_class(new_workspace(), {
        "id": "class1", "name": "Electronics A", "module": "Electronics 1",
        "cohort": "2026", "students": []
    })
    workspace = add_student(workspace, "class1", {
        "id": "STU001", "name": "Example Student", "email": "student@example.com"
    })
    rubric = [{"criterion": "Theory", "weight": 40},
              {"criterion": "Design", "weight": 60}]
    workspace = add_assignment(workspace, {
        "id": "assign1", "class_id": "class1", "title": "DC circuit report",
        "brief": "Analyse a low-voltage circuit.", "due_date": "2026-11-15",
        "rubric": rubric, "records": []
    })
    return workspace


class LecturerWorkspaceTests(unittest.TestCase):
    def test_empty_workspace(self):
        result = validate_workspace(new_workspace())
        self.assertEqual(result["classes"], [])
        self.assertEqual(result["assignments"], [])

    def test_add_class_and_student(self):
        workspace = setup_workspace()
        self.assertEqual(len(workspace["classes"][0]["students"]), 1)

    def test_duplicate_student_id_rejected(self):
        workspace = setup_workspace()
        with self.assertRaises(ValueError):
            add_student(workspace, "class1", {"id": "stu001", "name": "Duplicate"})

    def test_roster_csv_import(self):
        workspace = add_class(new_workspace(), {"id": "class1", "name": "A", "students": []})
        result = import_roster_csv(workspace, "class1",
            "student_id,name,email\\nSTU001,Student One,one@example.com\\n")
        self.assertEqual(result["classes"][0]["students"][0]["name"], "Student One")

    def test_roster_csv_requires_columns(self):
        workspace = add_class(new_workspace(), {"id": "class1", "name": "A", "students": []})
        with self.assertRaises(ValueError):
            import_roster_csv(workspace, "class1", "id,full_name\\n1,Student\\n")

    def test_rubric_parser_and_total(self):
        rubric = parse_rubric_text("Theory | 40\\nDesign | 60")
        self.assertEqual(sum(x["weight"] for x in rubric), 100)

    def test_rubric_must_total_100(self):
        with self.assertRaises(ValueError):
            parse_rubric_text("Theory | 40\\nDesign | 50")

    def test_assignment_rejects_unknown_class(self):
        workspace = new_workspace()
        with self.assertRaises(ValueError):
            add_assignment(workspace, {"id": "a", "class_id": "missing", "title": "T",
                "due_date": "2026-11-15", "rubric": [{"criterion": "T", "weight": 100}], "records": []})

    def test_submission_marks_and_summary(self):
        workspace = setup_workspace()
        result = record_submission(workspace, "assign1", {
            "student_id": "STU001", "status": "Reviewed", "submitted_on": "2026-11-14",
            "marks": {"Theory": 35, "Design": 50}, "feedback": "Good analysis."
        })
        summary = assignment_summary(result, "assign1")
        self.assertEqual(summary["rows"][0]["marks"], 85)
        self.assertEqual(summary["average_percentage"], 85)

    def test_marks_cannot_exceed_rubric_weight(self):
        workspace = setup_workspace()
        with self.assertRaises(ValueError):
            record_submission(workspace, "assign1", {
                "student_id": "STU001", "status": "Reviewed", "submitted_on": "2026-11-14",
                "marks": {"Theory": 41, "Design": 50}, "feedback": ""
            })

    def test_record_replaces_existing_student_record(self):
        workspace = setup_workspace()
        first = {"student_id": "STU001", "status": "Received", "submitted_on": "2026-11-14",
                 "marks": {"Theory": 0, "Design": 0}, "feedback": ""}
        workspace = record_submission(workspace, "assign1", first)
        second = first | {"status": "Reviewed", "marks": {"Theory": 40, "Design": 60}}
        workspace = record_submission(workspace, "assign1", second)
        self.assertEqual(len(workspace["assignments"][0]["records"]), 1)
        self.assertEqual(assignment_summary(workspace, "assign1")["rows"][0]["marks"], 100)

    def test_unreviewed_record_has_no_published_percentage(self):
        workspace = setup_workspace()
        workspace = record_submission(workspace, "assign1", {
            "student_id": "STU001", "status": "Received", "submitted_on": "2026-11-14",
            "marks": {"Theory": 35, "Design": 50}, "feedback": ""
        })
        self.assertIsNone(assignment_summary(workspace, "assign1")["rows"][0]["percentage"])

    def test_exports(self):
        workspace = setup_workspace()
        workspace = record_submission(workspace, "assign1", {
            "student_id": "STU001", "status": "Reviewed", "submitted_on": "2026-11-14",
            "marks": {"Theory": 35, "Design": 50}, "feedback": "Good."
        })
        self.assertIn("STU001", assignment_csv(workspace, "assign1"))
        self.assertIn("DC circuit report", assignment_markdown(workspace, "assign1"))
        self.assertIn('"schema_version": 1', workspace_json(workspace))

    def test_json_round_trip(self):
        workspace = setup_workspace()
        restored = validate_workspace(json.loads(workspace_json(workspace)))
        self.assertEqual(restored, workspace)

    def test_reject_wrong_schema_and_invalid_date(self):
        with self.assertRaises(ValueError):
            validate_workspace({"schema_version": 2, "classes": [], "assignments": []})
        workspace = setup_workspace()
        bad = json.loads(workspace_json(workspace))
        bad["assignments"][0]["due_date"] = "not-a-date"
        with self.assertRaises(ValueError):
            validate_workspace(bad)


if __name__ == "__main__":
    unittest.main()
