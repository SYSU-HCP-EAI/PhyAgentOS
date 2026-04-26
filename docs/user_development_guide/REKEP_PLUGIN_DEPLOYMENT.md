# ReKep Plugin Deployment

> **English** | [中文](REKEP_PLUGIN_DEPLOYMENT_zh.md)

This guide covers the one-click deployment, development, and execution of the `PhyAgentOS-rekep-real-plugin` for real-world ReKep robot arms.

---

## Table of Contents

- [One-Click Deployment](#one-click-deployment)
- [Start PhyAgentOS with ReKep](#start-phyagentos-with-rekep)
- [Plugin Development](#plugin-development)
- [Validation Workflow](#validation-workflow)
- [Related Repositories](#related-repositories)

---

## One-Click Deployment

First, prepare the main repository:

```bash
git clone https://github.com/SYSU-HCP-EAI/PhyAgentOS.git
cd PhyAgentOS
pip install -e .
pip install watchdog
```

Then deploy the ReKep plugin:

```bash
python scripts/deploy_rekep_real_plugin.py \
  --repo-url https://github.com/baiyu858/PhyAgentOS-rekep-real-plugin.git
```

For solver optional dependencies:

```bash
python scripts/deploy_rekep_real_plugin.py \
  --repo-url https://github.com/baiyu858/PhyAgentOS-rekep-real-plugin.git \
  --with-solver
```

After deployment, PhyAgentOS recognizes the `rekep_real` driver.

---

## Start PhyAgentOS with ReKep

Initialize the workspace:

```bash
paos onboard
```

Open two terminals.

**Terminal 1**: Start the hardware watchdog:

```bash
python hal/hal_watchdog.py --driver rekep_real --workspace ~/.PhyAgentOS/workspace
```

**Terminal 2**: Start the brain Agent:

```bash
paos agent
```

Now the Agent generates action intentions, `hal_watchdog.py` listens to `ACTION.md` and calls the `rekep_real` driver, forming a complete "perception-decision-execution" loop.

---

## Plugin Development

To develop or modify ReKep real-world capabilities, work directly in the plugin repository:

```bash
git clone https://github.com/baiyu858/PhyAgentOS-rekep-real-plugin.git
cd PhyAgentOS-rekep-real-plugin
```

During development, place the plugin next to the main repo and install from local path:

```bash
cd ../PhyAgentOS
python scripts/deploy_rekep_real_plugin.py \
  --repo-url ../PhyAgentOS-rekep-real-plugin
```

Key files:

- `phyagentos_rekep_real_plugin/driver.py`: HAL driver entrypoint
- `runtime/dobot_bridge.py`: ReKep real-world bridge main entry
- `runtime/robot_factory.py`: Robot family adapter factory
- `runtime/cellbot_adapter.py`: New robot adapter template

---

## Validation Workflow

Preflight check:

```bash
python runtime/dobot_bridge.py preflight --pretty
```

Dry-run (no real motion):

```bash
python runtime/dobot_bridge.py execute \
  --instruction "pick up the red block and place it on the tray" \
  --pretty
```

Real execution:

```bash
python runtime/dobot_bridge.py execute \
  --instruction "pick up the red block and place it on the tray" \
  --execute_motion \
  --pretty
```

When adapting a new robot, switch family via generic parameters:

```bash
python runtime/dobot_bridge.py preflight \
  --robot_family cellbot \
  --robot_driver your_driver
```

---

## Related Repositories

- PhyAgentOS main: `https://github.com/SYSU-HCP-EAI/PhyAgentOS.git`
- ReKep plugin: `https://github.com/baiyu858/PhyAgentOS-rekep-real-plugin`
- ReKep releases: `https://github.com/baiyu858/PhyAgentOS-rekep-real-plugin/releases`
