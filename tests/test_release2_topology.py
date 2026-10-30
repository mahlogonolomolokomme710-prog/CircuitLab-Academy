import unittest

from release2_circuit_reader import parse_circuitjs
from release2_topology import analyze_topology


SERIES_DIVIDER = """$ 1 5.0E-6 10.2 50 5.0 50
v 64 160 64 320 0 0 40 5 0 0 0.5
r 64 160 160 160 0 1000
w 160 160 224 160 0
r 224 160 320 160 0 1000
w 320 160 320 320 0
w 320 320 64 320 0
g 64 320 64 352 0
"""

PARALLEL = """$ 1 5.0E-6 10.2 50 5.0 50
v 64 160 64 320 0 0 40 5 0 0 0.5
w 64 160 160 160 0
w 160 160 160 192 0
r 160 192 320 192 0 1000
w 160 192 160 288 0
r 160 288 320 288 0 1000
w 320 192 320 288 0
w 320 288 320 320 0
w 320 320 64 320 0
g 64 320 64 352 0
"""

RC = """$ 1 5.0E-6 10.2 50 5.0 50
v 64 160 64 320 0 0 40 5 0 0 0.5
r 64 160 160 160 0 10000
w 160 160 224 160 0
c 224 160 224 320 0 0.0001 0.001
w 224 320 64 320 0
g 64 320 64 352 0
"""


class TopologyRecognitionTests(unittest.TestCase):
    def interpret(self, text):
        return analyze_topology(parse_circuitjs(text))

    def test_series_resistors_are_recognized(self):
        result = self.interpret(SERIES_DIVIDER)
        self.assertTrue(any("series-resistor relationship" in x for x in result["findings"]))

    def test_voltage_divider_candidate_is_recognized(self):
        result = self.interpret(SERIES_DIVIDER)
        self.assertTrue(any("Voltage-divider candidate" in x for x in result["findings"]))

    def test_parallel_resistors_are_recognized(self):
        result = self.interpret(PARALLEL)
        self.assertTrue(any("parallel-resistor group" in x for x in result["findings"]))

    def test_rc_relationship_is_recognized(self):
        result = self.interpret(RC)
        self.assertTrue(any("RC network candidate" in x for x in result["findings"]))

    def test_interpretation_always_carries_a_caution(self):
        result = self.interpret(RC)
        self.assertTrue(result["warnings"])
        self.assertIn("heuristic", result["summary"].lower())


if __name__ == "__main__":
    unittest.main()
