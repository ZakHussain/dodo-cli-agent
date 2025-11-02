"""
Dodo Dismay - Disappointment/Rejection Response
Doda expresses disappointment by looking down and slowly shaking her head.

Body mapping:
- shoulder_lift = knees
- elbow_flex = waist/butt
- wrist_flex = neck
- wrist_roll = head rotation
- gripper = beak

To run it:
# Interactive mode
python so101_control.py --port COM7 --calibration zetta-zero.json --interactive
SO101> preset creative-movements/dodo_dismay

# Command line
python so101_control.py --port COM7 --calibration zetta-zero.json --preset creative-movements/dodo_dismay
"""
import time


def execute(controller):
    """
    Perform a dodo bird dismay/disappointment response.

    Doda looks down at the ground, slumps slightly, and slowly shakes
    her head side to side in disapproval with beak closed.

    Args:
        controller: SO101Controller instance
    """
    print("Dodo dismay - Disappointed...")

    # Capture starting position
    start_pos = controller.get_positions()
    print("  Captured starting position")

    # Idle/alert stance parameters
    idle_knee_lift = 35.0       # shoulder_lift: body raised
    idle_waist_flex = -25.0     # elbow_flex: body upright
    idle_head_forward = -40.0   # wrist_flex: beak points straight forward

    # Behavior parameters
    body_slump = -15.0          # shoulder_lift: slight body slump (sad posture)
    head_down = 40.0            # wrist_flex: head looks down (disappointment)
    head_shake_amount = 30.0    # wrist_roll: side-to-side shake

    # Step 1: Move to idle/alert stance
    print("  1. Moving to idle stance...")
    controller.set_positions({
        "shoulder_lift": start_pos["shoulder_lift"] + idle_knee_lift,
        "elbow_flex": start_pos["elbow_flex"] + idle_waist_flex,
        "wrist_flex": start_pos["wrist_flex"] + idle_head_forward,
    })
    time.sleep(2.0)

    # Step 2: Look down in dismay with slight slump
    print("  2. Looking down in dismay...")
    controller.set_positions({
        "shoulder_lift": start_pos["shoulder_lift"] + idle_knee_lift + body_slump,
        "wrist_flex": start_pos["wrist_flex"] + head_down,
    })
    controller.set_gripper(0.0)  # Beak closed (disapproval)
    time.sleep(1.5)

    # Step 3: Slow head shakes (side to side in disappointment)
    print("  3. Shaking head in dismay...")
    for i in range(3):
        # Shake left
        controller.set_single_joint("wrist_roll", start_pos["wrist_roll"] - head_shake_amount)
        time.sleep(0.8)
        # Shake right
        controller.set_single_joint("wrist_roll", start_pos["wrist_roll"] + head_shake_amount)
        time.sleep(0.8)

    # Return head roll to center
    controller.set_single_joint("wrist_roll", start_pos["wrist_roll"])
    time.sleep(0.5)

    # Step 4: Return to starting position
    print("  4. Returning to start position...")
    controller.set_positions(start_pos)
    time.sleep(2.0)

    print("✓ Dodo dismay complete!\n")
