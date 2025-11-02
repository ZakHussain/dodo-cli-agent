# Doda Terminal - Phase 1

**Agentic Dodo Robot Terminal** - Gift Evaluation Game

## Phase 1: Foundation

Basic terminal with agent chat and manual behavior execution.

### Features
- Chat with Doda (Claude-powered AI agent)
- Manual behavior execution (`/behavior greeting`)
- Clean Rich terminal interface

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

3. **Connect robot:**
   - Ensure SO-101 robot arm is connected to COM7
   - Calibration file: `../so101/zetta-zero.json`

### Run

```bash
python doda_terminal.py
```

### Commands

- `/help` - Show help
- `/behavior greeting` - Execute greeting behavior on robot
- `/exit` - Exit terminal

Regular messages (without `/`) are sent to Doda for conversation.

### Testing Phase 1

Follow the testing procedures in `DODA_TERMINAL_PROMPT.md` Phase 1 Testing Checkpoint section.

**Success Criteria:**
- ✅ Agent responds with streaming
- ✅ `/behavior greeting` executes on physical robot
- ✅ Robot returns to starting position
- ✅ Clean exit

### Next Phases

- Phase 2: Behavior tools + preferences system (agent autonomy)
- Phase 3: Rich UI + phase indicators
- Phase 4: Commands + manual game control
- Phase 5: Configuration + safety
- Phase 6: Camera + vision analysis
- Phase 7: Full Woo game loop

---

**Built for the Woo Game** - See `../DODA_TERMINAL_PROMPT.md` for complete specifications.
