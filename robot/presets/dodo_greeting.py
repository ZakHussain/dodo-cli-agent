"""
Dodo Greeting - Welcoming/Turn Start
Doda greets the player with friendly head tilts and chirping motions.

Body mapping:
- shoulder_lift = knees
- elbow_flex = waist/butt
- wrist_flex = neck
- wrist_roll = head rotation
- gripper = beak

To run it:
# Interactive mode
python so101_control.py --port COM7 --calibration zetta-zero.json --interactive
SO101> preset creative-movements/dodo_greeting

# Command line
python so101_control.py --port COM7 --calibration zetta-zero.json --preset creative-movements/dodo_greeting
"""
import time


def execute(controller):
    """
    Perform a dodo bird greeting/welcoming gesture.

    Doda tilts her head side-to-side in a friendly, curious manner
    and makes small chirping beak movements to greet the player.

    Args:
        controller: SO101Controller instance
    """
    print("Dodo greeting - Hello!")

    # Capture starting position
    start_pos = controller.get_positions()
    print("  Captured starting position")

    # Idle/alert stance parameters
    idle_knee_lift = 35.0       # shoulder_lift: body raised
    idle_waist_flex = -25.0     # elbow_flex: body upright
    idle_head_forward = -40.0   # wrist_flex: beak points straight forward

    # Behavior parameters
    head_tilt_amount = 30.0     # wrist_roll: friendly head tilt
    chirp_open = 50.0           # gripper: small beak opening (chirping)

    # Step 1: Move to idle/alert stance
    print("  1. Moving to idle stance...")
    controller.set_positions({
        "shoulder_lift": start_pos["shoulder_lift"] + idle_knee_lift,
        "elbow_flex": start_pos["elbow_flex"] + idle_waist_flex,
        "wrist_flex": start_pos["wrist_flex"] + idle_head_forward,
    })
    time.sleep(2.0)

    # Step 2: Friendly head tilts (curious greeting)
    print("  2. Friendly head tilts...")
    for i in range(3):
        # Tilt left
        controller.set_single_joint("wrist_roll", start_pos["wrist_roll"] - head_tilt_amount)
        time.sleep(0.6)
        # Tilt right
        controller.set_single_joint("wrist_roll", start_pos["wrist_roll"] + head_tilt_amount)
        time.sleep(0.6)

    # Return head to center
    controller.set_single_joint("wrist_roll", start_pos["wrist_roll"])
    time.sleep(0.4)

    # Step 3: Chirping beak movements (friendly greeting sounds)
    print("  3. Chirping...")
    for i in range(3):
        # Small beak open (chirp)
        controller.set_gripper(chirp_open)
        time.sleep(0.3)
        # Close beak
        controller.set_gripper(0.0)
        time.sleep(0.3)

    # Step 4: Return to starting position
    print("  4. Returning to start position...")
    controller.set_positions(start_pos)
    time.sleep(2.0)

    print("✓ Dodo greeting complete!\n")
