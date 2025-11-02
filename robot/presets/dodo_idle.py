"""
Dodo Idle - Waiting Animation
Doda waits patiently with gentle breathing motions and subtle head rolling.

Body mapping:
- shoulder_lift = knees
- elbow_flex = waist/butt
- wrist_flex = neck
- wrist_roll = head rotation
- gripper = beak

To run it:
# Interactive mode
python so101_control.py --port COM7 --calibration zetta-zero.json --interactive
SO101> preset creative-movements/dodo_idle

# Command line
python so101_control.py --port COM7 --calibration zetta-zero.json --preset creative-movements/dodo_idle
python so101_control.py --port COM7 --calibration zetta-zero.json --preset creative-movements/dodo_idle cycles=5
"""
import time


def execute(controller, cycles=1):
    """
    Perform a dodo bird idle/waiting animation.

    Doda waits patiently with gentle breathing-like body movements,
    slow meditative head rolling, and occasional small head adjustments.
    Very calm and subtle - showing she's alive but patient.

    Args:
        controller: SO101Controller instance
        cycles: Number of idle cycles to perform (default: 3)
    """
    print(f"Dodo idle - Waiting patiently ({cycles} cycles)...")

    # Capture starting position
    start_pos = controller.get_positions()
    print("  Captured starting position")

    # Idle/alert stance parameters
    idle_knee_lift = 35.0       # shoulder_lift: body raised
    idle_waist_flex = -25.0     # elbow_flex: body upright
    idle_head_forward = -40.0   # wrist_flex: beak points straight forward

    # Behavior parameters
    breath_amount = 3.0         # shoulder_lift: subtle breathing up/down
    head_roll_amount = 15.0     # wrist_roll: gentle head roll side-to-side
    head_adjust = 5.0           # wrist_flex: tiny head adjustments

    # Step 1: Move to idle/alert stance
    print("  1. Moving to idle stance...")
    controller.set_positions({
        "shoulder_lift": start_pos["shoulder_lift"] + idle_knee_lift,
        "elbow_flex": start_pos["elbow_flex"] + idle_waist_flex,
        "wrist_flex": start_pos["wrist_flex"] + idle_head_forward,
    })
    time.sleep(2.0)

    # Step 2: Idle loop - breathing and head rolling
    print(f"  2. Idle animation ({cycles} cycles)...")

    idle_shoulder = start_pos["shoulder_lift"] + idle_knee_lift
    idle_wrist_flex = start_pos["wrist_flex"] + idle_head_forward

    for cycle in range(cycles):
        print(f"     Cycle {cycle + 1}/{cycles}")

        # Breathe in (body rises slightly) + head roll left
        controller.set_positions({
            "shoulder_lift": idle_shoulder + breath_amount,
            "wrist_roll": start_pos["wrist_roll"] - head_roll_amount,
        })
        time.sleep(2.0)

        # Breathe out (body lowers slightly) + head roll right
        controller.set_positions({
            "shoulder_lift": idle_shoulder - breath_amount,
            "wrist_roll": start_pos["wrist_roll"] + head_roll_amount,
        })
        time.sleep(2.0)

        # Breathe neutral + head center + small head adjustment
        controller.set_positions({
            "shoulder_lift": idle_shoulder,
            "wrist_roll": start_pos["wrist_roll"],
            "wrist_flex": idle_wrist_flex + head_adjust,
        })
        time.sleep(1.5)

        # Return head to neutral
        controller.set_single_joint("wrist_flex", idle_wrist_flex)
        time.sleep(1.5)

    # Step 3: Return to starting position
    print("  3. Returning to start position...")
    controller.set_positions(start_pos)
    time.sleep(2.0)

    print("✓ Dodo idle complete!\n")
