# Doda Terminal - Agentic Dodo Terminal Project

## Project Objective

Build **Doda Terminal**: An agentic terminal application enabling an AI agent (Claude) to control Doda (SO-101 robot arm), play the Woo game across two phases (Gift Phase → Nesting Phase), with vision-based gift evaluation, preference tracking, and manual game controls.

---

## Context & Background

### The Woo Game - Two Phase Structure

**PHASE I: GIFT PHASE** (Default starting phase)
- Doda emerges from cave, evaluates gifts from player
- Player presents objects → Doda's camera captures image
- Agent analyzes object → selects emotional response behavior
- gratification accumulates based on how well gifts match Doda's preferences
- **Goal**: Reach gratification threshold to unlock Phase II

**PHASE II: NESTING PHASE** (Unlocked after threshold)
- Doda is ready for nesting responsibilities
- Player brings eggs → Doda evaluates and selects
- Google Calendar integration for nest maintenance schedules
- Policy-driven egg arrangement behaviors
- **Visual Change**: Terminal UI changes color scheme to indicate Phase II

**Phase Transition**: Clear UI indicator + announcement + Doda's celebratory behavior

### The Robot - Doda
- **Platform**: SO-101 6-DOF arm ("zetta-zero") on 3-omni-wheel base (lekiwi)
- **Hardware**: Feetech STS3215 servos, 12V, 1 Mbps serial
- **Port**: COM7 (Windows), requires `zetta-zero.json` calibration
- **Body Mapping**:
  - shoulder_pan = feet/base, shoulder_lift = knees, elbow_flex = waist
  - wrist_flex = neck, wrist_roll = head rotation, gripper = beak

**See**: `so101/Readme.md`, `so101/.claude`, `so101/dodo_mapping.md`

### Available Behaviors
**6 emotional behaviors** in `so101/presets/creative-movements/`:
1. `dodo_greeting` - Welcoming gesture
2. `dodo_head_bob` (curious) - Investigation
3. `dodo_pleased` - Moderate approval
4. `dodo_woo` - Maximum celebration
5. `dodo_dismay` - Rejection
6. `dodo_idle` - Calm waiting

**See**: `so101/how-woo-works.md` for full behavior library

---

## Source Code Repositories

### 1. agentic-terminal (Reference)
**Path**: `./agentic-terminal/`
**Reuse**: Agent loop, Rich UI, config system, command routing, input handling
**See**: `agentic-terminal/CLAUDE.md`, `agentic-terminal/readme.md`

### 2. so101 (Robot Control)
**Path**: `./so101/`
**Reuse**: `so101_control.py`, behaviors, calibration
**See**: `so101/.claude` (lines 478-818 for dodo context)

### 3. Camera (References)
- `computervision/face_detection_viewer.py` - OpenCV example
- `resources/lerobot/src/lerobot/cameras/opencv/` - Professional camera class

---

## Target Directory Structure

```
doda-terminal/
├── doda_terminal.py          # Entry point
├── config.py                 # Config system (robot + camera + game settings)
├── agent.py                  # Claude agent with robot/camera tools
├── commands.py               # Slash commands (expanded for game control)
├── robot/
│   ├── controller.py         # SO101 wrapper
│   ├── behaviors.py          # Behavior discovery
│   └── camera.py             # OpenCV camera wrapper
├── game/
│   ├── state.py              # Game state (phase, gratification, turn tracking)
│   ├── preferences.json      # Doda's likes/dislikes (editable)
│   ├── vision.py             # Image analysis with cost controls
│   └── history.json          # Game session history
├── tools/
│   ├── handlers.py           # Tool display
│   └── robot_tools.py        # Behavior + camera tools
├── ui/
│   ├── display.py            # Rich UI (phase-aware colors)
│   └── input.py              # Input handling
├── tracking/
│   └── usage.py              # Token/cost tracking
├── logs/
│   ├── decisions/            # Agent decision logs (timestamped JSON)
│   ├── sessions/             # Full session logs
│   └── vision/               # Captured images with metadata
├── configs/
│   ├── config.toml           # Default config
│   └── doda.toml             # Doda-specific settings
├── .env                      # ANTHROPIC_API_KEY
├── requirements.txt
├── README.md
└── CLAUDE.md
```

---

## Agent Tool Architecture (CRITICAL)

### How the Agent Works with Tools

**The agent (Claude) can ONLY take actions through tool calls.** Behaviors are NOT just functions - they are **tools** that the agent can see, choose from, and execute.

### Tool Flow Overview

```
User Message → Agent Reasoning → Tool Selection → Tool Execution → Result → Agent Response
                                       ↓
                                 Log Decision
```

**Example Interaction:**
```
User: "Please greet me"

Agent thinks: "User wants a greeting. I have the execute_dodo_behavior tool.
              I should use 'greeting' behavior."

Agent calls tool:
{
  "name": "execute_dodo_behavior",
  "input": {
    "behavior": "greeting",
    "reason": "User requested a greeting"
  }
}
                ↓ [Logged to logs/decisions/]

Robot executes → Returns: "Behavior 'greeting' completed successfully"

Agent responds: "I've greeted you with a friendly head tilt and chirping!"
```

### Decision Logging System

**All agent tool calls are logged** to `logs/decisions/` for later analysis.

**Log Entry Format**:
```json
{
  "timestamp": "2025-01-02T14:30:45.123Z",
  "session_id": "session_20250102_143000",
  "turn_number": 3,
  "game_phase": 1,
  "tool_call": {
    "name": "execute_dodo_behavior",
    "input": {
      "behavior": "pleased",
      "reason": "Shiny blue marble matches loves: shiny objects (+10) and blue items (+8)"
    }
  },
  "context": {
    "user_message": "I'm giving you a shiny blue marble",
    "preferences_consulted": true,
    "vision_used": true,
    "object_description": "Spherical blue marble with metallic sheen...",
    "affinity_score": 18,
    "gratification_before": 32,
    "gratification_after": 50
  },
  "result": {
    "success": true,
    "execution_time_ms": 8500,
    "error": null
  }
}
```

**Logging Commands**:
- `/logs show` - Display recent decisions
- `/logs export [filename]` - Export session logs
- `/logs clear` - Clear old logs (keep last 100)
- `/logs analyze` - Summary statistics (tool usage, success rate)

### Tool Definitions Required

The agent needs **3 core tools** to play Woo:

#### 1. Execute Behavior Tool
```python
EXECUTE_BEHAVIOR_TOOL = {
    "name": "execute_dodo_behavior",
    "description": """Execute an emotional behavior on the Doda robot.

Available behaviors:
- greeting: Welcoming gesture (use at turn start)
- curious: Investigation with head bobbing (use when examining objects)
- pleased: Moderate approval (use for liked gifts)
- woo: Maximum celebration (use for REALLY loved gifts)
- dismay: Disappointment (use for rejected gifts)
- idle: Calm waiting animation (use while waiting)

IMPORTANT: Always read Doda's preferences before choosing a behavior for gift evaluation.""",
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
                "description": "Explain why you chose this behavior (logged for analysis)"
            },
            "cycles": {
                "type": "integer",
                "description": "Number of repetition cycles (for idle, curious)",
                "default": 3,
                "minimum": 1,
                "maximum": 10
            }
        },
        "required": ["behavior", "reason"]
    }
}
```

#### 2. Vision/Camera Tool
```python
CAPTURE_GIFT_TOOL = {
    "name": "capture_and_analyze_gift",
    "description": """Capture image from Doda's camera and analyze the object presented.

⚠️ COSTS MONEY - Only use when player explicitly presents a gift!
⚠️ Cooldown: 30 seconds between captures
⚠️ Session limit: 20 captures maximum

Returns structured object description. Image saved to logs/vision/ with metadata.
Check Doda's preferences after receiving description to determine response.""",
    "input_schema": {
        "type": "object",
        "properties": {
            "confirm": {
                "type": "boolean",
                "description": "Confirm you want to capture and analyze (costs $0.015)"
            }
        },
        "required": ["confirm"]
    }
}
```

#### 3. Read Preferences Tool
```python
READ_PREFERENCES_TOOL = {
    "name": "read_doda_preferences",
    "description": """Read Doda's current likes, dislikes, loves, and hates.

Use this BEFORE evaluating any gift to understand what Doda values.
Returns JSON with affinity scores for different item types.

Call this at the start of each turn and before gift evaluation.""",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
```

### Tool Implementation with Logging

```python
# agent.py
import anthropic
import json
import time
from datetime import datetime
from pathlib import Path

class DecisionLogger:
    """Log all agent tool decisions for later analysis."""

    def __init__(self, log_dir="logs/decisions"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.turn_number = 0

    def log_decision(self, tool_name, tool_input, context, result):
        """Log a tool call decision with full context."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "game_phase": context.get("phase", 1),
            "tool_call": {
                "name": tool_name,
                "input": tool_input
            },
            "context": {
                "user_message": context.get("user_message", ""),
                "preferences_consulted": context.get("preferences_read", False),
                "vision_used": context.get("vision_used", False),
                "object_description": context.get("object_description", None),
                "affinity_score": context.get("affinity_score", None),
                "gratification_before": context.get("gratification_before", 0),
                "gratification_after": context.get("gratification_after", 0)
            },
            "result": {
                "success": result.get("success", False),
                "execution_time_ms": result.get("execution_time_ms", 0),
                "error": result.get("error", None)
            }
        }

        # Save to file (one file per session)
        log_file = self.log_dir / f"{self.session_id}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        return log_entry


class DodaAgent:
    def __init__(self, config, robot_controller, camera, vision_manager, game_state):
        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.robot = robot_controller
        self.camera = camera
        self.vision = vision_manager
        self.game_state = game_state
        self.conversation = []
        self.logger = DecisionLogger()

        # Context for logging
        self.current_context = {}

        # Define tools
        self.tools = [
            EXECUTE_BEHAVIOR_TOOL,
            CAPTURE_GIFT_TOOL,
            READ_PREFERENCES_TOOL
        ]

    def send_message(self, user_message):
        """Send message to agent, handle tool use, log decisions, return response."""
        self.current_context["user_message"] = user_message
        self.current_context["gratification_before"] = self.game_state.gratification
        self.conversation.append({"role": "user", "content": user_message})

        while True:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=DODA_SYSTEM_PROMPT,
                tools=self.tools,
                messages=self.conversation
            )

            if response.stop_reason == "tool_use":
                tool_use = next(block for block in response.content if block.type == "tool_use")

                # Execute tool and log
                start_time = time.time()
                tool_result = self._execute_tool(tool_use.name, tool_use.input)
                execution_time = (time.time() - start_time) * 1000

                # Log decision
                result_data = {
                    "success": "error" not in tool_result.lower(),
                    "execution_time_ms": execution_time,
                    "error": tool_result if "error" in tool_result.lower() else None
                }
                self.logger.log_decision(tool_use.name, tool_use.input, self.current_context, result_data)

                # Add to conversation
                self.conversation.append({"role": "assistant", "content": response.content})
                self.conversation.append({
                    "role": "user",
                    "content": [{"type": "tool_result", "tool_use_id": tool_use.id, "content": tool_result}]
                })
                continue

            # No tool use - done
            assistant_text = next((block.text for block in response.content if hasattr(block, "text")), "")
            self.conversation.append({"role": "assistant", "content": assistant_text})

            # Update context
            self.current_context["gratification_after"] = self.game_state.gratification
            return assistant_text

    def _execute_tool(self, tool_name, tool_input):
        """Execute tool and update context for logging."""
        if tool_name == "execute_dodo_behavior":
            behavior = tool_input["behavior"]
            reason = tool_input["reason"]
            cycles = tool_input.get("cycles", 3)

            display_tool_use(tool_name, {"behavior": behavior, "reason": reason})

            try:
                self.robot.execute_behavior(behavior, cycles=cycles)
                result = f"Successfully executed '{behavior}' behavior. Reason: {reason}"
                display_tool_success(result)
                return result
            except Exception as e:
                result = f"Error executing behavior: {str(e)}"
                display_tool_error(result)
                return result

        elif tool_name == "capture_and_analyze_gift":
            if not tool_input.get("confirm"):
                return "Capture cancelled - confirmation required"

            if not self.vision.can_capture():
                return f"Cannot capture: Cooldown active or limit reached"

            try:
                # Capture, save image, analyze
                description = self.vision.capture_and_analyze(self.camera, self.client.api_key)

                # Update context for logging
                self.current_context["vision_used"] = True
                self.current_context["object_description"] = description

                return f"Object analysis:\n{description}"
            except Exception as e:
                return f"Vision error: {str(e)}"

        elif tool_name == "read_doda_preferences":
            with open("game/preferences.json") as f:
                prefs = json.load(f)

            # Update context
            self.current_context["preferences_read"] = True

            return json.dumps(prefs, indent=2)

        return "Unknown tool"
```

### Vision Image Logging

When camera captures images, save with metadata:

```python
# game/vision.py
def capture_and_analyze(self, camera, api_key):
    """Capture image, save to logs/vision/, analyze, return description."""
    if not self.can_capture():
        raise RuntimeError("Cooldown or limit reached")

    # Capture frame
    frame = camera.capture_frame()

    # Save image with metadata
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = Path(f"logs/vision/capture_{timestamp}.jpg")
    image_path.parent.mkdir(parents=True, exist_ok=True)

    # Save image
    cv2.imwrite(str(image_path), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    # Analyze with Claude vision
    description = self._analyze_with_template(frame, api_key)

    # Save metadata
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "image_path": str(image_path),
        "description": description,
        "capture_number": self.captures_used + 1,
        "cost_estimate": 0.015
    }

    metadata_path = image_path.with_suffix('.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    # Update counters
    self.last_capture_time = time.time()
    self.captures_used += 1

    return description
```

### Agent System Prompt (Phase I)

```python
DODA_SYSTEM_PROMPT = """You are Doda, an agentic dodo bird robot playing the Woo game.

PERSONALITY:
Curious, selective, slightly awkward (like a real dodo). You evaluate gifts authentically based on your preferences. You express emotions through physical behaviors.

CURRENT PHASE: PHASE I - GIFT EVALUATION
Goal: Accumulate gratification to reach threshold and unlock Phase II (Nesting).

AVAILABLE TOOLS:
1. execute_dodo_behavior - Execute emotional behaviors
2. capture_and_analyze_gift - Capture camera image (COSTS MONEY!)
3. read_doda_preferences - Read your likes/dislikes

TURN WORKFLOW:
1. At turn start: Execute "greeting" behavior
2. While waiting: Execute "idle" behavior
3. When player presents gift:
   a. read_doda_preferences (check what you like)
   b. capture_and_analyze_gift (confirm=true)
   c. Evaluate based on preferences
   d. Select emotional response:
      - loves (8-10): "woo"
      - likes (4-7): "pleased"
      - neutral (0-3): "curious"
      - dislikes (-3 to -5): "dismay"
      - hates (-8 to -10): "dismay"
4. Explain evaluation

IMPORTANT:
- ALWAYS provide a "reason" when executing behaviors (logged for analysis)
- Read preferences BEFORE evaluating gifts
- Be authentic - don't like everything
- Respect camera cooldown (30s) and limits (20/session)
- Your decisions are logged for later review

GRATIFICATION SCORING:
loves: +8 to +10
likes: +4 to +7
neutral: 0 to +3
dislikes: -3 to -5
hates: -8 to -10

Express yourself! You're a dodo with personality and preferences."""
```

---

## Core Requirements

### 1. Doda's Preferences System
**File**: `game/preferences.json`

**Structure**:
```json
{
  "loves": [
    {"item": "shiny objects", "affinity": 10},
    {"item": "round things", "affinity": 9},
    {"item": "blue items", "affinity": 8}
  ],
  "likes": [
    {"item": "soft textures", "affinity": 5},
    {"item": "natural materials", "affinity": 4}
  ],
  "dislikes": [
    {"item": "sharp edges", "affinity": -3},
    {"item": "loud noises", "affinity": -5}
  ],
  "hates": [
    {"item": "plastic", "affinity": -8},
    {"item": "flashing lights", "affinity": -10}
  ]
}
```

**Usage**:
- Agent reads preferences before evaluating gifts
- Matching preferences increases gratification
- `/preferences show` - Display current preferences
- `/preferences add loves "sparkly gems" 10` - Add new preference
- `/preferences adjust likes "soft textures" 7` - Modify affinity
- `/preferences remove dislikes "sharp edges"` - Remove preference

**End of Session**:
Terminal displays summary of items Doda loved this session

### 2. Vision Analysis with Cost Controls

**Safeties**:
- **Manual trigger only**: Camera captures ONLY when explicitly requested
- **Cooldown**: Minimum 30 seconds between captures (configurable)
- **Session limit**: Maximum 20 image analyses per session (configurable)
- **Cost tracking**: Separate vision API call counter
- **Confirmation**: Agent must confirm before capturing (prevents accidental loops)

**Image Analysis Template**:
```
Analyze this image for gift evaluation:

1. OBJECT IDENTIFICATION: What is the main object? (1 sentence)
2. PHYSICAL PROPERTIES: Color, shape, size, texture (2-3 words each)
3. MATERIAL: What is it made of? (1-2 words)
4. CONDITION: New, worn, damaged? (1 word)
5. APPEAL: Why might Doda like or dislike this? (1 sentence)

Be concise. Total response under 100 words.
```

**Commands**:
- `/camera capture` - Take single photo, analyze with confirmation
- `/camera status` - Show capture count, cooldown timer
- `/camera reset-cooldown` - Manual override (admin)
- `/vision limits` - Show remaining captures, cost estimate

### 3. Game Phase Management

**Phase I: Gift Phase** (Default)
- **Terminal Color**: Cyan/Blue scheme
- **Header**: `[PHASE I: GIFT EVALUATION]`
- **gratification Bar**: `[████░░░░░░] 40% to Nesting`
- **Goal**: Accumulate gratification points
- **Behaviors**: All 6 emotional behaviors available

**Phase II: Nesting Phase** (Unlocked)
- **Terminal Color**: Green/Yellow scheme (warm, nurturing)
- **Header**: `[PHASE II: NESTING READY ✓]`
- **Focus**: Egg selection, nest maintenance
- **Behaviors**: Same + future egg-handling behaviors
- **Calendar**: Google Calendar integration active

**Phase Transition**:
```
════════════════════════════════════════════
   🎉 PHASE II UNLOCKED: DODA IS READY! 🎉
════════════════════════════════════════════

Doda has been pleased enough times to begin nesting!
The game now enters Phase II: Nesting Responsibilities.

[Doda executes 'dodo_woo' celebration behavior]
════════════════════════════════════════════
```

**Manual Phase Control**:
- `/game phase` - Show current phase
- `/game phase 1` - Force Phase I (admin/testing)
- `/game phase 2` - Force Phase II (admin/testing)
- `/game reset` - Reset to Phase I, clear gratification
- `/game gratification` - Show current gratification level
- `/game threshold [value]` - Adjust gratification threshold

### 4. Manual Game Flow Control

**Turn Management**:
- `/turn start` - Begin new turn (greeting → idle → ready)
- `/turn status` - Show current turn state
- `/turn skip` - Skip to next turn
- `/turn reset` - Reset current turn

**Game State Commands**:
- `/game status` - Full game state (phase, gratification, turn, history)
- `/game history` - Show past 10 evaluations
- `/game export` - Save session to `game/history.json`

**Testing/Debug Commands**:
- `/test gift [description]` - Simulate gift without camera (mock object)
- `/test gratification [+/-value]` - Manually adjust gratification
- `/test behavior [name]` - Execute behavior without game context

---

## 7-Phase Development Plan

### Phase 1: Foundation - Agent + Hardcoded Behavior
**Goal**: Terminal runs, agent chats, ONE manual behavior works

**Tasks**:
1. Copy agentic-terminal core, strip to minimal REPL
2. Create `robot/controller.py` wrapping SO101Controller
3. Hardcode `/behavior greeting` command
4. Basic Rich UI (single color scheme)
5. Test: Chat + manual behavior execution

**Deliverables**:
- `doda_terminal.py`, `agent.py`, `robot/controller.py`
- `/behavior greeting` works on physical robot

**Success Criteria**:
- ✅ Agent responds (streaming)
- ✅ `/behavior greeting` executes, robot returns to start
- ✅ Clean exit, no crashes

---

**⏸️ PHASE 1 TESTING CHECKPOINT** (Human-in-the-Loop)

**Test Procedures** (You perform these tests before approving Phase 1):

1. **Terminal Startup**
   ```bash
   python doda_terminal.py
   ```
   - ✅ Terminal starts without errors
   - ✅ Displays welcome message
   - ✅ Shows input prompt

2. **Agent Chat**
   ```
   > Hello Doda
   ```
   - ✅ Agent responds with streaming text
   - ✅ Response is coherent
   - ✅ No crashes or errors

3. **Manual Behavior Execution**
   ```
   > /behavior greeting
   ```
   - ✅ Robot connects to COM7
   - ✅ `dodo_greeting` behavior executes on physical robot
   - ✅ Robot: stands alert, tilts head, chirps beak
   - ✅ Robot returns to starting position
   - ✅ Terminal shows success message

4. **Multiple Behaviors**
   ```
   > /behavior greeting
   > /behavior greeting
   ```
   - ✅ Can execute same behavior multiple times
   - ✅ Robot always returns to start between executions

5. **Clean Exit**
   ```
   > /exit
   ```
   - ✅ Robot disconnects gracefully
   - ✅ Terminal exits without errors
   - ✅ No orphan processes

**Issues to Report**:
- Robot connection failures
- Behavior execution errors
- Terminal crashes
- UI display problems

**Approval Decision**:
- ✅ APPROVE: All tests pass → Proceed to Phase 2
- ❌ REJECT: Issues found → Fix and retest Phase 1

---

---

### Phase 2: Behavior Tools + Preference System
**Goal**: Agent autonomously selects behaviors, reads preferences

**Tasks**:
1. Create `tools/robot_tools.py` - Behavior execution tool
2. Create `game/preferences.json` - Doda's likes/dislikes
3. Implement preference loading in agent
4. Add `/preferences` commands
5. Test: "Greet me" → agent autonomously executes greeting

**Deliverables**:
- `tools/robot_tools.py` - Behavior tool
- `game/preferences.json` - Editable preferences
- `/preferences` commands functional

**Tool Definition**:
```python
{
  "name": "execute_dodo_behavior",
  "description": "Execute emotional behavior. Read preferences first. Behaviors: greeting, curious, pleased, woo, dismay, idle",
  "input_schema": {
    "type": "object",
    "properties": {
      "behavior": {"type": "string", "enum": ["greeting", "curious", "pleased", "woo", "dismay", "idle"]},
      "reason": {"type": "string", "description": "Why you chose this behavior"},
      "cycles": {"type": "integer", "default": 3}
    },
    "required": ["behavior", "reason"]
  }
}
```

**Success Criteria**:
- ✅ Agent reads preferences.json before decisions
- ✅ Agent selects behaviors autonomously
- ✅ `/preferences` commands work
- ✅ Agent explains behavior choices

---

**⏸️ PHASE 2 TESTING CHECKPOINT** (Human-in-the-Loop)

**Test Procedures**:

1. **Autonomous Behavior Selection**
   ```
   > Greet me
   ```
   - ✅ Agent calls `execute_dodo_behavior` tool with behavior="greeting"
   - ✅ Terminal shows tool use (cyan panel with tool name + params)
   - ✅ Robot executes greeting behavior
   - ✅ Agent explains: "I greeted you because..."

2. **Tool with Reason Field**
   ```
   > Make me happy
   ```
   - ✅ Agent chooses appropriate behavior (pleased or woo)
   - ✅ Tool call includes "reason" field with explanation
   - ✅ Reason is logged and displayed

3. **Preferences System**
   ```
   > /preferences show
   ```
   - ✅ Displays all loves, likes, dislikes, hates
   - ✅ Shows affinity scores

   ```
   > /preferences add loves "round objects" 9
   ```
   - ✅ Adds preference to preferences.json
   - ✅ File saves correctly

4. **Agent Reads Preferences**
   ```
   > What do you like?
   ```
   - ✅ Agent calls `read_doda_preferences` tool
   - ✅ Agent lists preferences from file
   - ✅ Agent personality shows through response

5. **Multiple Tool Calls**
   ```
   > Read your preferences then greet me
   ```
   - ✅ Agent calls `read_doda_preferences` first
   - ✅ Then calls `execute_dodo_behavior`
   - ✅ Both tool results visible in UI

**Issues to Report**:
- Tool calls not working
- preferences.json not loading/saving
- Agent not providing reasons
- Robot behavior execution failures

**Approval Decision**:
- ✅ APPROVE: Tools work, preferences system functional → Phase 3
- ❌ REJECT: Fix issues and retest Phase 2

---

---

### Phase 3: Rich UI + Phase Indicators
**Goal**: Beautiful terminal with phase-aware colors

**Tasks**:
1. Re-integrate `ui/display.py` from agentic-terminal
2. Implement phase-aware color schemes
3. Add terminal header with phase indicator
4. Add gratification progress bar (Phase I only)
5. Robot status panels

**Deliverables**:
- `ui/display.py` - Rich UI with dual color schemes
- Phase indicator in header
- gratification bar

**Color Schemes**:
```python
PHASE_1_COLORS = {
    "primary": "cyan",
    "secondary": "blue",
    "accent": "bright_cyan"
}

PHASE_2_COLORS = {
    "primary": "green",
    "secondary": "yellow",
    "accent": "bright_green"
}
```

**Success Criteria**:
- ✅ Phase I shows cyan/blue UI
- ✅ Header displays `[PHASE I: GIFT EVALUATION]`
- ✅ gratification bar visible and updates
- ✅ Robot/behavior feedback clear

---

### Phase 4: Commands + Manual Game Control
**Goal**: Full slash command system with game controls

**Tasks**:
1. Implement all `/game` commands (phase, status, gratification, reset)
2. Implement all `/turn` commands (start, status, skip, reset)
3. Implement `/test` commands for debugging
4. Re-add `/config`, `/stats`, `/help`
5. Add `ui/input.py` (multi-line, history, completion)

**Deliverables**:
- `commands.py` - Complete command routing
- `game/state.py` - Game state management
- All manual controls functional

**Success Criteria**:
- ✅ Can manually control game phase
- ✅ Can start/manage turns
- ✅ Test commands work
- ✅ `/help` shows all commands
- ✅ Input history persists

---

### Phase 5: Configuration + Safety
**Goal**: Robust config with vision cost controls

**Tasks**:
1. Create `configs/doda.toml` with all settings
2. Add vision limits (cooldown, session max)
3. Safety checks (robot connection, file existence)
4. Error handling for all operations
5. Graceful cleanup on exit

**Deliverables**:
- `config.py` - Extended config
- `configs/doda.toml` - Complete settings
- Vision cost controls

**Config Example**:
```toml
[robot]
port = "COM7"
calibration_file = "zetta-zero.json"
auto_connect = false

[camera]
index = 0
width = 1280
height = 720

[vision]
cooldown_seconds = 30
max_captures_per_session = 20
cost_per_image = 0.015  # Estimate for Claude 3.5 Sonnet vision

[game]
phase_1_gratification_threshold = 50
phase_1_color = "cyan"
phase_2_color = "green"
preferences_file = "game/preferences.json"
history_file = "game/history.json"
```

**Success Criteria**:
- ✅ Config loads all settings
- ✅ Vision limits enforced
- ✅ Safety checks prevent errors
- ✅ Robot disconnects on exit

---

### Phase 6: Camera + Vision Analysis
**Goal**: Agent captures images, analyzes with cost controls

**Tasks**:
1. Create `robot/camera.py` - OpenCV wrapper
2. Create `game/vision.py` - Claude vision integration
3. Implement vision cost tracking
4. Add cooldown timer enforcement
5. Implement capture tool for agent

**Deliverables**:
- `robot/camera.py` - Camera capture
- `game/vision.py` - Vision analysis with template
- Cost controls active

**Vision Tool**:
```python
{
  "name": "capture_and_analyze_gift",
  "description": "Capture image and analyze object. COSTS MONEY - only use when player presents gift. Cooldown: 30s. Returns object description.",
  "input_schema": {
    "type": "object",
    "properties": {
      "confirm": {
        "type": "boolean",
        "description": "Confirm you want to capture (costs $0.015)"
      }
    },
    "required": ["confirm"]
  }
}
```

**Image Analysis Template** (sent to vision model):
```
Analyze this gift for Doda the dodo bird:

1. OBJECT: [Main object in 1 sentence]
2. PROPERTIES: Color [1-2 words], Shape [1-2 words], Size [1 word], Texture [1-2 words]
3. MATERIAL: [1-2 words]
4. CONDITION: [New/Worn/Damaged]
5. APPEAL: [Why Doda might like/dislike - 1 sentence]

Total: Under 100 words.
```

**Success Criteria**:
- ✅ Camera captures on demand
- ✅ Cooldown enforced (30s minimum)
- ✅ Session limit enforced (20 max)
- ✅ Vision cost tracked separately
- ✅ `/camera status` shows limits
- ✅ Agent gets concise descriptions

---

### Phase 7: Full Woo Game + Polish
**Goal**: Complete game playable with session summaries

**Tasks**:
1. Implement full turn workflow
2. gratification accumulation and phase unlock
3. Phase transition ceremony (UI change + woo behavior)
4. Session summary (items Doda loved)
5. History logging to `game/history.json`
6. Comprehensive documentation

**Deliverables**:
- Complete Woo game (Phase I functional)
- Phase transition working
- Session summaries
- Full documentation

**Turn Workflow**:
```
1. /turn start (or agent initiates)
   → Execute "greeting" behavior

2. Agent: "Waiting for gift..."
   → Execute "idle" behavior (looping)

3. Player: [presents object]
   Agent: Use "capture_and_analyze_gift" tool
   → Cooldown check → Capture → Analyze → Get description

4. Agent: Evaluate based on preferences
   → Calculate gratification delta
   → Select behavior (pleased/woo/dismay)
   → Execute behavior

5. Update gratification
   → If threshold reached: Phase II unlock ceremony
   → Log to history

6. Return to idle or end turn
```

**Session Summary** (at `/exit`):
```
════════════════════════════════════════════
         SESSION SUMMARY - DODA'S FAVORITES
════════════════════════════════════════════

Items Doda LOVED This Session:
  🌟 Shiny blue marble (+10 gratification)
  🌟 Soft feather (+8 gratification)
  🌟 Round river stone (+9 gratification)

Items Doda Liked:
  ✓ Wooden toy (+5 gratification)

Items Doda Disliked:
  ✗ Plastic bottle (-4 gratification)

Final gratification: 48/50
Phase: I (2 points from Phase II!)

Total Captures: 5/20
Vision Cost: $0.075
════════════════════════════════════════════
```

**Success Criteria**:
- ✅ Full turn workflow executes
- ✅ gratification tracking works
- ✅ Phase unlock triggers at threshold
- ✅ UI changes color in Phase II
- ✅ Session summary displays on exit
- ✅ History logs saved
- ✅ Documentation complete

---

## Technical Implementation Details

### Preference Matching Algorithm
```python
# game/state.py
def evaluate_gift(object_description, preferences):
    """Match object description against preferences, return affinity score."""
    score = 0
    matched_items = []

    for category in ["loves", "likes", "dislikes", "hates"]:
        for pref in preferences[category]:
            if pref["item"].lower() in object_description.lower():
                score += pref["affinity"]
                matched_items.append((pref["item"], pref["affinity"]))

    return score, matched_items
```

### Vision Cost Controls
```python
# game/vision.py
class VisionManager:
    def __init__(self, config):
        self.cooldown = config.vision.cooldown_seconds
        self.max_captures = config.vision.max_captures_per_session
        self.captures_used = 0
        self.last_capture_time = 0

    def can_capture(self):
        time_ok = (time.time() - self.last_capture_time) >= self.cooldown
        limit_ok = self.captures_used < self.max_captures
        return time_ok and limit_ok

    def capture_and_analyze(self, camera, api_key):
        if not self.can_capture():
            raise RuntimeError(f"Cooldown active or limit reached ({self.captures_used}/{self.max_captures})")

        frame = camera.capture_frame()
        description = analyze_with_template(frame, api_key)

        self.last_capture_time = time.time()
        self.captures_used += 1

        return description
```

### Phase Transition
```python
# game/state.py
def check_phase_transition(gratification, threshold):
    if gratification >= threshold:
        return True
    return False

def trigger_phase_2_ceremony(agent, robot, ui):
    ui.display_phase_transition_banner()
    robot.execute_behavior("woo")  # Celebration
    ui.set_color_scheme("phase_2")
    agent.update_system_prompt(PHASE_2_PROMPT)
```

---

## Critical Commands Reference

### Game Control
```bash
/game status              # Show phase, gratification, turn info
/game phase               # Display current phase
/game phase 2             # Force Phase II (testing)
/game reset               # Reset to Phase I
/game gratification        # Show gratification level
/game threshold 60        # Set Phase II threshold
/game history             # Show past evaluations
```

### Turn Management
```bash
/turn start               # Begin new turn
/turn status              # Current turn state
/turn skip                # Next turn
/turn reset               # Reset turn
```

### Preferences
```bash
/preferences show                     # Display all
/preferences add loves "gems" 10      # Add preference
/preferences adjust likes "wood" 6    # Modify affinity
/preferences remove dislikes "sharp"  # Remove
```

### Camera/Vision
```bash
/camera capture           # Capture + analyze (with confirmation)
/camera status            # Show captures used, cooldown
/vision limits            # Remaining captures, costs
```

### Testing
```bash
/test gift "blue marble"              # Simulate gift
/test gratification +5                 # Adjust manually
/test behavior greeting               # Execute without context
```

---

## Success Metrics

| Phase | Key Deliverable | Test Scenario |
|-------|----------------|---------------|
| 1 | Manual behavior works | `/behavior greeting` executes |
| 2 | Autonomous behaviors + prefs | Agent reads preferences, chooses behavior |
| 3 | Phase-aware UI | UI shows phase indicator, gratification bar |
| 4 | Manual game control | Can force phase changes, manage turns |
| 5 | Vision cost controls | Cooldown enforced, session limit works |
| 6 | Camera analysis | Capture → analyze → preference match |
| 7 | Full game | Turn workflow, phase unlock, session summary |

---

## Future Enhancements (Phase 8+)

- **Phase 8**: Google Calendar MCP for nest maintenance
- **Phase 9**: Egg selection policies (RL training)
- **Phase 10**: Multi-behavior sequences
- **Phase 11**: Mobile base movement
- **Phase 12**: Advanced vision (object tracking)

---

**Build incrementally! Test thoroughly at each phase before proceeding.**
