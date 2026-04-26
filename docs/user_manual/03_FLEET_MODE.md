# 03 - Fleet Mode

> **English** | [中文](03_FLEET_MODE_zh.md)

Fleet mode enables one Agent to plan and coordinate multiple heterogeneous robots simultaneously.

---

## Table of Contents

- [When to Use Fleet Mode](#when-to-use-fleet-mode)
- [Configuration](#configuration)
- [Startup Order](#startup-order)
- [Workspace Topology](#workspace-topology)
- [Interaction in Fleet Mode](#interaction-in-fleet-mode)
- [Troubleshooting](#troubleshooting)

---

## When to Use Fleet Mode

Use fleet mode when you need:

- One Agent to plan across multiple robot instances
- Separate shared environment and per-robot action queues
- Independent `EMBODIED.md` and `ACTION.md` per robot

---

## Configuration

Edit `~/.PhyAgentOS/config.json`:

```json
{
  "embodiments": {
    "mode": "fleet",
    "shared_workspace": "~/.PhyAgentOS/workspaces/shared",
    "instances": [
      {
        "robot_id": "go2_edu_001",
        "driver": "go2_edu",
        "workspace": "~/.PhyAgentOS/workspaces/go2_edu_001"
      },
      {
        "robot_id": "franka_lab_001",
        "driver": "franka_multi",
        "workspace": "~/.PhyAgentOS/workspaces/franka_lab_001"
      }
    ]
  }
}
```

After editing, run:

```bash
paos onboard
```

---

## Startup Order

1. Configure `embodiments.mode = "fleet"`
2. Run `paos onboard`
3. Start one watchdog per robot instance
4. Start one `paos agent` or `paos gateway`

Example:

```bash
# Terminal A: Watchdog for Go2
python hal/hal_watchdog.py \
  --robot-id go2_edu_001 \
  --driver-config examples/go2_driver_config.json

# Terminal B: Watchdog for Franka
python hal/hal_watchdog.py \
  --robot-id franka_lab_001 \
  --driver-config examples/franka_research3.driver.json

# Terminal C: Agent
paos agent
```

> In fleet mode, `--robot-id` binds the watchdog to a specific instance. The driver name is read from `config.json`.

---

## Workspace Topology

```text
~/.PhyAgentOS/workspaces/
├── shared/
│   ├── ENVIRONMENT.md      # Global environment state
│   ├── ROBOTS.md           # Auto-generated robot registry
│   ├── TASK.md             # Multi-step task state
│   ├── ORCHESTRATOR.md     # Coordination state
│   └── LESSONS.md          # Shared failure memory
├── go2_edu_001/
│   ├── ACTION.md           # Action queue for this robot
│   └── EMBODIED.md         # Runtime profile for this robot
└── franka_lab_001/
    ├── ACTION.md
    └── EMBODIED.md
```

---

## Interaction in Fleet Mode

User instructions should ideally name the target robot explicitly:

```text
Let Go2 go to the door for inspection, then let the arm pick up the package on the table.
```

The Agent:
1. Reads `ROBOTS.md` to discover available robots
2. Reads `ENVIRONMENT.md` for shared scene state
3. Dispatches actions to the correct robot workspace
4. Critic validates each action against that robot's `EMBODIED.md`

---

## Troubleshooting

### Task not dispatched to correct robot

- Check `robot_id`, `driver`, and `workspace` in config
- Confirm watchdog was started with `--robot-id`
- Check `ROBOTS.md` in the shared workspace
- Ensure the instruction explicitly names the target robot

### One robot's actions affect another

- Confirm each watchdog is bound to a different workspace
- Confirm `robot_id` values are unique

---

## Next Steps

- [04 - Embodiments](04_EMBODIMENTS.md) for per-robot startup details
- [Development Guide](../user_development_guide/README.md) for fleet architecture internals
