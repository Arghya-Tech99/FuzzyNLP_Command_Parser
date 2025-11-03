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
    Ensures misspellings correctly map to the target word.
    """

    def test_misspelled_action_correction(self):
        # Test a misspelled action
        tokens = ['advence']
        expected = ['move']
        self.assertEqual(fuzzy_correct_sentence(tokens), expected)

    def test_misspelled_unit_correction(self):
        # Test a misspelled unit
        tokens = ['centimetars']
        expected = ['cm']
        # NOTE: This depends on how your REFERENCE_COMMAND_LEXICON maps the standard unit
        self.assertEqual(fuzzy_correct_sentence(tokens), expected)

    def test_unknown_word_no_correction(self):
        # Test a word that should not be corrected
        tokens = ['banana']
        expected = ['banana']
        self.assertEqual(fuzzy_correct_sentence(tokens), expected)


class TestParserLogic(unittest.TestCase):
    """
    PHASE 5, STEP 1: Unit Testing for Parser Logic (Phase 3)
    Ensures various sentence structures yield the correct Command Object.
    """

    # We must use the raw input string for generate_command_object as it relies on SpaCy

    def test_move_forward_command(self):
        # Test a standard movement command
        raw_input = "move forward 50 centimeters"
        fuzzy_tokens = ['move', 'forward', '50', 'cm']  # Simulated output from Phase 2

        result = generate_command_object(raw_input, fuzzy_tokens)

        self.assertEqual(result['command'], 'MOVE')
        self.assertEqual(result['value'], 50.0)
        self.assertEqual(result['unit'], 'cm')
        self.assertEqual(result['direction'], 'FORWARD')

    def test_rotate_left_command(self):
        # Test a rotation command
        raw_input = "turn left 45 degrees"
        fuzzy_tokens = ['rotate', 'left', '45', 'degrees']

        result = generate_command_object(raw_input, fuzzy_tokens)

        self.assertEqual(result['command'], 'ROTATE')
        self.assertEqual(result['value'], 45.0)
        self.assertEqual(result['direction'], 'LEFT')

    def test_simple_stop_command(self):
        # Test a simple action command
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