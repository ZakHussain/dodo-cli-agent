# Doda Terminal - Competition Ready! 🏆

## Final Configuration

**Status**: Ready for competition demo
**Date**: 2025-11-02

## Game Settings

- **Win Threshold**: +15 gratification
- **Lose Threshold**: -10 gratification
- **Behavior Cycles**: 1 cycle (fast execution)
- **Camera**: Index 1
- **Robot Port**: COM8 (LeKiwi)

## Streamlined Behavior Flow

### 1. Initial Greeting (First Interaction Only)
- Executes `dodo_greeting` behavior
- Doda says a kind welcome message
- Only happens ONCE at the start

### 2. Gift Presentation
User says: "I have a gift for you"

**Doda's Response Flow**:
1. Acknowledges briefly
2. Immediately calls `capture_and_analyze_gift` tool
3. **During capture**: Runs `idle` behavior (1 cycle) + prints "Give me a moment to think..."
4. Vision analyzes image (Step 1/2)
5. Preferences evaluated (Step 2/2)

### 3. Reaction Based on Score

**Positive Score (> 0)**:
- Executes `pleased` OR `head_bob` behavior
- Happy message explaining what she likes
- Shows current gratification level

**Negative Score (< 0)**:
- Executes `dismay` behavior
- Disappointed message explaining what she dislikes
- Shows current gratification level

**Neutral Score (= 0)**:
- No behavior executed
- Explains neutral feelings

### 4. Win/Lose Conditions

**Win (+15 gratification)**:
- System automatically executes `dodo_woo` behavior
- Big "WOOOOOOO!!!!" ASCII art displays
- Game over screen

**Lose (-10 gratification)**:
- System automatically executes `dodo_dismay` behavior
- All torques disable (robot goes limp)
- Red "FOREVER ALONE YOU ARE" screen
- Game over

## Quick Test Commands

```bash
# Start the game
python doda_terminal.py

# Test win condition immediately
> /test-win

# Reset and test lose condition
> /reset
> /test-lose

# Normal gameplay
> /reset
> I have a gift for you
[Present object to camera]
```

## File Outputs

### Photos
- **Location**: `game/gift_photos/gift_TIMESTAMP.jpg`
- Saved automatically on each capture

### Descriptions
- **Location**: `game/gift_photos/image_descriptions/gift_TIMESTAMP.json`
- Contains: analysis, affinity score, reason, matched preferences

### Game State
- **Location**: `game/save_state.json`
- Auto-saves after each gift

## Preferences Summary

**Doda Loves** (+8 to +10):
- Dodo birds (especially large, colorful beaks!)
- Eggs, nests
- Large beaks, colorful beaks

**Doda Likes** (+4 to +7):
- Feathers, plants, food
- Toys, round objects

**Doda Dislikes** (-3 to -5):
- Sharp objects, loud things
- Metal, dirty items

**Doda Hates** (-8 to -10):
- Predators, snakes
- Fire, cages

## Competition Demo Script

### Setup (Pre-Demo)
1. Connect LeKiwi robot to COM8
2. Connect USB camera (index 1)
3. Start terminal: `python doda_terminal.py`
4. Verify camera and robot connected

### Demo Flow

**Scene 1: Introduction**
```
> Hello!
[Doda executes greeting behavior]
[Doda: "Hi! I'm Doda, a curious dodo bird..."]
```

**Scene 2: First Gift (Positive)**
```
> I have a gift for you
[Doda: "Oh! A gift? Let me see..."]
[Tool: capture_and_analyze_gift]
  "Give me a moment to think..."
  [Idle behavior plays]
  [Step 1/2] Analyzing image...
  [Step 2/2] Evaluating preferences...
[Doda executes pleased/head_bob]
[Doda: "Oh wow! I love this because... Gratification: +7"]
```

**Scene 3: Second Gift (Positive - approaching win)**
```
> I brought another one
[Same flow]
[Doda: "Another wonderful gift! Gratification: +14"]
```

**Scene 4: Third Gift (Positive - WIN!)**
```
> One more gift for you
[Same flow]
[Gratification reaches +15]
[System executes dodo_woo automatically]
[Giant "WOOOOOOO!!!!" screen displays]
[Doda: "I'm so happy!!!"]
```

**Alternative: Lose Scenario**
```
> /reset
[Present negative items like sharp objects]
[Doda executes dismay each time]
[At -10: Robot goes limp, red "FOREVER ALONE YOU ARE" screen]
```

## Tips for Best Demo

1. **Pre-select objects**: Have positive items ready (colorful toys, dodo pictures)
2. **Test lighting**: Ensure camera can see objects clearly
3. **Keep it moving**: Fast-paced, 1-cycle behaviors keep energy high
4. **Show variety**: Demo both win and lose conditions if time allows
5. **Emphasize AI**: Point out vision analysis and preference reasoning

## Technical Highlights

- **Two-step vision**: Separate image analysis + preference evaluation
- **Claude Sonnet 4.5**: Latest vision model
- **Claude Sonnet 4**: Reasoning for preferences
- **Real-time adaptation**: Agent uses tools autonomously
- **Physical embodiment**: Robot expresses emotions through movement

## Troubleshooting

**Camera not detecting**:
```bash
python robot/camera.py
```

**Robot not connecting**:
- Check COM8 in Device Manager
- Verify `lekiwi-calibrated.json` exists

**Vision errors**:
- Check ANTHROPIC_API_KEY in `.env`
- Verify internet connection

## Files Modified for Competition

1. `game/state.py` - Thresholds: +15 win, -10 lose
2. `doda_terminal.py` - Win screen: "WOOOOOOO!!!!"
3. `agent.py` - Streamlined workflow in system prompt
4. `tools/robot_tools.py` - Idle during capture, save descriptions
5. `robot/presets/dodo_idle.py` - 1 cycle default
6. `robot/presets/dodo_head_bob.py` - 1 cycle default

---

**Ready to win! Good luck at the competition! 🦤🏆**
