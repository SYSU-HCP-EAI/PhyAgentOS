# PhyAgentOS User Manual

> **English** | [中文](README_zh.md)

This manual is for end users, integrators, and demo operators who want to install, run, and operate PhyAgentOS.

For architecture details or plugin development, see the [Development Guide](../user_development_guide/README.md).

---

## Table of Contents

- [Reading Paths](#reading-paths)
- [Document Map](#document-map)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)

---

## Reading Paths

| Goal | Read in this order |
|---|---|
| I want to run PhyAgentOS for the first time | [01 Installation](01_INSTALLATION.md) → [02 Basic Usage](02_BASIC_USAGE.md) |
| I want to connect a specific robot | [01 Installation](01_INSTALLATION.md) → [04 Embodiments](04_EMBODIMENTS.md) |
| I want multi-robot coordination | [02 Basic Usage](02_BASIC_USAGE.md) → [03 Fleet Mode](03_FLEET_MODE.md) |
| I want simulation with Isaac Sim | [PAOS Simulation Guide](../README_paos_env.md) |

---

## Document Map

| Document | Purpose |
|---|---|
| [01 - Installation](01_INSTALLATION.md) | Environment setup, Python/conda installation, LLM provider configuration |
| [02 - Basic Usage](02_BASIC_USAGE.md) | `paos onboard`, `paos agent`, `paos gateway`, single-instance mode, command cheat-sheet |
| [03 - Fleet Mode](03_FLEET_MODE.md) | Multi-robot topology, `config.json` fleet setup, per-robot watchdog startup |
| [04 - Embodiments](04_EMBODIMENTS.md) | How to start each supported robot: Franka, Go2, XLeRobot, G1 simulation, PIPER, IoT |
| [Appendix: Franka Capabilities](appendix/franka_capabilities.md) | Backend capability matrix |
| [Appendix: Franka Compatibility](appendix/franka_compatibility.md) | Version compatibility table |
| [Appendix: Franka Version Guide](appendix/franka_version_guide.md) | Upgrade/downgrade guide |
| [Appendix: Franka Driver Config](appendix/franka_research3_driver_json_example.md) | Driver JSON reference |

---

## Quick Start (5 Minutes)

```bash
# 1. Install
git clone https://github.com/SYSU-HCP-EAI/PhyAgentOS.git
cd PhyAgentOS
pip install -e .

# 2. Configure LLM provider
# Edit ~/.PhyAgentOS/config.json

# 3. Initialize workspace
paos onboard

# 4. Terminal A: Start simulation watchdog
python hal/hal_watchdog.py --driver simulation

# 5. Terminal B: Start agent
paos agent -m "look around the room"
```

For detailed steps, continue to [01 Installation](01_INSTALLATION.md).
