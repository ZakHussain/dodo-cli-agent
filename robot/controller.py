"""
Robot Controller - Phase 1
Wrapper around SO-101 controller for Doda Terminal.
Handles lazy connection and behavior execution.
"""

import sys
import time
import importlib.util
from pathlib import Path


class RobotController:
    """
    Wrapper for SO-101 robot arm controller.
    Provides lazy connection and behavior execution for Doda.
    """

    def __init__(self, port: str = "COM8", calibration_file: str = None):
        """
        Initialize robot controller.

        Args:
            port: Serial port for robot (default COM8 for LeKiwi)
            calibration_file: Path to calibration JSON file (defaults to lekiwi-calibrated.json)
        """
        self.port = port

        # Use LeKiwi calibration file if none specified
        if calibration_file is None:
            calibration_file = str(Path(__file__).parent.parent / "calibration-files" / "lekiwi-calibrated.json")

        self.calibration_file = calibration_file
        self.controller = None
        self.is_connected = False
        self.current_rotation_degrees = 0  # Track base rotation

        # Add so101 directory to path for imports
        so101_path = Path(__file__).parent.parent.parent / "so101"
        if str(so101_path) not in sys.path:
            sys.path.insert(0, str(so101_path))

    def connect(self) -> bool:
        """
        Connect to the robot (lazy initialization).

        Returns:
            True if connected successfully
        """
        if self.is_connected:
            return True

        try:
            # Import SO101 controller
            from so101_control import SO101Controller, SO101Config

            # Create config
            config = SO101Config(
                port=self.port,
                calibration_file=self.calibration_file,
                disable_torque_on_disconnect=True
            )

            # Create and connect controller
            self.controller = SO101Controller(config)

            if not self.controller.connect(enable_torque=True, load_calibration=True):
                return False

            self.is_connected = True
            return True

        except Exception as e:
            print(f"Robot connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from robot."""
        if self.is_connected and self.controller:
            self.controller.disconnect()
            self.is_connected = False

    def execute_behavior(self, behavior_name: str, **kwargs) -> dict:
        """
        Execute a dodo behavior preset.

        Args:
            behavior_name: Name of the behavior (e.g., "greeting", "head_bob")
            **kwargs: Additional parameters for the behavior

        Returns:
            dict with keys: success (bool), duration (float), error (str)
        """
        # Ensure we're connected
        if not self.connect():
            return {
                "success": False,
                "duration": 0.0,
                "error": "Failed to connect to robot"
            }

        try:
            # Map behavior names to preset files
            behavior_map = {
                "greeting": "dodo_greeting",
                "head_bob": "dodo_head_bob",
                "curious": "dodo_head_bob",  # Alias
                "pleased": "dodo_pleased",  # Legacy - not used in game
                "woo": "dodo_woo",  # Win condition only
                "dismay": "dodo_dismay",
                "dies": "dodo_dies",  # Lose condition
                "idle": "dodo_idle"
            }

            preset_name = behavior_map.get(behavior_name, behavior_name)

            # Load preset from local presets directory
            presets_dir = Path(__file__).parent / "presets"
            preset_path = presets_dir / f"{preset_name}.py"

            if not preset_path.exists():
                return {
                    "success": False,
                    "duration": 0.0,
                    "error": f"Preset '{preset_name}' not found in {presets_dir}"
                }

            # Load the preset module
            spec = importlib.util.spec_from_file_location(f"preset_{preset_name}", preset_path)
            if spec is None or spec.loader is None:
                return {
                    "success": False,
                    "duration": 0.0,
                    "error": f"Failed to load preset '{preset_name}'"
                }

            preset_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(preset_module)

            if not hasattr(preset_module, 'execute'):
                return {
                    "success": False,
                    "duration": 0.0,
                    "error": f"Preset '{preset_name}' does not have an execute() function"
                }

            # Execute behavior and time it
            start_time = time.time()
            preset_module.execute(self.controller, **kwargs)
            duration = time.time() - start_time

            return {
                "success": True,
                "duration": duration,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "duration": 0.0,
                "error": str(e)
            }

    def get_available_behaviors(self) -> list:
        """
        Get list of available dodo behaviors.

        Returns:
            List of behavior names
        """
        return [
            "greeting",
            "head_bob",
            "curious",
            "pleased",
            "woo",
            "dismay",
            "idle"
        ]

    def rotate_base(self, degrees: float, direction: str = "auto") -> dict:
        """
        Rotate the LeKiwi base by specified degrees and return to start.

        Args:
            degrees: Number of degrees to rotate (positive values)
            direction: "left", "right", or "auto" (auto chooses shortest path)

        Returns:
            dict with keys: success (bool), actual_degrees (float), error (str)
        """
        # Ensure we're connected
        if not self.connect():
            return {
                "success": False,
                "actual_degrees": 0.0,
                "error": "Failed to connect to robot"
            }

        try:
            # Calibration: approximately 1.5 seconds per 90 degrees at speed 400
            SECONDS_PER_DEGREE = 1.5 / 90.0
            ROTATION_SPEED = 400

            # Determine direction
            if direction == "auto":
                # For now, use left as default
                direction = "left"

            # Calculate duration
            duration = abs(degrees) * SECONDS_PER_DEGREE

            # Set wheel velocities for rotation
            # Left rotation: left wheel back, right wheel forward
            # Right rotation: left wheel forward, right wheel back
            if direction == "left":
                # Counter-clockwise rotation
                velocities = [-ROTATION_SPEED, -ROTATION_SPEED, -ROTATION_SPEED]
            else:
                # Clockwise rotation
                velocities = [ROTATION_SPEED, ROTATION_SPEED, ROTATION_SPEED]

            # Wheel motor IDs are 7, 8, 9
            wheel_ids = [7, 8, 9]

            # Rotate
            for motor_id, velocity in zip(wheel_ids, velocities):
                self.controller.set_goal_velocity(motor_id, velocity)

            time.sleep(duration)

            # Stop wheels
            for motor_id in wheel_ids:
                self.controller.set_goal_velocity(motor_id, 0)

            time.sleep(0.1)  # Brief pause

            # Return to start position (rotate back)
            return_velocities = [-v for v in velocities]

            for motor_id, velocity in zip(wheel_ids, return_velocities):
                self.controller.set_goal_velocity(motor_id, velocity)

            time.sleep(duration)

            # Stop wheels
            for motor_id in wheel_ids:
                self.controller.set_goal_velocity(motor_id, 0)

            return {
                "success": True,
                "actual_degrees": degrees,
                "error": None
            }

        except Exception as e:
            # Stop wheels on error
            try:
                for motor_id in [7, 8, 9]:
                    self.controller.set_goal_velocity(motor_id, 0)
            except:
                pass

            return {
                "success": False,
                "actual_degrees": 0.0,
                "error": str(e)
            }

    def capture_joint_positions(self) -> dict:
        """
        Capture current positions of all joints.

        Returns:
            dict with joint names as keys and positions as values
            (normalized -1.0 to 1.0 for arm, velocities for wheels)
        """
        # Ensure we're connected
        if not self.connect():
            return {
                "success": False,
                "positions": {},
                "error": "Failed to connect to robot"
            }

        try:
            positions = {}

            # Read all motor positions
            # Arm motors: 1-6
            arm_motor_names = [
                "shoulder_pan",
                "shoulder_lift",
                "elbow_flex",
                "wrist_flex",
                "wrist_roll",
                "gripper"
            ]

            for motor_id, name in enumerate(arm_motor_names, start=1):
                try:
                    # Get normalized position (-1.0 to 1.0)
                    pos = self.controller.get_normalized_position(motor_id)
                    positions[name] = round(pos, 3)
                except Exception as e:
                    positions[name] = None
                    print(f"Warning: Could not read {name}: {e}")

            # Wheel motors: 7-9 (velocities, not positions)
            wheel_names = ["wheel_left", "wheel_back", "wheel_right"]
            for motor_id, name in enumerate(wheel_names, start=7):
                try:
                    # For wheels, we can read current velocity or just set to 0 (stopped)
                    positions[name] = 0  # Wheels should be stopped when capturing
                except Exception as e:
                    positions[name] = None
                    print(f"Warning: Could not read {name}: {e}")

            return {
                "success": True,
                "positions": positions,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "positions": {},
                "error": str(e)
            }

    def disable_all_torques(self):
        """
        Disable all motor torques - used for lose condition.
        Doda goes limp.
        """
        if not self.is_connected or not self.controller:
            return

        try:
            # Disable torque for all motors (1-9)
            for motor_id in range(1, 10):
                try:
                    self.controller.disable_torque(motor_id)
                except:
                    pass

            print("All torques disabled - Doda is now limp")

        except Exception as e:
            print(f"Error disabling torques: {e}")
