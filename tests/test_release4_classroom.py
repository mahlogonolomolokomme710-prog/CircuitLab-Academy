import math
import unittest
from release4_classroom import CLASSROOMS, divider_result, rc_waveform, quiz_feedback

class Release41ClassroomTests(unittest.TestCase):
    def test_four_classrooms_have_guided_steps_and_questions(self):
        self.assertEqual(len(CLASSROOMS), 4)
        for lesson in CLASSROOMS.values():
            self.assertGreaterEqual(len(lesson["steps"]), 4)
            self.assertTrue(lesson["equations"])
            self.assertTrue(lesson["questions"])

    def test_unloaded_equal_divider(self):
        result = divider_result(12, 1000, 1000)
        self.assertAlmostEqual(result["unloaded_v"], 6)
        self.assertAlmostEqual(result["loaded_v"], 6)

    def test_loaded_divider_drops_output(self):
        result = divider_result(12, 1000, 1000, 1000)
        self.assertAlmostEqual(result["loaded_v"], 4)
        self.assertLess(result["loaded_v"], result["unloaded_v"])

    def test_divider_rejects_invalid_values(self):
        for args in [(12,0,1000,None),(12,1000,-1,None),(12,1000,1000,0),(-1,1000,1000,None)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                divider_result(*args)

    def test_rc_time_constant_and_initial_final_values(self):
        data=rc_waveform(10000,100e-6,5)
        self.assertEqual(len(data),101)
        self.assertAlmostEqual(data[0]["voltage_v"],0)
        self.assertAlmostEqual(data[20]["voltage_v"],5*(1-math.exp(-1)),places=5)
        self.assertAlmostEqual(data[-1]["voltage_v"],5*(1-math.exp(-5)),places=5)

    def test_rc_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            rc_waveform(0,1e-6,5)
        with self.assertRaises(ValueError):
            rc_waveform(1000,1e-6,-5)

    def test_quiz_feedback_correct_and_incorrect(self):
        q=CLASSROOMS["ohms_law"]["questions"][0]
        self.assertTrue(quiz_feedback(q,"4 mA")["correct"])
        self.assertFalse(quiz_feedback(q,"36 mA")["correct"])

    def test_quiz_rejects_unknown_option(self):
        with self.assertRaises(ValueError):
            quiz_feedback(CLASSROOMS["ohms_law"]["questions"][0],"Maybe")

if __name__ == "__main__":
    unittest.main()
