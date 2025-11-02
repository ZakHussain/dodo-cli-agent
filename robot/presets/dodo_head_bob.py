"""
Dodo Head Bob
Curious head bobbing motion of a dodo bird in alert stance.

Body mapping:
- shoulder_lift = knees
- elbow_flex = waist/butt
- wrist_flex = neck
- wrist_roll = head rotation
- gripper = beak

To run it:
# Interactive mode
python so101_control.py --port COM7 --calibration zetta-zero.json --interactive
SO101> preset creative-movements/dodo_head_bob

# Or with custom cycles
SO101> preset creative-movements/dodo_head_bob cycles=3

# Command line
python so101_control.py --port COM7 --calibration zetta-zero.json --preset creative-movements/dodo_head_bob
"""
import time


def execute(controller, cycles=4):
    """
    Perform a dodo bird head bobbing motion.

    The dodo first raises its body into an alert stance (lifting knees and
    extending waist), then bobs its head (neck) up and down curiously while
    maintaining the raised posture.

    Args:
        controller: SO101Controller instance
        cycles: Number of head bob repetitions (default: 4)
    """
    print(f"Dodo head bob starting ({cycles} cycles)...")

    # Capture starting position
    start_pos = controller.get_positions()
    print("  Captured starting position")

    # Motion parameters
    knee_lift = 35.0        # shoulder_lift: raise body (knees up)
    waist_flex = -25.0      # elbow_flex: flex inward (keep body upright)
    head_forward = -40.0    # wrist_flex: head raised/extended (alert stance)
    neck_bob_down = 30.0    # wrist_flex: head bob down from forward

    # Step 1: Stand up alert with head looking forward
    print("  1. Standing up alert...")
    controller.set_positions({
        "shoulder_lift": start_pos["shoulder_lift"] + knee_lift,
        "elbow_flex": start_pos["elbow_flex"] + waist_flex,
        "wrist_flex": start_pos["wrist_flex"] + head_forward,
    })
    time.sleep(2.0)

    # Step 2: Perform head bobs while body stays raised
    for i in range(cycles):
        print(f"  2. Head bob {i+1}/{cycles}...")

        # Bob head down (neck bends down from forward)
        controller.set_single_joint("wrist_flex", start_pos["wrist_flex"] + neck_bob_down)
        time.sleep(1.0)

        # Bob head back to forward (neck back to alert)
        controller.set_single_joint("wrist_flex", start_pos["wrist_flex"] + head_forward)
        time.sleep(1.0)

    # Step 3: Return to exact starting position
    print("  3. Returning to start position...")
    controller.set_positions(start_pos)
    time.sleep(2.0)

    print("✓ Dodo head bob complete!\n")
