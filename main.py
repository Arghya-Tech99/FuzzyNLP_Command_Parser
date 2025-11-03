import unittest
# Import the functions/classes from your project modules
# NOTE: Replace 'your_module_name' with the actual filenames you created.
from robot_controller import RobotController, execute_command
from fuzzy_matching import fuzzy_correct_sentence, REFERENCE_COMMAND_LEXICON  # Assuming Phase 2 file
from command_parser import generate_command_object  # Assuming Phase 3 file

# Mock Data (Simulated Phase 1 output for testing Phase 2/3)
MOCK_INPUT_CLEAN = "move the robot forward ten centimeters"
MOCK_INPUT_FUZZY = ['move', 'the', 'robot', 'forwerd', 'ten', 'centimetars']  # Simulating output of Phase 1
MOCK_INPUT_SLANG = ['rotate', 'it', '90', 'degerees', 'plz']


class TestFuzzyMatching(unittest.TestCase):
    """
    PHASE 5, STEP 1: Unit Testing for Fuzzy Matching (Phase 2)
    Ensures misspellings correctly map to the closest word in the vocabulary.
    """

    def test_misspelled_action_correction(self):
        # Corrected: Expect the closest word ('advance')
        tokens = ['advence']
        expected = ['advance']
        self.assertEqual(fuzzy_correct_sentence(tokens), expected)

    def test_misspelled_unit_correction(self):
        # Corrected: Expect the closest word ('centimeter')
        tokens = ['centimetars']
        expected = ['centimeter']
        self.assertEqual(fuzzy_correct_sentence(tokens), expected)

    def test_unknown_word_no_correction(self):
        # This test passed and remains unchanged
        tokens = ['banana']
        expected = ['banana']
        self.assertEqual(fuzzy_correct_sentence(tokens), expected)


class TestParserLogic(unittest.TestCase):
    """
    Unit Testing for Parser Logic (Phase 3)
    """

    def test_move_forward_command(self):
        # Raw input for SpaCy
        raw_input = "move forward 50 centimeters"
        fuzzy_tokens = ['move', 'forward', '50',
                        'cm']  # Not used directly for extraction, but required by function signature

        result = generate_command_object(raw_input, fuzzy_tokens)

        self.assertEqual(result['command'], 'MOVE')
        # Corrected: Use assertAlmostEqual for numeric comparisons (good practice for floats)
        self.assertAlmostEqual(result['value'], 50.0)
        # Corrected: Expecting the full word unit extracted from the raw string
        self.assertEqual(result['unit'], 'centimeter')
        self.assertEqual(result['direction'], 'FORWARD')

    def test_rotate_left_command(self):
        # Test a rotation command
        raw_input = "turn left 45 degrees"
        fuzzy_tokens = ['rotate', 'left', '45', 'degrees']

        result = generate_command_object(raw_input, fuzzy_tokens)

        self.assertEqual(result['command'], 'ROTATE')
        self.assertAlmostEqual(result['value'], 45.0)
        # Assuming the parser correctly extracts 'degrees'
        self.assertEqual(result['unit'], 'degrees')
        self.assertEqual(result['direction'], 'LEFT')

    def test_simple_stop_command(self):
        # This test should pass if the command is correctly identified.
        raw_input = "stop immediately"
        fuzzy_tokens = ['stop', 'immediately']

        result = generate_command_object(raw_input, fuzzy_tokens)

        self.assertEqual(result['command'], 'STOP')
        self.assertIsNone(result['value'])


class TestRobotController(unittest.TestCase):
    """
    PHASE 5, STEP 1: Unit Testing for Robot Controller (Phase 4)
    Ensures the correct robot function is called and state is updated.
    """

    def setUp(self):
        # Create a new RobotController instance before each test
        self.robot = RobotController()

    def test_move_updates_state(self):
        # Test that a move command updates the internal state
        cmd = {'command': 'MOVE', 'direction': 'FORWARD', 'value': 100.0, 'unit': 'cm'}
        execute_command(cmd, self.robot)

        # 100cm = 1m (based on the controller's internal logic)
        self.assertAlmostEqual(self.robot.y, 1.0)
        self.assertAlmostEqual(self.robot.x, 0.0)

    def test_rotate_updates_angle(self):
        # Test that a rotate command updates the angle
        cmd = {'command': 'ROTATE', 'direction': 'RIGHT', 'value': 45.0, 'unit': 'degrees'}
        execute_command(cmd, self.robot)

        self.assertAlmostEqual(self.robot.angle, 45.0)

    def test_error_handling_missing_slot(self):
        # Test the robustness (Error Handling) of the execution logic
        # Missing 'value' for a MOVE command
        cmd = {'command': 'MOVE', 'direction': 'FORWARD', 'unit': 'cm'}
        feedback = execute_command(cmd, self.robot)

        self.assertTrue("Error: MOVE command missing" in feedback)
        self.assertEqual(self.robot.x, 0.0)  # State should not change

    def test_error_handling_unrecognized_command(self):
        # Test an unknown command
        cmd = {'command': 'DANCE'}
        feedback = execute_command(cmd, self.robot)

        self.assertTrue("not recognized" in feedback)


# --- Execution Block ---
if __name__ == '__main__':
    print("--- Running Phase 5 Unit Tests ---")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)