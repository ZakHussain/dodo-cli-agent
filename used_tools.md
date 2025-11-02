# Tool Usage Log

This file tracks all tools used by the Doda Terminal agent and their purposes.

## Format
- **Tool Name**: Name of the tool/function
- **Reason**: Why this tool was used
- **Timestamp**: When it was used (session-based)

---

## Tool Log

### Session: Behavior Flow Fixes

#### 1. Read
- **File**: `c:\Users\hussa\Desktop\zetta-projects\doda-terminal\used_tools.md`
- **Reason**: Check if tool tracking file exists
- **Result**: File did not exist, creating new one

#### 2. Write
- **File**: `c:\Users\hussa\Desktop\zetta-projects\doda-terminal\used_tools.md`
- **Reason**: Create initial tool usage tracking file
- **Result**: This file created

---

## Instructions for Updating

Every time a tool is used in the agent system, an entry should be added to this log with:
1. Tool name (e.g., `execute_dodo_behavior`, `capture_and_analyze_gift`)
2. Reason for using it
3. Any relevant parameters or results

This helps track autonomous behavior and debug tool selection issues.

### 2025-11-02 15:30:03
- **Tool**: `execute_dodo_behavior`
- **Input**: ```json
{
  "behavior_name": "greeting",
  "reason": "First interaction with human bringing a gift"
}
```

### 2025-11-02 15:30:16
- **Tool**: `capture_and_analyze_gift`
- **Input**: ```json
{}
```

### 2025-11-02 15:30:40
- **Tool**: `execute_dodo_behavior`
- **Input**: ```json
{
  "behavior_name": "dismay",
  "reason": "Negative reaction to scary human feet in the photo - affinity score -10"
}
```
