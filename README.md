# Doda Terminal - Phase 2

**Agentic Dodo Robot Terminal** - Gift Evaluation Game: WOO!

## Phase 2: Complete Game Implementation

Full autonomous game with agent tools, vision, preferences, and win/lose conditions.

### Features
- **Autonomous Agent**: Doda uses 5 tools to interact with the world
- **Gift Evaluation**: Camera-based vision analysis with affinity scoring
- **Preferences System**: Doda loves dodo birds, large beaks, and colorful things
- **Win Condition**: Reach +30 gratification → Execute dodo_woo → "WOO!!" display
- **Lose Condition**: Drop to -30 gratification → Robot goes limp → "FOREVER ALONE YOU ARE"
- **LeKiwi Platform**: SO-101 arm + 3 omniwheel base for rotation
- **Rich Terminal UI**: Colored panels, gratification bar, ASCII art endings

### Architecture

```
doda-terminal/
├── doda_terminal.py        # Main entry point
├── agent.py                # Doda AI agent with tool support
├── robot/
│   ├── controller.py       # Robot controller (behaviors, rotation, positions)
│   ├── camera.py           # Camera auto-detection
│   └── presets/            # Dodo behavior presets
├── game/
│   ├── state.py            # Game state & gratification tracking
│   └── preferences.py      # Preferences & affinity scoring
├── tools/
│   └── robot_tools.py      # 5 tools for agent
└── calibration-files/
    └── lekiwi-calibrated.json
```

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create .env file:**
   ```bash
   cp .env.template .env
   ```
   Then edit `.env` and add your Anthropic API key.

3. **Connect hardware:**
   - LeKiwi robot (SO-101 + wheels) on COM8
   - USB camera (auto-detected at indices 0, 1, or 2)
   - Calibration file: `calibration-files/lekiwi-calibrated.json`

4. **Verify camera (optional):**
   ```bash
   python robot/camera.py
   ```

### Run

```bash
python doda_terminal.py
```

### Commands

- `/help` - Show help and available commands
- `/view-gift` - Manually trigger gift analysis
- `/status` - Show current gratification level
- `/reset` - Reset game state
- `/exit` - Exit terminal

Regular messages (without `/`) are sent to Doda for autonomous interaction.

### Agent Tools

Doda has 5 tools for autonomous interaction:

1. **execute_dodo_behavior**: Express emotions through movement
   - greeting, head_bob, curious, pleased, woo, dismay, idle

2. **capture_and_analyze_gift**: Take photo and analyze object
   - Returns description and affinity score
   - Special handling for dodo birds (beak size/color matter!)

3. **read_doda_preferences**: Check what Doda loves/likes/dislikes/hates
   - Helps understand how Doda will react

4. **rotate_base**: Rotate wheeled base to look around
   - Specify degrees and direction
   - Auto-returns to starting position

5. **capture_joint_positions**: Record current arm/wheel positions
   - Get snapshot of current robot state

### Game Rules

- **Starting Gratification**: 0
- **Win Threshold**: +30 (triggers dodo_woo → "WOO!!")
- **Lose Threshold**: -30 (triggers dodo_pleased → limp → "FOREVER ALONE YOU ARE")
- **Affinity Scoring**: -10 to +10 per gift (dodo birds can exceed +10!)
- **Gratification Changes**: Cumulative based on all gifts

### Preferences System

**Loves** (+8 to +10):
- Dodo birds (especially with large, colorful beaks!)
- Eggs, nests
- Large beaks, colorful beaks

**Likes** (+4 to +7):
- Feathers, plants, food
- Toys, round objects

**Dislikes** (-3 to -5):
- Sharp objects, loud things
- Metal, dirty items

**Hates** (-8 to -10):
- Predators, snakes
- Fire, cages

### Testing Phase 2

**Test Scenarios:**

1. **Basic Interaction**:
   - Chat with Doda, verify agent responds
   - Doda should proactively use behaviors to express emotions

2. **Gift Evaluation**:
   - Place object in front of camera
   - Say "I have a gift for you"
   - Verify Doda uses capture_and_analyze_gift tool
   - Check gratification updates

3. **Win Condition**:
   - Present multiple positive gifts (dodo birds, eggs, feathers)
   - Reach +30 gratification
   - Verify dodo_woo executes and "WOO!!" displays

4. **Lose Condition**:
   - Present multiple negative gifts (sharp objects, cages)
   - Drop to -30 gratification
   - Verify dodo_pleased executes, torques disable, "FOREVER ALONE YOU ARE" displays

**Success Criteria:**
- ✅ Agent autonomously uses all 5 tools
- ✅ Gift analysis updates gratification correctly
- ✅ Win condition triggers at +30
- ✅ Lose condition triggers at -30
- ✅ Camera auto-detection works
- ✅ Base rotation functions correctly
- ✅ Game state persists and can reset

### Notes

- Camera vision uses Claude's API for real image analysis and affinity scoring
- Base rotation calibration: ~1.5 seconds per 90 degrees at speed 400
- Preferences stored in `game/doda_preferences.json` (auto-generated)
- Game state saved to `game/save_state.json` (auto-saved on each gift)

---

**Built for the Woo Game** - See `DODA_TERMINAL_PROMPT_V2.md` for complete specifications.
