# 02 - Basic Usage

> **English** | [中文](02_BASIC_USAGE_zh.md)

This chapter covers the core CLI commands, single-instance mode operation, and how to interact with the agent.

---

## Table of Contents

- [Understanding the Two Tracks](#understanding-the-two-tracks)
- [Core CLI Commands](#core-cli-commands)
- [Single-Instance Mode Quick Start](#single-instance-mode-quick-start)
- [Command Cheat Sheet](#command-cheat-sheet)
- [Runtime Markdown Files](#runtime-markdown-files)
- [Common Interaction Examples](#common-interaction-examples)
- [Troubleshooting](#troubleshooting)

---

## Understanding the Two Tracks

PhyAgentOS separates cognition from execution:

- **Track A (Brain)**: `paos agent` or `paos gateway` — plans, reasons, validates actions via Critic
- **Track B (HAL)**: `python hal/hal_watchdog.py` — reads `ACTION.md`, executes via driver, writes back `ENVIRONMENT.md`

They communicate through workspace Markdown files, not direct Python calls.

---

## Core CLI Commands

### `paos onboard`

Initializes or refreshes the workspace and config templates.

```bash
paos onboard
```

Run this after installation, after upgrades, or after switching single/fleet mode.

### `paos agent`

Interactive CLI for single-turn or multi-turn conversation.

```bash
# Interactive mode
paos agent

# Single-turn mode
paos agent -m "look around the room"
```

### `paos gateway`

Long-running service mode with channel integration (Feishu, Slack, etc.), heartbeat, and cron jobs.

```bash
paos gateway
```

Use this when you want the agent to stay online and respond to messages from external channels.

---

## Single-Instance Mode Quick Start

### Step 1: Initialize

```bash
paos onboard
```

### Step 2: Start HAL Watchdog (Track B)

```bash
# Terminal A
python hal/hal_watchdog.py --driver simulation
```

The watchdog will:
- Load the `simulation` driver
- Copy the driver profile to `EMBODIED.md`
- Poll `ACTION.md` periodically
- Execute actions and update `ENVIRONMENT.md`

### Step 3: Start Agent (Track A)

```bash
# Terminal B
paos agent
```

Enter natural language instructions at the prompt.

### Step 4: Observe File Changes

Watch these files to understand the runtime loop:

| File | What to check |
|---|---|
| `EMBODIED.md` | Is the robot profile correctly installed? |
| `ACTION.md` | Did the Agent successfully write an action? |
| `ENVIRONMENT.md` | Did the environment state update after execution? |
| `LESSONS.md` | Were any actions rejected by Critic? |

---

## Command Cheat Sheet

| Goal | Command |
|---|---|
| Initialize workspace | `paos onboard` |
| Interactive agent | `paos agent` |
| Single-turn message | `paos agent -m "..."` |
| Start gateway service | `paos gateway` |
| Start simulation watchdog | `python hal/hal_watchdog.py --driver simulation` |
| Start with custom workspace | `python hal/hal_watchdog.py --workspace <path> --driver <name>` |
| Pass driver config JSON | `python hal/hal_watchdog.py --driver <name> --driver-config <file>` |
| Run pytest | `pytest tests/` |

---

## Runtime Markdown Files

These files are the shared state between Track A and Track B:

| File | Location | Purpose |
|---|---|---|
| `ACTION.md` | Workspace root | Pending action queue |
| `EMBODIED.md` | Workspace root | Robot capabilities, constraints, connection state |
| `ENVIRONMENT.md` | Workspace root | Current scene graph, objects, robot state |
| `LESSONS.md` | Workspace root | Failure experience recorded by Critic |
| `TASK.md` | Workspace root | Multi-step task decomposition state |
| `ORCHESTRATOR.md` | Workspace root | Orchestration layer state |

For fleet mode, see [03 Fleet Mode](03_FLEET_MODE.md).

---

## Common Interaction Examples

### Environment query

```text
What objects are on the table?
```

Verifies: Agent reads `ENVIRONMENT.md`, Watchdog writes it correctly.

### Manipulation task

```text
Pick up the red apple and place it on the tray.
```

Verifies: Target object exists in scene, robot supports `pick_up`/`put_down`, Watchdog executes and clears `ACTION.md`.

### Navigation task

```text
Move to the refrigerator and stop.
```

Verifies: Semantic location exists in scene graph, robot supports navigation actions.

---

## Troubleshooting

### No API Key error

- Check `~/.PhyAgentOS/config.json`
- Confirm `agents.defaults.model` matches a configured provider
- Confirm the provider has a valid `api_key`

### `EMBODIED.md` not found

- Run `paos onboard`
- Confirm watchdog started successfully
- Confirm driver profile file exists and is readable

### `ACTION.md` has content but action not executed

- Confirm the corresponding watchdog is still running
- Check `ACTION.md` JSON block format
- Check watchdog terminal for driver errors
- Check if `driver-config` is missing required parameters

### Action rejected by Critic

- Check `LESSONS.md` for rejection reason
- Verify the action is declared in `EMBODIED.md` Supported Actions
- Verify the target object/location exists in `ENVIRONMENT.md`

---

## Next Steps

- For real robots: [04 - Embodiments](04_EMBODIMENTS.md)
- For multi-robot: [03 - Fleet Mode](03_FLEET_MODE.md)
- For plugin development: [Plugin Development Guide](../user_development_guide/PLUGIN_DEVELOPMENT_GUIDE.md)
