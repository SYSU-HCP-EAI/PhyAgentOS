# PhyAgentOS Development Guide

> **English** | [中文](README_zh.md)

This guide is for secondary developers, hardware integrators, plugin authors, and maintainers who want to understand, extend, or modify PhyAgentOS.

For end-user operations, see the [User Manual](../user_manual/README.md).

---

## Table of Contents

- [Reading Paths](#reading-paths)
- [Document Map](#document-map)
- [Project Structure at a Glance](#project-structure-at-a-glance)
- [Track A vs Track B](#track-a-vs-track-b)
- [Quick Start for Developers](#quick-start-for-developers)

---

## Reading Paths

| Goal | Read in this order |
|---|---|
| Understand runtime communication | [Communication Architecture](COMMUNICATION.md) |
| Connect a real robot via plugin | [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md) → [ReKep Plugin Deployment](REKEP_PLUGIN_DEPLOYMENT.md) |
| Develop a HAL driver | [HAL Driver Development](HAL_DRIVER.md) → [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md) |
| Understand perception / navigation | [Perception & Navigation](PERCEPTION_NAVIGATION.md) |
| Understand ROS2 integration | [ROS2 Integration](ROS2_INTEGRATION.md) *(In Development)* |

---

## Document Map

| Document | Purpose |
|---|---|
| [Communication Architecture](COMMUNICATION.md) | How Track A and Track B communicate via workspace files |
| [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md) | How to develop, deploy, and release external HAL plugins |
| [ReKep Plugin Deployment](REKEP_PLUGIN_DEPLOYMENT.md) | One-click deployment guide for the ReKep real-world plugin |
| [HAL Driver Development](HAL_DRIVER.md) | How to implement `BaseDriver`, write profiles, and register drivers |
| [Perception & Navigation](PERCEPTION_NAVIGATION.md) | How perception pipeline, semantic navigation, and ROS2 bridge work |
| [ROS2 Integration](ROS2_INTEGRATION.md) | *(In Development)* ROS2 adapter patterns, topic mapping, navigation stack |

---

## Project Structure at a Glance

```text
PhyAgentOS/                # Track A: Software Brain Core
├── agent/                 # AgentLoop, context, memory, sub-agents, tools
├── cli/                   # CLI entry: paos onboard, agent, gateway
├── providers/             # LLM provider adapters
├── channels/              # External channel integrations
├── heartbeat/             # Heartbeat and periodic task scheduling
├── cron/                  # Cron job service
└── templates/             # Workspace Markdown templates

hal/                       # Track B: Hardware HAL & Simulation
├── hal_watchdog.py        # Hardware watchdog daemon
├── base_driver.py         # BaseDriver abstract interface
├── drivers/               # Built-in driver implementations
├── plugins.py             # External plugin registry and loading
├── profiles/              # Robot/embodiment static profiles
├── navigation/            # Navigation backend and semantic navigation
├── perception/            # Perception, geometry, segmentation, fusion
├── ros2/                  # ROS2 bridge and adapters
└── simulation/            # Simulation environment

scripts/                   # Plugin deployment scripts
examples/                  # Driver configuration examples
tests/                     # Automated tests
docs/                      # Documentation
```

---

## Track A vs Track B

| Layer | Responsibility | Key Entry Points |
|---|---|---|
| **Track A** | Natural language understanding, planning, tool invocation, Critic validation, memory | `paos agent`, `paos gateway` |
| **Track B** | Action execution, driver management, state feedback, environment updates | `hal/hal_watchdog.py` |
| **Protocol** | Shared workspace Markdown files: `ENVIRONMENT.md`, `ACTION.md`, `EMBODIED.md`, `LESSONS.md`, etc. | Files in `~/.PhyAgentOS/workspace/` |

The golden rule: **Do not hide hardware facts inside opaque code paths.** All runtime state should be inspectable by opening a Markdown file.

---

## Quick Start for Developers

```bash
# 1. Clone and install
git clone https://github.com/SYSU-HCP-EAI/PhyAgentOS.git
cd PhyAgentOS
pip install -e .

# 2. Initialize workspace
paos onboard

# 3. Run tests
pytest tests/

# 4. Start development loop
# Terminal A: python hal/hal_watchdog.py --driver simulation
# Terminal B: paos agent
```

---

## Next Steps

- Understand the protocol: [Communication Architecture](COMMUNICATION.md)
- Build a plugin: [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)
- Add a driver: [HAL Driver Development](HAL_DRIVER.md)
