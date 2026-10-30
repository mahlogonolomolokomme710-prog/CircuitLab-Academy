import unittest

from release2_simulation import analyze_measurements, parse_measurement_csv


class SimulationComparisonTests(unittest.TestCase):
    def test_percentage_error_and_tolerance(self):
        result = analyze_measurements([{
            "measurement": "Output voltage", "theoretical": "5", "simulated": "4.9",
            "unit": "V", "tolerance_pct": "3",
        }])
        row = result["results"][0]
        self.assertAlmostEqual(row["percentage_error"], -2.0)
        self.assertEqual(row["status"], "WITHIN TOLERANCE")

    def test_outside_tolerance(self):
        result = analyze_measurements([{
            "measurement": "Current", "theoretical": "0.01", "simulated": "0.008",
            "unit": "A", "tolerance_pct": "5",
        }])
        self.assertEqual(result["outside_tolerance"], 1)

    def test_zero_reference_requires_absolute_tolerance(self):
        result = analyze_measurements([{
            "measurement": "Offset", "theoretical": "0", "simulated": "0.02", "unit": "V",
        }])
        self.assertIsNone(result["results"][0]["percentage_error"])
        self.assertEqual(result["review"], 1)

    def test_zero_reference_uses_absolute_tolerance(self):
        result = analyze_measurements([{
            "measurement": "Offset", "theoretical": "0", "simulated": "0.02",
            "unit": "V", "tolerance_abs": "0.05",
        }])
        self.assertEqual(result["results"][0]["status"], "WITHIN TOLERANCE")

    def test_csv_parser_requires_columns(self):
        with self.assertRaises(ValueError):
            parse_measurement_csv("name,expected,observed\nVout,5,4.9")

    def test_csv_parser_reads_measurement_rows(self):
        rows = parse_measurement_csv("measurement,theoretical,simulated,unit\nVout,5,4.9,V\n")
        self.assertEqual(rows[0]["measurement"], "Vout")


if __name__ == "__main__":
    unittest.main()
