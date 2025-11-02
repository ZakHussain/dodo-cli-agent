# Phase 1 Plan - Foundation

**Status**: ✅ COMPLETED

**Objective**: Build minimal terminal with agent chat and manual behavior execution.

---

## Goals

1. Create basic terminal application structure
2. Integrate Claude agent for conversation
3. Wrap SO-101 robot controller
4. Implement manual behavior command (`/behavior greeting`)
5. Test end-to-end: terminal → agent → robot

---

## Implementation Details

### Files Created

| File | Purpose |
|------|---------|
| `doda_terminal.py` | Main entry point, terminal loop, command routing |
| `agent.py` | Simple Claude agent wrapper (no tools yet) |
| `robot/controller.py` | SO-101 robot wrapper with lazy connection |
| `robot/__init__.py` | Python package marker |
| `requirements.txt` | Dependencies (anthropic, rich, feetech-servo-sdk) |
| `.env.template` | API key template |
| `README.md` | Phase 1 documentation |

### Architecture

```
┌─────────────────────────────────────────┐
│         doda_terminal.py                │
│  - Terminal UI (Rich)                   │
│  - Input loop                           │
│  - Command routing                      │
└─────────────┬───────────────────────────┘
              │
      ┌───────┴────────┐
      │                │
┌─────▼─────┐   ┌─────▼──────────┐
│  agent.py │   │ robot/         │
│           │   │ controller.py  │
│ - Claude  │   │                │
│ - System  │   │ - SO101 wrap   │
│   prompt  │   │ - Behaviors    │
│ - History │   │ - Lazy connect │
└───────────┘   └────────┬───────┘
                         │
                  ┌──────▼─────────────┐
                  │  so101_control.py  │
                  │  (existing)        │
                  └────────────────────┘
```

### System Prompt (Phase 1)

```
You are Doda, a curious dodo bird robot.

You are friendly, curious, and slightly awkward (like a real dodo).
You live in a cave and are learning about the world.

In future phases, you'll be able to express emotions through
physical movements, but for now you can only chat.

Keep responses concise and in-character. Show your dodo personality!
```

### Commands Implemented

- `/help` - Show help message
- `/behavior greeting` - Execute greeting behavior on robot
- `/exit` - Exit terminal

### Robot Controller Features

**Lazy Connection**: Robot connects only when needed (first behavior execution)

**Behavior Mapping**:
```python
{
    "greeting": "dodo_greeting",
    "head_bob": "dodo_head_bob",
    "curious": "dodo_head_bob",  # Alias
    "pleased": "dodo_pleased",
    "woo": "dodo_woo",
    "dismay": "dodo_dismay",
    "idle": "dodo_idle"
}
```

**Return Format**:
```python
{
    "success": bool,
    "duration": float,  # seconds
    "error": str or None
}
```

---

## Testing Checkpoint

**⏸️ PHASE 1 TESTING CHECKPOINT** (Human-in-the-Loop)

### Test Procedures

1. **Terminal Startup**
   ```bash
   python doda_terminal.py
   ```
   - ✅ Terminal starts without errors
   - ✅ Welcome banner displays with dodo emoji 🦤
   - ✅ Command prompt appears

2. **Agent Chat**
   - Type: `Hello Doda!`
   - ✅ Agent responds with in-character message
   - ✅ Response shows Doda personality (curious, friendly)
   - ✅ Response is concise

3. **Manual Behavior Execution**
   ```
   /behavior greeting
   ```
   - ✅ System message shows "Executing greeting behavior..."
   - ✅ Robot connects to COM7 (if first run)
   - ✅ Robot performs greeting (head tilts + chirping beak)
   - ✅ Robot returns to starting position
   - ✅ Success message with duration displayed

4. **Help Command**
   ```
   /help
   ```
   - ✅ Help panel displays
   - ✅ Shows all Phase 1 commands

5. **Clean Exit**
   ```
   /exit
   ```
   - ✅ Goodbye message displays
   - ✅ Robot disconnects cleanly
   - ✅ No error messages

### Success Criteria

- ✅ All tests pass
- ✅ No crashes or exceptions
- ✅ Robot performs behavior correctly
- ✅ Clean startup and shutdown

### Issues to Report

Document any issues:
- Connection failures
- Behavior execution errors
- UI formatting problems
- Agent response quality issues

### Approval Decision

**After testing, make decision:**

- ✅ **APPROVE**: All tests pass → Proceed to Phase 2
- ❌ **REJECT**: Issues found → Document issues, fix, and retest

---

## What's NOT in Phase 1

- ❌ Agent tools (Phase 2)
- ❌ Preferences system (Phase 2)
- ❌ Decision logging (Phase 2)
- ❌ Phase-aware UI colors (Phase 3)
- ❌ Additional slash commands (Phase 4)
- ❌ Camera integration (Phase 5)
- ❌ Vision analysis (Phase 5)
- ❌ Game state tracking (Phase 6)
- ❌ Two-phase game loop (Phase 7)

---

## Dependencies

```
anthropic==0.34.0      # Claude API
python-dotenv==1.0.0   # Environment variables
rich==13.7.0           # Terminal UI
feetech-servo-sdk==1.0.0  # Robot control
pyserial==3.5          # Serial communication
```

---

## Notes

- **Robot Port**: Hardcoded to COM7 (will be configurable in Phase 4)
- **Calibration**: Uses `../so101/zetta-zero.json`
- **Lazy Connection**: Robot only connects when first behavior is executed
- **Error Handling**: Basic try/catch, will be enhanced in later phases
- **No Logging**: Decision logging will be added in Phase 2

---

## Next Phase

**Phase 2**: Agent Tools + Preferences System
- Convert behaviors to agent tools
- Implement decision logging
- Add preferences.json
- Enable agent autonomous behavior selection
