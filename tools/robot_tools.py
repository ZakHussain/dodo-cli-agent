"""
Robot tools for Doda Agent - Phase 2
Provides tools for behavior execution, vision, preferences, base rotation, and position capture
"""

import json
from typing import Any, Callable
from pathlib import Path
from anthropic.types import ToolParam


def create_robot_tools(robot_controller, camera_manager, preferences_system) -> tuple[list[ToolParam], dict[str, Callable]]:
    """
    Create tool definitions and handlers for Doda agent

    Args:
        robot_controller: RobotController instance
        camera_manager: CameraManager instance
        preferences_system: PreferencesSystem instance

    Returns:
        Tuple of (tool_definitions, tool_handlers)
    """

    # Tool 1: Execute Dodo Behavior
    execute_behavior_def = {
        "name": "execute_dodo_behavior",
        "description": "Execute a physical behavior on the Dodo robot. Use this to express emotions through movement.",
        "input_schema": {
            "type": "object",
            "properties": {
                "behavior_name": {
                    "type": "string",
                    "enum": ["greeting", "head_bob", "curious", "pleased", "woo", "dismay", "idle"],
                    "description": "The behavior to execute. greeting=wave, head_bob/curious=look around, pleased=stretch neck forward, woo=excited celebration, dismay=sad droop, idle=subtle breathing"
                },
                "reason": {
                    "type": "string",
                    "description": "Why you're executing this behavior (for logging)"
                }
            },
            "required": ["behavior_name", "reason"]
        }
    }

    def handle_execute_behavior(behavior_name: str, reason: str) -> dict:
        """Execute a dodo behavior"""
        result = robot_controller.execute_behavior(behavior_name)

        return {
            "success": result["success"],
            "behavior": behavior_name,
            "reason": reason,
            "duration": result.get("duration", 0.0),
            "error": result.get("error")
        }

    # Tool 2: Capture and Analyze Gift
    capture_gift_def = {
        "name": "capture_and_analyze_gift",
        "description": "Capture a photo of the gift in front of you and analyze what it is. Returns object description and calculates affinity score based on your preferences.",
        "input_schema": {
            "type": "object",
            "properties": {
                "save_photo": {
                    "type": "boolean",
                    "description": "Whether to save the photo to disk (default true)",
                    "default": True
                }
            },
            "required": []
        }
    }

    def handle_capture_gift(save_photo: bool = True) -> dict:
        """Capture and analyze gift using two-step vision process"""
        # Capture frame
        frame = camera_manager.capture_frame()

        if frame is None:
            return {
                "success": False,
                "error": "Failed to capture image from camera",
                "gift_analysis": None,
                "affinity_score": 0,
                "affinity_reason": ""
            }

        # Save photo if requested
        photo_path = None
        timestamp = None
        if save_photo:
            photo_dir = Path("game/gift_photos")
            photo_dir.mkdir(parents=True, exist_ok=True)

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            photo_path = photo_dir / f"gift_{timestamp}.jpg"

            camera_manager.save_frame(str(photo_path))

        # TWO-STEP VISION PROCESS
        from tools.vision_helper import analyze_image, evaluate_preferences

        # STEP 1: Analyze image with Vision API
        print("  [Step 1/2] Analyzing image...")
        gift_analysis = analyze_image(frame)

        # STEP 2: Evaluate based on preferences
        print("  [Step 2/2] Evaluating preferences...")
        preferences = preferences_system.get_all_preferences()
        evaluation = evaluate_preferences(gift_analysis, preferences)

        affinity_score = evaluation["affinity_score"]
        affinity_reason = evaluation["explanation"]

        # Save image description to file
        if timestamp:
            import json
            desc_dir = Path("game/gift_photos/image_descriptions")
            desc_dir.mkdir(parents=True, exist_ok=True)
            desc_path = desc_dir / f"gift_{timestamp}.json"

            description_data = {
                "timestamp": timestamp,
                "gift_analysis": gift_analysis,
                "affinity_score": affinity_score,
                "affinity_reason": affinity_reason,
                "matched_preferences": evaluation.get("matched_preferences", []),
                "photo_path": str(photo_path) if photo_path else None
            }

            with open(desc_path, 'w') as f:
                json.dump(description_data, f, indent=2)

        return {
            "success": True,
            "gift_analysis": gift_analysis,
            "affinity_score": affinity_score,
            "affinity_reason": affinity_reason,
            "matched_preferences": evaluation.get("matched_preferences", []),
            "photo_path": str(photo_path) if photo_path else None,
            "error": None
        }

    # Tool 3: Read Preferences
    read_preferences_def = {
        "name": "read_doda_preferences",
        "description": "Read your preferences to understand what you love, like, dislike, and hate. Use this to reason about gifts before analyzing them.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["all", "loves", "likes", "dislikes", "hates"],
                    "description": "Which category of preferences to read",
                    "default": "all"
                }
            },
            "required": []
        }
    }

    def handle_read_preferences(category: str = "all") -> dict:
        """Read Doda's preferences"""
        if category == "all":
            prefs = preferences_system.get_all_preferences()
        else:
            prefs = {category: preferences_system.get_category(category)}

        return {
            "success": True,
            "preferences": prefs,
            "error": None
        }

    # Tool 4: Rotate Base
    rotate_base_def = {
        "name": "rotate_base",
        "description": "Rotate your wheeled base left or right by specified degrees to look around. Automatically returns to starting orientation after rotation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "degrees": {
                    "type": "number",
                    "description": "How many degrees to rotate (positive number, typically 45-180)",
                    "minimum": 0,
                    "maximum": 360
                },
                "direction": {
                    "type": "string",
                    "enum": ["left", "right", "auto"],
                    "description": "Direction to rotate (auto chooses shortest path)",
                    "default": "auto"
                },
                "reason": {
                    "type": "string",
                    "description": "Why you're rotating (for logging)"
                }
            },
            "required": ["degrees", "reason"]
        }
    }

    def handle_rotate_base(degrees: float, direction: str = "auto", reason: str = "") -> dict:
        """Rotate the base"""
        result = robot_controller.rotate_base(degrees, direction)

        return {
            "success": result["success"],
            "degrees_rotated": result.get("actual_degrees", 0.0),
            "direction": direction,
            "reason": reason,
            "returned_to_start": result["success"],  # Always returns to start if successful
            "error": result.get("error")
        }

    # Tool 5: Capture Joint Positions
    capture_positions_def = {
        "name": "capture_joint_positions",
        "description": "Capture current positions of all your joints (arm and wheels). Useful for recording poses or checking current state.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }

    def handle_capture_positions() -> dict:
        """Capture all joint positions"""
        result = robot_controller.capture_joint_positions()

        return {
            "success": result["success"],
            "positions": result.get("positions", {}),
            "error": result.get("error")
        }

    # Return tool definitions and handlers
    tool_definitions = [
        execute_behavior_def,
        capture_gift_def,
        read_preferences_def,
        rotate_base_def,
        capture_positions_def
    ]

    tool_handlers = {
        "execute_dodo_behavior": handle_execute_behavior,
        "capture_and_analyze_gift": handle_capture_gift,
        "read_doda_preferences": handle_read_preferences,
        "rotate_base": handle_rotate_base,
        "capture_joint_positions": handle_capture_positions
    }

    return tool_definitions, tool_handlers
