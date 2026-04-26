# PhyAgentOS Documentation

> **English** | [中文](README_zh.md)

Welcome to the PhyAgentOS documentation hub. This page helps you find the right document based on who you are and what you want to do.

---

## Quick Navigation by Role

| If you are... | Start here |
|---|---|
| A first-time user who wants to run a demo | [User Manual: Installation](user_manual/01_INSTALLATION.md) → [Basic Usage](user_manual/02_BASIC_USAGE.md) |
| A user who wants to connect a real robot or simulation | [Embodiments Guide](user_manual/04_EMBODIMENTS.md) |
| A developer who wants to write a plugin or driver | [Development Guide Overview](user_development_guide/README.md) → [Plugin Development](user_development_guide/PLUGIN_DEVELOPMENT_GUIDE.md) |
| A researcher who wants to understand the architecture | [Technical Report](plans/Report_en.md) |
| A user who wants Isaac Sim simulation | [PAOS Simulation Guide](README_paos_env.md) |

---

## Documentation Map

### For End Users

| Document | What it covers |
|---|---|
| [User Manual Overview](user_manual/README.md) | Introduction, reading paths, and document map for users |
| [01 - Installation](user_manual/01_INSTALLATION.md) | Environment setup, dependencies, and first-time configuration |
| [02 - Basic Usage](user_manual/02_BASIC_USAGE.md) | CLI commands, single-instance mode, command cheat-sheet, and interaction examples |
| [03 - Fleet Mode](user_manual/03_FLEET_MODE.md) | Multi-robot configuration, startup order, and fleet interaction |
| [04 - Embodiments](user_manual/04_EMBODIMENTS.md) | How to connect each supported robot: Franka, Go2, XLeRobot, G1 simulation, PIPER, IoT |
| [Appendix: Franka Capabilities](user_manual/appendix/franka_capabilities.md) | Backend capability matrix for Franka Research 3 |
| [Appendix: Franka Compatibility](user_manual/appendix/franka_compatibility.md) | Version compatibility table for Franka |
| [Appendix: Franka Version Guide](user_manual/appendix/franka_version_guide.md) | Upgrade/downgrade guide for Franka software |
| [Appendix: Franka Driver JSON](user_manual/appendix/franka_research3_driver_json_example.md) | Driver configuration reference for Franka |

### For Developers

| Document | What it covers |
|---|---|
| [Development Guide Overview](user_development_guide/README.md) | Project structure, module responsibilities, and recommended reading order |
| [Communication Architecture](user_development_guide/COMMUNICATION.md) | How Track A and Track B communicate via workspace files |
| [Plugin Development Guide](user_development_guide/PLUGIN_DEVELOPMENT_GUIDE.md) | How to develop, deploy, and release external HAL plugins |
| [ReKep Plugin Deployment](user_development_guide/REKEP_PLUGIN_DEPLOYMENT.md) | One-click deployment and execution of the ReKep real-world plugin |
| [HAL Driver Development](user_development_guide/HAL_DRIVER.md) | How to implement a `BaseDriver`, write profiles, and register drivers |
| [Perception & Navigation](user_development_guide/PERCEPTION_NAVIGATION.md) | How the perception pipeline, semantic navigation, and ROS2 bridge work |
| [ROS2 Integration](user_development_guide/ROS2_INTEGRATION.md) | *(In Development)* ROS2 adapter patterns, topic mapping, and navigation stack |

### Architecture & Planning

| Document | What it covers |
|---|---|
| [Technical Report (EN)](plans/Report_en.md) | Full academic/technical report on the PhyAgentOS architecture |
| [Technical Report (ZH)](plans/Report.md) | Chinese version of the technical report |
| [Changelog v0.0.5](changelog/v0.0.5.md) | Release notes for version 0.0.5 |

### Simulation Environment

| Document | What it covers |
|---|---|
| [PAOS Simulation Guide (EN)](README_paos_env.md) | Isaac Sim 5.1 setup, environment preparation, and demo pipeline |
| [PAOS Simulation Guide (ZH)](README_paos_env_zh.md) | Chinese version of the simulation guide |

---

## Recommended Reading Paths

### Path A: "I just want to see it run"
1. [Installation](user_manual/01_INSTALLATION.md)
2. [Basic Usage](user_manual/02_BASIC_USAGE.md)
3. Try: `paos onboard` → `python hal/hal_watchdog.py --driver simulation` → `paos agent`

### Path B: "I want to connect my robot"
1. [Installation](user_manual/01_INSTALLATION.md)
2. [Basic Usage](user_manual/02_BASIC_USAGE.md)
3. [Embodiments Guide](user_manual/04_EMBODIMENTS.md) → find your robot model
4. If your robot needs a plugin: [Plugin Development Guide](user_development_guide/PLUGIN_DEVELOPMENT_GUIDE.md)

### Path C: "I want to understand the architecture"
1. [Technical Report](plans/Report_en.md)
2. [Communication Architecture](user_development_guide/COMMUNICATION.md)
3. [Development Guide Overview](user_development_guide/README.md)

### Path D: "I want to write a plugin"
1. [Development Guide Overview](user_development_guide/README.md)
2. [HAL Driver Development](user_development_guide/HAL_DRIVER.md)
3. [Plugin Development Guide](user_development_guide/PLUGIN_DEVELOPMENT_GUIDE.md)
4. [ReKep Plugin Deployment](user_development_guide/REKEP_PLUGIN_DEPLOYMENT.md) (as a concrete example)

---

## Language Switch

- English documents: `*.md`
- Chinese documents: `*_zh.md`

Most paired documents are cross-linked at the top of each file.
