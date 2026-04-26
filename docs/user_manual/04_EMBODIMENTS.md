# 04 - Embodiment Guide

> **English** | [中文](04_EMBODIMENTS_zh.md)

This guide covers how to start and operate every supported robot embodiment in PhyAgentOS.

---

## Table of Contents

- [Supported Embodiments Summary](#supported-embodiments-summary)
- [Built-in Simulation](#built-in-simulation)
- [Franka Research 3](#franka-research-3)
- [Unitree Go2](#unitree-go2)
- [XLeRobot Remote Chassis](#xlerobot-remote-chassis)
- [G1 Humanoid Simulation](#g1-humanoid-simulation)
- [AgileX PIPER (via ReKep Plugin)](#agilex-piper-via-rekep-plugin)
- [XiaoZhi IoT Device](#xiaozhi-iot-device)
- [Adding a New Robot](#adding-a-new-robot)

---

## Supported Embodiments Summary

| Type | Robot | Driver | Status | How to Start |
|---|---|---|---|---|
| Built-in Simulation | — | `simulation` | Ready | `python hal/hal_watchdog.py --driver simulation` |
| Desktop Arm | Franka Research 3 | `franka_research3` / `franka_multi` | Ready | See [Franka section](#franka-research-3) |
| Quadruped | Unitree Go2 | `go2_edu` | Partial | See [Go2 section](#unitree-go2) |
| Remote Chassis | XLeRobot | `xlerobot_2wheels_remote` | Ready | See [XLeRobot section](#xlerobot-remote-chassis) |
| Humanoid Sim | G1 | `g1_simulation` | Ready | See [G1 section](#g1-humanoid-simulation) |
| Desktop Arm | AgileX PIPER | `rekep_real` (plugin) | Ready | See [PIPER section](#agilex-piper-via-rekep-plugin) |
| IoT Device | XiaoZhi (ESP32) | TBD | Partial | See [XiaoZhi section](#xiaozhi-iot-device) |

---

## Built-in Simulation

The fastest way to verify the full loop without any hardware.

```bash
python hal/hal_watchdog.py --driver simulation
paos agent -m "look around the room"
```

Supported actions in simulation:
- `move_to`, `pick_up`, `put_down`, `push`, `grasp`, `stop`

For Isaac Sim-based simulation, see [PAOS Simulation Guide](../README_paos_env.md).

---

## Franka Research 3

### Network Architecture

```
WorkStation PC --> Control Box (Shop Floor: 172.16.0.x) --> Robot Arm
```

### First-Time Setup

1. Connect PC to Control Box via Ethernet (Shop Floor port)
2. Set PC wired IP to `172.16.0.x` (e.g., `172.16.0.1`)
3. Activate FCI in the Control Box Desk interface
4. Install backend drivers

### Backend Installation

```bash
# Official Python binding
pip install pylibfranka

# Alternative high-level library (broader compatibility)
pip install git+https://github.com/TimSchneider42/franky.git
```

> Check version compatibility before installing. See [Franka Compatibility](appendix/franka_compatibility.md).

### Startup

```bash
# Multi-backend auto-negotiation (recommended)
python hal/hal_watchdog.py --driver franka_multi

# Or with config
python hal/hal_watchdog.py \
  --driver franka_multi \
  --driver-config examples/franka_research3.driver.json
```

### Supported Actions

`move_to`, `move_joints`, `grasp`, `move_gripper`, `stop`

### More References

- [Franka Capabilities](appendix/franka_capabilities.md)
- [Franka Compatibility](appendix/franka_compatibility.md)
- [Franka Version Guide](appendix/franka_version_guide.md)
- [Franka Driver Config](appendix/franka_research3_driver_json_example.md)

---

## Unitree Go2

Go2 requires a real robot or its ROS2-based simulation stack.

### Configuration

Example driver config: [`examples/go2_driver_config.json`](../../examples/go2_driver_config.json)

### Startup

```bash
python hal/hal_watchdog.py \
  --driver go2_edu \
  --driver-config examples/go2_driver_config.json
```

### Capabilities

- Mobility (forward, turn, stop)
- Semantic navigation (move to labeled targets)
- Status monitoring via ROS2 topics

> Go2 support is partial: full perception fusion and advanced navigation are in development.

---

## XLeRobot Remote Chassis

XLeRobot is controlled remotely via ZMQ from a separate host.

### Configuration

Example driver config: [`examples/xlerobot_2wheels_remote.driver.json`](../../examples/xlerobot_2wheels_remote.driver.json)

### Startup

```bash
python hal/hal_watchdog.py \
  --driver xlerobot_2wheels_remote \
  --driver-config examples/xlerobot_2wheels_remote.driver.json
```

### Capabilities

- Chassis movement (forward, backward, turn)
- Dual-arm motion (if equipped)
- Remote status check and safety confirmation

---

## G1 Humanoid Simulation

G1 simulation driver runs in Isaac Sim or a compatible physics simulator.

### Startup

```bash
python hal/hal_watchdog.py --driver g1_simulation
```

### Configuration

Example: [`examples/g1_simulation_driver.json`](../../examples/g1_simulation_driver.json)

---

## AgileX PIPER (via ReKep Plugin)

PIPER is supported through the external `rekep_real` plugin.

### Install Plugin

```bash
python scripts/deploy_rekep_real_plugin.py \
  --repo-url https://github.com/baiyu858/PhyAgentOS-rekep-real-plugin.git
```

### Startup

```bash
python hal/hal_watchdog.py --driver rekep_real
```

### Auto-Onboard New Robot into ReKep

1. Place the robot SDK under `runtime/third_party/<robot_slug>/`
2. Tell the agent: `Help me onboard a new robot <robot name> into ReKep`
3. The skill inspects the SDK and returns deployment instructions

For full details, see [ReKep Plugin Deployment](../user_development_guide/REKEP_PLUGIN_DEPLOYMENT.md).

---

## XiaoZhi IoT Device

XiaoZhi (ESP32-based) currently supports voice dialogue interaction.

> Full IoT device integration is planned for v0.0.7. See [Technical Report](../plans/Report_en.md) roadmap.

---

## Adding a New Robot

If your robot is not listed above, you have two paths:

1. **Built-in driver** (modify main repo): See [HAL Driver Development](../user_development_guide/HAL_DRIVER.md)
2. **External plugin** (recommended for complex hardware): See [Plugin Development Guide](../user_development_guide/PLUGIN_DEVELOPMENT_GUIDE.md)

The ReKep plugin is the best reference implementation for external plugins.

---

## Next Steps

- For multi-robot: [03 - Fleet Mode](03_FLEET_MODE.md)
- For plugin authors: [Plugin Development Guide](../user_development_guide/PLUGIN_DEVELOPMENT_GUIDE.md)
- For architecture: [Communication Architecture](../user_development_guide/COMMUNICATION.md)
