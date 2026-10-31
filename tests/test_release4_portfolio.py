import unittest
import json

from release4_portfolio import (
    add_entry, new_portfolio, portfolio_csv, portfolio_json,
    portfolio_markdown, portfolio_progress, validate_portfolio,
)


def sample_entry():
    return {"id": "abc123", "title": "RC timing experiment", "kind": "Practical laboratory",
            "module": "Electronics 1", "date": "2026-10-31", "status": "Completed",
            "skills": "Circuit analysis, Oscilloscope", "summary": "Measured capacitor charging.",
            "evidence": "RC_scope_trace.csv", "reflection": "Consider probe loading."}


class StudentPortfolioTests(unittest.TestCase):
    def test_empty_portfolio(self):
        p = new_portfolio()
        self.assertEqual(portfolio_progress(p)["total"], 0)

    def test_add_entry_without_mutating_original(self):
        p = new_portfolio()
        updated = add_entry(p, sample_entry())
        self.assertEqual(len(p["entries"]), 0)
        self.assertEqual(len(updated["entries"]), 1)

    def test_progress_counts_status_and_skills(self):
        p = add_entry(new_portfolio(), sample_entry())
        result = portfolio_progress(p)
        self.assertEqual(result["completed"], 1)
        self.assertIn("Oscilloscope", result["skills"])

    def test_markdown_contains_entry_and_self_reported_notice(self):
        report = portfolio_markdown(add_entry(new_portfolio(), sample_entry()))
        self.assertIn("RC timing experiment", report)
        self.assertIn("self-reported", report)

    def test_csv_contains_entry(self):
        data = portfolio_csv(add_entry(new_portfolio(), sample_entry()))
        self.assertIn("RC timing experiment", data)
        self.assertIn("Practical laboratory", data)

    def test_json_round_trip(self):
        p = add_entry(new_portfolio(), sample_entry())
        restored = validate_portfolio(json.loads(portfolio_json(p)))
        self.assertEqual(restored, p)

    def test_rejects_wrong_schema(self):
        with self.assertRaises(ValueError):
            validate_portfolio({"schema_version": 2, "entries": [], "profile": {}})

    def test_rejects_missing_title(self):
        entry = sample_entry()
        entry["title"] = ""
        with self.assertRaises(ValueError):
            add_entry(new_portfolio(), entry)

    def test_rejects_invalid_status(self):
        entry = sample_entry()
        entry["status"] = "Passed"
        with self.assertRaises(ValueError):
            add_entry(new_portfolio(), entry)

    def test_rejects_more_than_250_entries(self):
        p = new_portfolio()
        p["entries"] = [sample_entry() | {"id": str(i)} for i in range(251)]
        with self.assertRaises(ValueError):
            validate_portfolio(p)


if __name__ == "__main__":
    unittest.main()
