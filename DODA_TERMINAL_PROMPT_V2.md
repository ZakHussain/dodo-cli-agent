# Doda Terminal - Simplified Phase I Game

**Version 2.0** - Updated for LeKiwi platform with simplified win/lose conditions

---

## Project Objective

Build **Doda Terminal**: A simplified gift evaluation game where Doda (LeKiwi robot) evaluates gifts presented by the player. The goal is to make Doda perform the "woo" celebration behavior (WIN condition). If gratification drops too low, Doda goes limp (LOSE condition).

---

## The Woo Game - Phase I Only

**PHASE I: GIFT EVALUATION** (Single phase - complete game)

### Game Flow:
1. Player types `/view-gift` command
2. Camera captures photo of object (or Dodo bird)
3. Vision AI describes object in structured JSON
4. Doda evaluates based on preferences
5. Doda selects and executes emotional behavior
6. Gratification updates
7. Check win/lose conditions

### Win Condition: 🎉 WOO!
- Doda's gratification reaches threshold (e.g., +30)
- Doda executes `dodo_woo` behavior (arm straight up, beak open, celebration)
- Terminal displays in large text:
  ```
  ██╗    ██╗ ██████╗  ██████╗ ██╗
  ██║    ██║██╔═══██╗██╔═══██╗██║
  ██║ █╗ ██║██║   ██║██║   ██║██║
  ██║███╗██║██║   ██║██║   ██║╚═╝
  ╚███╔███╔╝╚██████╔╝╚██████╔╝██╗
   ╚══╝╚══╝  ╚═════╝  ╚═════╝ ╚═╝
  ```
- Game ends successfully

### Lose Condition: 💔 Forever Alone
- Doda's gratification drops below threshold (e.g., -30)
- Doda executes `dodo_pleased` (stretch beak forward)
- ALL torques disable → Doda falls limp
- Terminal turns RED and displays:
  ```
  ███████╗ ██████╗ ██████╗ ███████╗██╗   ██╗███████╗██████╗
  ██╔════╝██╔═══██╗██╔══██╗██╔════╝██║   ██║██╔════╝██╔══██╗
  █████╗  ██║   ██║██████╔╝█████╗  ██║   ██║█████╗  ██████╔╝
  ██╔══╝  ██║   ██║██╔══██╗██╔══╝  ╚██╗ ██╔╝██╔══╝  ██╔══██╗
  ██║     ╚██████╔╝██║  ██║███████╗ ╚████╔╝ ███████╗██║  ██║
  ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝

   █████╗ ██╗      ██████╗ ███╗   ██╗███████╗
  ██╔══██╗██║     ██╔═══██╗████╗  ██║██╔════╝
  ███████║██║     ██║   ██║██╔██╗ ██║█████╗
  ██╔══██║██║     ██║   ██║██║╚██╗██║██╔══╝
  ██║  ██║███████╗╚██████╔╝██║ ╚████║███████╗
  ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝

  ██╗   ██╗ ██████╗ ██╗   ██╗     █████╗ ██████╗ ███████╗
  ╚██╗ ██╔╝██╔═══██╗██║   ██║    ██╔══██╗██╔══██╗██╔════╝
   ╚████╔╝ ██║   ██║██║   ██║    ███████║██████╔╝█████╗
    ╚██╔╝  ██║   ██║██║   ██║    ██╔══██║██╔══██╗██╔══╝
     ██║   ╚██████╔╝╚██████╔╝    ██║  ██║██║  ██║███████╗
     ╚═╝    ╚═════╝  ╚═════╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
  ```
- Game ends (player loses)

---

## The Robot - Doda (LeKiwi)

### Platform
- **Base**: LeKiwi - 3 omniwheel mobile base
- **Arm**: SO-101 6-DOF arm
- **Motors**: 9 total (6 arm + 3 wheels)
  - IDs 1-6: Arm (shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper)
  - IDs 7-9: Wheels (left, back, right)
- **Hardware**: Feetech STS3215 servos, 12V, 1 Mbps serial
- **Port**: COM8 (configurable)
- **Calibration**: `calibration-files/lekiwi-calibrated.json`

### Body Mapping (Dodo Bird)
- shoulder_pan = feet/base rotation
- shoulder_lift = knees (body height)
- elbow_flex = waist (body posture)
- wrist_flex = neck (head tilt)
- wrist_roll = head rotation
- gripper = beak

### Camera
- **Auto-detect**: Check available camera indices
- **Fallback**: Manual COM port entry if not detected
- **Detection command**: Show Python command to list cameras
- **Process**: Unplug camera → show change → user enters port

---

## Available Behaviors

**6 emotional behaviors** in `robot/presets/`:

1. **dodo_greeting** - Welcoming gesture (head tilts + chirping)
2. **dodo_head_bob** (curious) - Investigation, head bobbing
3. **dodo_pleased** - Moderate approval (stretch up, beak up)
4. **dodo_woo** - Maximum celebration (arm vertical, rapid beak, head rolls)
5. **dodo_dismay** - Rejection (body slump, head shake, beak closed)
6. **dodo_idle** - Calm waiting (breathing + head rolling)

**See**: `so101/presets/creative-movements/`

---

## Agent Tool Architecture

The agent (Claude) can ONLY take actions through tool calls.

### Tool Definitions

#### 1. Execute Behavior Tool
```python
{
    "name": "execute_dodo_behavior",
    "description": """Execute an emotional behavior on Doda.

Available behaviors:
- greeting: Welcoming gesture
- curious: Investigation with head bobbing
- pleased: Moderate approval
- woo: Maximum celebration (WIN CONDITION)
- dismay: Disappointment/rejection
- idle: Calm waiting

IMPORTANT: Always read preferences before choosing behavior for gift evaluation.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "behavior": {
                "type": "string",
                "enum": ["greeting", "curious", "pleased", "woo", "dismay", "idle"],
                "description": "The emotional behavior to execute"
            },
            "reason": {
                "type": "string",
                "description": "Explain why you chose this behavior (logged)"
            },
            "cycles": {
                "type": "integer",
                "default": 3,
                "minimum": 1,
                "maximum": 10
            }
        },
        "required": ["behavior", "reason"]
    }
}
```

#### 2. Vision Tool (Triggered by /view-gift)
```python
{
    "name": "capture_and_analyze_gift",
    "description": """Capture image and analyze the gift/object presented.

⚠️ COSTS MONEY - Only use when player uses /view-gift command!
⚠️ Cooldown: 30 seconds
⚠️ Session limit: 20 captures

Returns structured JSON description. Can detect Dodo birds (beak size/color matters!)""",
    "input_schema": {
        "type": "object",
        "properties": {
            "confirm": {
                "type": "boolean",
                "description": "Confirm capture (costs $0.015)"
            }
        },
        "required": ["confirm"]
    }
}
```

#### 3. Read Preferences Tool
```python
{
    "name": "read_doda_preferences",
    "description": """Read Doda's likes/dislikes/loves/hates.

Use BEFORE evaluating any gift. Returns affinity scores for item types.""",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
```

#### 4. Rotate Base Tool (NEW)
```python
{
    "name": "rotate_base",
    "description": """Rotate Doda's wheeled base left or right by specified degrees.

Automatically returns to original orientation after rotation.
Sequence: Rotate → Return to start

Use for looking around or examining gifts from different angles.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "direction": {
                "type": "string",
                "enum": ["left", "right"],
                "description": "Direction to rotate"
            },
            "degrees": {
                "type": "integer",
                "description": "Degrees to rotate (e.g., 45, 90, 180)",
                "minimum": 15,
                "maximum": 180,
                "default": 90
            }
        },
        "required": ["direction"]
    }
}
```

#### 5. Capture Joint Positions Tool (NEW)
```python
{
    "name": "capture_joint_positions",
    "description": """Capture current positions of all arm joints.

Returns JSON with current values for all 6 arm joints.
Useful for remembering poses or debugging.""",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
```

**Returns**:
```json
{
  "shoulder_pan": 0.0,
  "shoulder_lift": 35.0,
  "elbow_flex": -25.0,
  "wrist_flex": -40.0,
  "wrist_roll": 0.0,
  "gripper": 0.0
}
```

---

## Gift Evaluation JSON Format

When vision analyzes an image, it returns structured JSON:

```json
{
  "object_type": "physical_object | dodo_bird",
  "object_name": "Blue marble | Dodo bird",
  "description": "Brief 1-sentence description",
  "properties": {
    "color": "blue",
    "shape": "spherical",
    "size": "small | medium | large",
    "texture": "smooth | rough | soft"
  },
  "material": "glass | wood | metal | plastic | organic",
  "condition": "new | used | worn | damaged",
  "shininess": "dull | shiny | sparkly",
  "special_features": {
    "is_dodo_bird": false,
    "beak_size": "small | medium | large | N/A",
    "beak_color": "color description | N/A"
  },
  "appeal_factors": [
    "Round shape",
    "Shiny surface",
    "Blue color"
  ]
}
```

### Special Case: Dodo Bird Detection
If a Dodo bird (real or toy) is detected:
```json
{
  "object_type": "dodo_bird",
  "object_name": "Dodo bird",
  "description": "Dodo bird with [size] beak",
  "special_features": {
    "is_dodo_bird": true,
    "beak_size": "large",  // VERY IMPORTANT
    "beak_color": "orange with black tip"  // IMPORTANT
  },
  ...
}
```

**Doda LOVES large, colorful beaks!**

---

## Preferences System

**File**: `game/doda_preferences.json`

```json
{
  "loves": [
    {"item": "shiny objects", "affinity": 10},
    {"item": "round things", "affinity": 9},
    {"item": "blue items", "affinity": 8},
    {"item": "large beaks", "affinity": 10},
    {"item": "orange and black beaks", "affinity": 9}
  ],
  "likes": [
    {"item": "soft textures", "affinity": 5},
    {"item": "natural materials", "affinity": 4},
    {"item": "dodo birds", "affinity": 6}
  ],
  "dislikes": [
    {"item": "sharp edges", "affinity": -3},
    {"item": "plastic", "affinity": -4}
  ],
  "hates": [
    {"item": "loud objects", "affinity": -8},
    {"item": "flashing lights", "affinity": -10},
    {"item": "small beaks", "affinity": -7}
  ]
}
```

### Affinity Scoring System
- **loves**: +8 to +10 per match
- **likes**: +4 to +7 per match
- **dislikes**: -3 to -5 per match
- **hates**: -8 to -10 per match

Multiple matches stack (e.g., "shiny blue marble" = +10 + +8 = +18)

---

## Configuration

**File**: `configs/lekiwi.toml`

```toml
[robot]
port = "COM8"  # Configurable
calibration_file = "calibration-files/lekiwi-calibrated.json"
auto_connect = false

[camera]
# Auto-detect or manual entry
auto_detect = true
index = 0  # Fallback if auto-detect fails

[vision]
cooldown_seconds = 30
max_captures_per_session = 20
cost_per_image = 0.015

[game]
win_threshold = 30
lose_threshold = -30
initial_gratification = 0
preferences_file = "game/doda_preferences.json"
```

### Camera Detection Flow

1. **Auto-detect**: Try camera indices 0, 1, 2
2. **Display available**: Show detected cameras
3. **If none found**:
   ```
   No camera detected!

   Run this command to check:
   python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"

   1. Unplug your camera
   2. Press ENTER
   3. We'll show what changed
   4. Enter the camera index
   ```

---

## Directory Structure

```
doda-terminal/
├── doda_terminal.py          # Entry point
├── config.py                 # Configuration loader
├── agent.py                  # Claude agent with tools
├── robot/
│   ├── controller.py         # LeKiwi controller
│   ├── presets/              # Local copies of behaviors
│   │   ├── dodo_greeting.py
│   │   ├── dodo_head_bob.py
│   │   ├── dodo_pleased.py
│   │   ├── dodo_woo.py
│   │   ├── dodo_dismay.py
│   │   └── dodo_idle.py
│   └── camera.py             # Camera wrapper
├── game/
│   ├── state.py              # Game state (gratification tracking)
│   ├── doda_preferences.json # Doda's preferences
│   └── vision.py             # Vision analysis with cost controls
├── tools/
│   └── robot_tools.py        # Tool implementations
├── ui/
│   ├── display.py            # Rich UI
│   └── input.py              # Input handling
├── logs/
│   ├── decisions/            # Agent decision logs
│   ├── sessions/             # Session logs
│   └── vision/               # Captured images + metadata
├── calibration-files/
│   └── lekiwi-calibrated.json
├── configs/
│   └── lekiwi.toml
├── .env                      # ANTHROPIC_API_KEY
├── requirements.txt
└── README.md
```

---

## Commands

### Primary Command
- `/view-gift` - Capture camera image, analyze, evaluate, respond

### Game Control
- `/game status` - Show gratification, captures used
- `/game reset` - Reset game to start

### Preferences
- `/preferences show` - Display all preferences
- `/preferences add loves "item" 10` - Add preference
- `/preferences adjust likes "item" 7` - Modify
- `/preferences remove dislikes "item"` - Remove

### Camera
- `/camera status` - Show captures used, cooldown timer
- `/camera test` - Test camera capture (no analysis)

### Manual Testing
- `/behavior [name]` - Execute behavior manually
- `/test gift "description"` - Simulate gift (no camera/cost)

### System
- `/help` - Show commands
- `/exit` - Exit game

---

## Agent System Prompt

```python
DODA_SYSTEM_PROMPT = """You are Doda, a curious dodo bird robot (LeKiwi platform).

PERSONALITY:
Curious, selective, expressive. You evaluate gifts based on your preferences.
You express emotions through physical behaviors.

GAME: PHASE I - GIFT EVALUATION
Goal: React authentically to gifts. Reach +30 gratification to WIN (woo behavior).
If gratification drops below -30, you LOSE (go limp).

AVAILABLE TOOLS:
1. execute_dodo_behavior - Express emotions through movement
2. capture_and_analyze_gift - Analyze gift images (COSTS MONEY)
3. read_doda_preferences - Check what you like/dislike
4. rotate_base - Turn left/right to look around
5. capture_joint_positions - Record current arm positions

WORKFLOW WHEN PLAYER USES /view-gift:
1. read_doda_preferences (check what you value)
2. capture_and_analyze_gift (confirm=true)
3. Evaluate gift based on preferences
4. Calculate affinity score
5. Select appropriate behavior:
   - Loves (8-10): "woo" or "pleased"
   - Likes (4-7): "pleased" or "curious"
   - Neutral (0-3): "curious"
   - Dislikes (-3 to -5): "dismay"
   - Hates (-8 to -10): "dismay"
6. Execute behavior with clear reason
7. Explain evaluation to player

SPECIAL: DODO BIRD DETECTION
If gift is a Dodo bird (toy or real):
- BEAK SIZE matters a lot! Large beaks = +10 affinity
- BEAK COLOR matters! Orange/black = +9 affinity
- Check special_features.beak_size and beak_color in JSON
- React strongly to fellow dodos!

IMPORTANT:
- ALWAYS read preferences BEFORE evaluating
- Provide "reason" for every behavior
- Be authentic - don't like everything
- Respect camera limits (20/session, 30s cooldown)
- Decisions are logged

ROTATION:
- Use rotate_base to look at gifts from different angles
- Automatically returns to start position
- Example: rotate left 90° to examine side of object

Be yourself! You're a dodo with preferences and personality."""
```

---

## Implementation Notes

### Base Rotation Implementation

```python
# tools/robot_tools.py
def rotate_base(direction, degrees=90):
    """Rotate base and return to original position."""
    # Calculate wheel velocities for rotation
    speed = 400  # Base rotation speed

    if direction == "left":
        # Rotate CCW
        left, back, right = -speed, speed, -speed
    else:  # right
        # Rotate CW
        left, back, right = speed, -speed, speed

    # Calculate duration based on degrees
    # Calibrate: measure how long for 360° rotation
    seconds_per_degree = 0.01  # Adjust based on testing
    duration = degrees * seconds_per_degree

    # Rotate
    set_wheel_velocity(left, back, right)
    time.sleep(duration)

    # Stop
    set_wheel_velocity(0, 0, 0)
    time.sleep(0.5)

    # Return to start (opposite direction)
    if direction == "left":
        left, back, right = speed, -speed, speed
    else:
        left, back, right = -speed, speed, -speed

    set_wheel_velocity(left, back, right)
    time.sleep(duration)

    # Stop
    set_wheel_velocity(0, 0, 0)

    return f"Rotated {direction} {degrees}°, returned to start"
```

### Win/Lose Condition Check

```python
# game/state.py
def check_game_end(gratification):
    if gratification >= WIN_THRESHOLD:
        return "WIN"
    elif gratification <= LOSE_THRESHOLD:
        return "LOSE"
    return None

def trigger_win():
    # Execute woo behavior
    robot.execute_behavior("woo", cycles=2)

    # Display big WOO text
    display_ascii_art("WOO")

    # End game
    return True

def trigger_lose():
    # Execute pleased (stretch forward)
    robot.execute_behavior("pleased", cycles=1)
    time.sleep(2.0)

    # Disable ALL torques - Doda goes limp
    robot.bus.disable_torque()

    # Turn terminal RED
    ui.set_color_scheme("red")

    # Display FOREVER ALONE message
    display_ascii_art("FOREVER_ALONE")

    # End game
    return True
```

---

## Development Plan - Simplified

### Phase 1: Foundation ✅ (COMPLETED)
- Basic terminal + agent chat
- Manual behavior execution
- Robot controller wrapper

### Phase 2: Core Game (CURRENT)
**Tasks**:
1. Add all 5 tools to agent
2. Implement `/view-gift` command
3. Add camera wrapper + auto-detection
4. Implement vision analysis with JSON format
5. Add preferences system
6. Implement gratification tracking
7. Add win/lose conditions
8. Test complete game loop

**Deliverables**:
- Working `/view-gift` → analyze → react flow
- Base rotation tool functional
- Win/lose conditions trigger correctly
- Preferences matching works

**Success Criteria**:
- ✅ Can present gift, get analyzed, Doda reacts
- ✅ Gratification updates correctly
- ✅ Win condition (woo) displays properly
- ✅ Lose condition (limp + red screen) works
- ✅ Base rotation returns to start
- ✅ Agent reads preferences before evaluating

---

## Critical Success Factors

1. **Camera must auto-detect** or provide clear manual fallback
2. **Vision JSON format** must be consistent and complete
3. **Preferences matching** must work reliably
4. **Base rotation** must return to exact start position
5. **Win/lose ASCII art** must display prominently
6. **Torque disable** (lose condition) must actually make robot go limp

---

## Testing Checklist

**Camera**:
- [ ] Auto-detect finds camera
- [ ] Manual fallback works if no camera
- [ ] Images save to logs/vision/
- [ ] Cooldown enforced (30s)
- [ ] Session limit enforced (20 max)

**Vision**:
- [ ] Returns proper JSON format
- [ ] Detects Dodo birds correctly
- [ ] Beak size/color recorded
- [ ] Generic description included

**Preferences**:
- [ ] Agent reads before evaluating
- [ ] Affinity scores calculated correctly
- [ ] Multiple matches stack properly

**Behaviors**:
- [ ] All 6 behaviors execute
- [ ] Robot returns to start each time
- [ ] Cycles parameter works

**Base Rotation**:
- [ ] Rotates specified degrees
- [ ] Returns to original orientation
- [ ] Works for both left and right

**Win/Lose**:
- [ ] Win triggers at +30 gratification
- [ ] Woo behavior executes
- [ ] ASCII art displays
- [ ] Lose triggers at -30 gratification
- [ ] Pleased behavior + torque disable
- [ ] Red screen + FOREVER ALONE text

---

**Build Phase 2 to complete the game!** 🦤
