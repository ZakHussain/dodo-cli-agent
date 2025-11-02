"""
Robot Controller - Phase 1
Wrapper around SO-101 controller for Doda Terminal.
Handles lazy connection and behavior execution.
"""

import sys
import time
from pathlib import Path


class RobotController:
    """
    Wrapper for SO-101 robot arm controller.
    Provides lazy connection and behavior execution for Doda.
    """

    def __init__(self, port: str = "COM7", calibration_file: str = None):
        """
        Initialize robot controller.

        Args:
            port: Serial port for robot
            calibration_file: Path to calibration JSON file
        """
        self.port = port
        self.calibration_file = calibration_file
        self.controller = None
        self.is_connected = False

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
            # Import preset execution
            from so101_control import execute_preset

            # Map behavior names to preset files
            behavior_map = {
                "greeting": "dodo_greeting",
                "head_bob": "dodo_head_bob",
                "curious": "dodo_head_bob",  # Alias
                "pleased": "dodo_pleased",
                "woo": "dodo_woo",
                "dismay": "dodo_dismay",
                "idle": "dodo_idle"
            }

            preset_name = behavior_map.get(behavior_name, behavior_name)

            # Execute behavior and time it
            start_time = time.time()
            success = execute_preset(self.controller, preset_name, **kwargs)
            duration = time.time() - start_time

            if success:
                return {
                    "success": True,
                    "duration": duration,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "duration": duration,
                    "error": f"Preset '{preset_name}' execution failed"
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
