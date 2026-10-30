import unittest

from release2_components import (
    COMPONENTS, catalogue_summary, get_component, search_components,
    selection_checklist,
)


class ComponentIntelligenceTests(unittest.TestCase):
    def test_catalogue_has_unique_ids(self):
        ids = [item["id"] for item in COMPONENTS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 12)

    def test_search_finds_mosfet(self):
        results = search_components("MOSFET")
        self.assertTrue(any(item["id"] == "mosfet" for item in results))

    def test_family_filter(self):
        results = search_components("", "Semiconductors")
        self.assertTrue(results)
        self.assertTrue(all(item["family"] == "Semiconductors" for item in results))

    def test_component_profile_contains_selection_and_failure_guidance(self):
        item = get_component("electrolytic-capacitor")
        self.assertTrue(item["selection"])
        self.assertTrue(item["failure_modes"])
        self.assertTrue(item["verification"])

    def test_unknown_component_raises_key_error(self):
        with self.assertRaises(KeyError):
            get_component("not-a-real-part")

    def test_checklist_mentions_exact_datasheet(self):
        checklist = selection_checklist("op-amp")
        self.assertTrue(any("exact manufacturer's datasheet" in line for line in checklist))

    def test_catalogue_summary_lists_components(self):
        summary = catalogue_summary()
        self.assertIn("Power MOSFET", summary)
        self.assertIn("Operational amplifier", summary)


if __name__ == "__main__":
    unittest.main()
