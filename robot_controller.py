# STEP 1: Robot/API Abstraction Layer

class RobotController:
    """
    Acts as the interface between the NLP output (Command Object)
    and the simulated robot's actual control signals.
    """

    def __init__(self):
        # Initialize internal state variables for simulation feedback
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0
        self.gripper_state = 'open'

    def _update_state(self, dx=0, dy=0, da=0):
        """Internal helper to update the robot's simulated position."""
        self.x += dx
        self.y += dy
        self.angle += da

    def get_current_state(self) -> str:
        """Provides feedback on the robot's current position and state."""
        return f"Position: ({self.x:.2f}, {self.y:.2f}), Orientation: {self.angle:.2f} degrees, Gripper: {self.gripper_state}"

    # --- Standardized Control Methods (Corresponding to Phase 3 Actions) ---

    def move_robot(self, direction: str, value: float, unit: str) -> str:
        """
        Translates the robot based on distance and direction.
        (PHASE 4, STEP 2: Integration with Robot Simulation)
        """
        # Convert all distance values to a common unit (e.g., meters)
        if unit == 'cm':
            distance_m = value / 100.0
        elif unit == 'meter':
            distance_m = value
        else:
            return f"Error: Unit '{unit}' not supported for movement."

        # Simplified 2D movement simulation
        dx, dy = 0, 0
        if direction == 'FORWARD':
            dy = distance_m
        elif direction == 'BACKWARD':
            dy = -distance_m
        elif direction == 'RIGHT':
            dx = distance_m
        elif direction == 'LEFT':
            dx = -distance_m

        self._update_state(dx=dx, dy=dy)

        # Simulated Feedback
        return f"Simulated: Moving robot {direction} by {value} {unit}. New state: {self.get_current_state()}"

    def rotate_robot(self, angle: float, direction: str) -> str:
        """
        Rotates the robot by a specified angle in degrees.
        """
        # Assume angle is always in degrees for simplicity
        rotation = angle if direction == 'RIGHT' else -angle
        self._update_state(da=rotation)

        # Simulated Feedback
        return f"Simulated: Rotating robot {direction} by {angle} degrees. New angle: {self.angle:.2f}."

    def halt_robot(self) -> str:
        """Stops all simulated movement."""
        return "Simulated: Robot immediately halted."

    def grab_object(self) -> str:
        """Simulates closing the gripper."""
        self.gripper_state = 'closed'
        return "Simulated: Gripper closed. Object secured."


# STEP 3 & 4: Execution Logic and Feedback Mechanism

def execute_command(command_obj: dict, robot: RobotController) -> str:
    """
    The final interpreter function that executes the command object.

    Args:
        command_obj (dict): The standardized command dictionary from Phase 3.
        robot (RobotController): The instance of the robot controller.

    Returns:
        str: Feedback message to the user.
    """

    command = command_obj.get('command')

    # 1. Dispatch based on the primary command
    if command == 'MOVE':
        direction = command_obj.get('direction')
        value = command_obj.get('value')
        unit = command_obj.get('unit')

        # Check for required slots before execution (Robustness check)
        if not all([direction, value, unit]):
            return "Error: MOVE command missing direction, value, or unit."

        # Execute the method in the RobotController class
        return robot.move_robot(direction, value, unit)

    elif command == 'ROTATE':
        direction = command_obj.get('direction', 'RIGHT')  # Default direction if not specified
        value = command_obj.get('value')

        if not value:
            return "Error: ROTATE command missing angle value."

        return robot.rotate_robot(value, direction)

    elif command == 'STOP':
        return robot.halt_robot()

    elif command == 'GRAB':
        return robot.grab_object()

    else:
        return f"Error: Command '{command}' not recognized by the Robot Controller."


# --- Example Integration and Testing ---

if __name__ == "__main__":
    # Initialize the Robot Controller
    robot_instance = RobotController()
    print("Robot Controller Initialized.")
    print(f"Initial State: {robot_instance.get_current_state()}\n")

    # Example 1: Movement Command (Output of Phase 3)
    cmd1 = {'command': 'MOVE', 'direction': 'FORWARD', 'value': 20.0, 'unit': 'cm'}
    feedback1 = execute_command(cmd1, robot_instance)
    print(f"Command 1: {cmd1}")
    print(f"Feedback: {feedback1}\n")

    # Example 2: Rotation Command
    cmd2 = {'command': 'ROTATE', 'direction': 'RIGHT', 'value': 90.0, 'unit': 'degrees'}
    feedback2 = execute_command(cmd2, robot_instance)
    print(f"Command 2: {cmd2}")
    print(f"Feedback: {feedback2}\n")

    # Example 3: Unrecognized Unit (Error Handling)
    cmd3 = {'command': 'MOVE', 'direction': 'LEFT', 'value': 5.0, 'unit': 'yards'}
    feedback3 = execute_command(cmd3, robot_instance)
    print(f"Command 3: {cmd3}")
    print(f"Feedback: {feedback3}\n")

    # Example 4: Simple Action
    cmd4 = {'command': 'GRAB'}
    feedback4 = execute_command(cmd4, robot_instance)
    print(f"Command 4: {cmd4}")
    print(f"Feedback: {feedback4}\n")

    # Final State Check
    print(f"Final Robot State: {robot_instance.get_current_state()}")