import unittest
from release4_university import LESSONS, COMPONENTS, get_lesson, search_knowledge, build_lesson_markdown, build_component_markdown

class Release40UniversityTests(unittest.TestCase):
    def test_curriculum_has_eight_complete_lessons(self):
        self.assertEqual(len(LESSONS), 8)
        for lesson in LESSONS.values():
            self.assertTrue(lesson["outcomes"])
            self.assertTrue(lesson["content"])
            self.assertTrue(lesson["equations"])
            self.assertTrue(lesson["questions"])
            self.assertEqual(len(lesson["questions"]), 2)

    def test_component_library_has_fifteen_entries(self):
        self.assertGreaterEqual(len(COMPONENTS), 15)
        required = {"family","function","principle","selection","failure","verification","caution"}
        for item in COMPONENTS.values():
            self.assertTrue(required.issubset(item))

    def test_unknown_lesson_rejected(self):
        with self.assertRaises(ValueError):
            get_lesson("not_a_lesson")

    def test_search_finds_lesson_and_component(self):
        self.assertTrue(any(x["kind"] == "Lesson" for x in search_knowledge("ripple", "Lessons")))
        self.assertTrue(any(x["kind"] == "Component" for x in search_knowledge("MOSFET", "Components")))

    def test_search_empty_query_returns_empty(self):
        self.assertEqual(search_knowledge("   "), [])

    def test_lesson_export_contains_equations_and_answers(self):
        text = build_lesson_markdown("dc_fundamentals")
        self.assertIn("V = IR", text)
        self.assertIn("Answer:", text)
        self.assertIn("Worked example", text)

    def test_component_export_contains_safety_caution(self):
        text = build_component_markdown("Capacitor")
        self.assertIn("Selection parameters", text)
        self.assertIn("Caution", text)

    def test_unknown_component_rejected(self):
        with self.assertRaises(ValueError):
            build_component_markdown("Unobtainium")

if __name__ == "__main__":
    unittest.main()
