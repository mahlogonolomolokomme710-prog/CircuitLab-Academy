import unittest

from release3_studio import solve_dc_network, _to_netlist, build_circuitjs_text, build_circuitjs_url


class Release3SolverTests(unittest.TestCase):
    def test_voltage_divider_midpoint(self):
        result = solve_dc_network([
            {"Ref":"V1","Type":"V","Node1":"N1","Node2":"0","Value":10},
            {"Ref":"R1","Type":"R","Node1":"N1","Node2":"N2","Value":1000},
            {"Ref":"R2","Type":"R","Node1":"N2","Node2":"0","Value":1000},
        ])
        self.assertAlmostEqual(result["node_voltages"]["N2"], 5.0, places=8)

    def test_resistor_current_and_power(self):
        result = solve_dc_network([
            {"Ref":"V1","Type":"V","Node1":"N1","Node2":"0","Value":10},
            {"Ref":"R1","Type":"R","Node1":"N1","Node2":"0","Value":1000},
        ])
        resistor = next(x for x in result["components"] if x["Reference"]=="R1")
        self.assertAlmostEqual(resistor["Current (A)"], .01)
        self.assertAlmostEqual(resistor["Power (W)"], .1)

    def test_negative_source_orientation(self):
        result = solve_dc_network([
            {"Ref":"V1","Type":"V","Node1":"0","Node2":"N1","Value":5},
            {"Ref":"R1","Type":"R","Node1":"N1","Node2":"0","Value":1000},
        ])
        self.assertAlmostEqual(result["node_voltages"]["N1"], -5)

    def test_floating_network_rejected(self):
        with self.assertRaisesRegex(ValueError, "ground"):
            solve_dc_network([{"Ref":"V1","Type":"V","Node1":"A","Node2":"B","Value":5},
                              {"Ref":"R1","Type":"R","Node1":"A","Node2":"B","Value":1000}])

    def test_singular_network_rejected(self):
        with self.assertRaisesRegex(ValueError, "singular"):
            solve_dc_network([{"Ref":"V1","Type":"V","Node1":"A","Node2":"0","Value":5},
                              {"Ref":"R1","Type":"R","Node1":"B","Node2":"0","Value":1000}])

    def test_duplicate_reference_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            solve_dc_network([{"Ref":"V1","Type":"V","Node1":"A","Node2":"0","Value":5},
                              {"Ref":"V1","Type":"R","Node1":"A","Node2":"0","Value":1000}])

    def test_netlist_export(self):
        net = _to_netlist([{"Ref":"V1","Type":"V","Node1":"N1","Node2":"0","Value":5}])
        self.assertIn("V1 N1 0 5", net)
        self.assertIn(".op", net)

    def test_circuitjs_export_contains_voltage_source_resistor_and_ground(self):
        circuit = build_circuitjs_text([
            {"Ref":"V1","Type":"V","Node1":"N1","Node2":"0","Value":5},
            {"Ref":"R1","Type":"R","Node1":"N1","Node2":"0","Value":1000},
        ])
        self.assertTrue(circuit.startswith("$ 1 "))
        self.assertIn("v ", circuit)
        self.assertIn("r ", circuit)
        self.assertIn("g ", circuit)
        self.assertTrue(circuit.endswith("\\n"))

    def test_circuitjs_url_encodes_circuit(self):
        url = build_circuitjs_url([
            {"Ref":"V1","Type":"V","Node1":"N1","Node2":"0","Value":5},
            {"Ref":"R1","Type":"R","Node1":"N1","Node2":"0","Value":1000},
        ])
        self.assertTrue(url.startswith("https://www.falstad.com/circuit/circuitjs.html?cct="))
        self.assertIn("%24", url)

    def test_circuitjs_export_requires_ground(self):
        with self.assertRaisesRegex(ValueError, "ground"):
            build_circuitjs_text([{"Ref":"R1","Type":"R","Node1":"A","Node2":"B","Value":1000}])


if __name__ == "__main__":
    unittest.main()
