"""
Dodo Woo - Maximum "Woo!" Celebration
Doda expresses extreme joy by fully extending her entire arm straight up to the sky.

Body mapping:
- shoulder_lift = knees
- elbow_flex = waist/butt
- wrist_flex = neck
- gripper = beak

To run it:
# Interactive mode
python so101_control.py --port COM7 --calibration zetta-zero.json --interactive
SO101> preset creative-movements/dodo_woo

# Command line
python so101_control.py --port COM7 --calibration zetta-zero.json --preset creative-movements/dodo_woo
"""
import time


def execute(controller):
    """
    Perform a dodo bird maximum "woo!" celebration.

    Doda stretches her ENTIRE arm completely straight up toward the sky,
    points her beak straight up, and celebrates with rapid beak movements
    and excited head rolls.

    Args:
        controller: SO101Controller instance
    """
    print("Dodo WOO! (Maximum celebration)")

    # Capture starting position
    start_pos = controller.get_positions()
    print("  Captured starting position")

    # Idle/alert stance parameters
    idle_knee_lift = 35.0       # shoulder_lift: body raised
    idle_waist_flex = -25.0     # elbow_flex: body upright
    idle_head_forward = -40.0   # wrist_flex: beak points straight forward

    # Motion parameters
    stretch_height = 65.0       # shoulder_lift: reach maximum height (knees extend)
    arm_straight_up = -90.0     # elbow_flex: flex ALL THE WAY - arm completely vertical
    head_up = -65.0             # wrist_flex: point beak straight up to sky
    head_roll_amount = 25.0     # wrist_roll: head shake left/right

    # Step 1: Move to idle/alert stance
    print("  1. Moving to idle stance...")
    controller.set_positions({
        "shoulder_lift": start_pos["shoulder_lift"] + idle_knee_lift,
        "elbow_flex": start_pos["elbow_flex"] + idle_waist_flex,
        "wrist_flex": start_pos["wrist_flex"] + idle_head_forward,
    })
    time.sleep(2.0)

    # Step 2: Stretch upward to the sky - FULL EXTENSION
    print("  2. Stretching ENTIRE arm to the sky...")
    controller.set_positions({
        "shoulder_lift": start_pos["shoulder_lift"] + stretch_height,
        "elbow_flex": start_pos["elbow_flex"] + arm_straight_up,
        "wrist_flex": start_pos["wrist_flex"] + head_up,
    })
    time.sleep(2.0)

    # Step 3: Rapid beak opening/closing - "Woo! Woo! Woo!"
    print("  3. Woo! Woo! Woo!")
    for i in range(3):
        # Open beak
        controller.set_gripper(100.0)
        time.sleep(0.3)
        # Close beak
        controller.set_gripper(0.0)
        time.sleep(0.3)

    # Step 4: Head roll left and right (excited celebration)
    print("  4. Excited head rolls...")
    for i in range(2):
        # Roll left
        controller.set_single_joint("wrist_roll", start_pos["wrist_roll"] - head_roll_amount)
        time.sleep(0.4)
        # Roll right
        controller.set_single_joint("wrist_roll", start_pos["wrist_roll"] + head_roll_amount)
        time.sleep(0.4)
    # Return head roll to center
    controller.set_single_joint("wrist_roll", start_pos["wrist_roll"])
    time.sleep(0.3)

    # Step 5: Return to starting position
    print("  5. Returning to start position...")
    controller.set_positions(start_pos)
    time.sleep(2.0)

    print("✓ Dodo WOO complete!\n")
