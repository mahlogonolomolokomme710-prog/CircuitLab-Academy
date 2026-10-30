import math
import unittest
from release4_visual_engine import (
    ohmic_circuit, voltage_drop_series, diode_current, diode_curve,
    transistor_switch, capacitor_response, build_visual_lab_report
)

class Release43VisualEngineTests(unittest.TestCase):
    def test_ohmic_circuit_current_and_power(self):
        result=ohmic_circuit(12,1000)
        self.assertAlmostEqual(result["current_a"],0.012)
        self.assertAlmostEqual(result["power_w"],0.144)

    def test_series_drops_sum_to_source_and_current_is_shared(self):
        result=voltage_drop_series(12,[1000,2000])
        self.assertAlmostEqual(sum(x["drop_v"] for x in result),12)
        self.assertAlmostEqual(result[0]["current_a"],result[1]["current_a"])
        self.assertAlmostEqual(result[0]["drop_v"],4)
        self.assertAlmostEqual(result[1]["drop_v"],8)

    def test_series_rejects_invalid_network(self):
        for source,values in [(-1,[100]),(5,[]),(5,[0]),(5,[float("inf")])]:
            with self.subTest(source=source,values=values), self.assertRaises(ValueError):
                voltage_drop_series(source,values)

    def test_diode_zero_voltage_and_forward_current(self):
        self.assertAlmostEqual(diode_current(0),0)
        self.assertGreater(diode_current(0.65),diode_current(0.2))

    def test_diode_reverse_current_is_small_and_negative(self):
        current=diode_current(-0.2)
        self.assertLess(current,0)
        self.assertGreater(current,-1e-9)

    def test_diode_curve_has_requested_points(self):
        curve=diode_curve(-0.2,0.7,51)
        self.assertEqual(len(curve),51)
        self.assertAlmostEqual(curve[0]["voltage_v"],-0.2)
        self.assertAlmostEqual(curve[-1]["voltage_v"],0.7)

    def test_diode_rejects_invalid_parameters(self):
        with self.assertRaises(ValueError):
            diode_current(0.2,0)
        with self.assertRaises(ValueError):
            diode_curve(1,0,10)

    def test_transistor_on_and_off_states(self):
        on=transistor_switch(9,100,True)
        off=transistor_switch(9,100,False)
        self.assertTrue(on["on"])
        self.assertAlmostEqual(on["load_current_a"],0.088)
        self.assertEqual(off["load_current_a"],0)
        self.assertEqual(off["load_voltage_v"],0)

    def test_transistor_rejects_invalid_load(self):
        with self.assertRaises(ValueError):
            transistor_switch(9,0,True)

    def test_capacitor_response_initial_and_one_tau(self):
        data=capacitor_response(5,10000,100e-6,points=101)
        self.assertAlmostEqual(data[0]["capacitor_voltage_v"],0)
        self.assertAlmostEqual(data[20]["capacitor_voltage_v"],5*(1-math.exp(-1)),places=5)
        self.assertAlmostEqual(data[-1]["time_s"],5)

    def test_capacitor_response_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            capacitor_response(5,0,1e-6)
        with self.assertRaises(ValueError):
            capacitor_response(-1,1000,1e-6)

    def test_report_identifies_model_values(self):
        report=build_visual_lab_report("Test lab",{"current_a":0.01})
        self.assertIn("Test lab",report)
        self.assertIn("not live CircuitJS",report)
        self.assertIn("Current A",report)

if __name__ == "__main__":
    unittest.main()
