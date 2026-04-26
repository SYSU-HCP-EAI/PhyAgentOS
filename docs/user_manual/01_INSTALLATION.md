# 01 - Installation & Environment Setup

> **English** | [中文](01_INSTALLATION_zh.md)

This chapter covers environment preparation, dependency installation, and first-time configuration for PhyAgentOS.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Clone & Install](#clone--install)
- [LLM Provider Configuration](#llm-provider-configuration)
- [Workspace Initialization](#workspace-initialization)
- [Verify Installation](#verify-installation)
- [Optional: Simulation Dependencies](#optional-simulation-dependencies)
- [Optional: External Plugins](#optional-external-plugins)

---

## Prerequisites

| Requirement | Minimum | Notes |
|---|---|---|
| Python | 3.11+ | Recommended: 3.11 or 3.12 |
| Git | any | For cloning and plugin deployment |
| LLM API Key | — | OpenAI-compatible, OpenRouter, Azure, etc. |
| Node.js | 18+ | Only needed for bridge/channel features |
| CUDA | optional | For local vision models or large perception pipelines |

---

## Clone & Install

```bash
git clone https://github.com/SYSU-HCP-EAI/PhyAgentOS.git
cd PhyAgentOS
pip install -e .
```

This installs the `paos` CLI entry point.

---

## LLM Provider Configuration

After installation, create or edit the configuration file:

**Config path**: `~/.PhyAgentOS/config.json`

### Minimal config example

```json
{
  "agents": {
    "defaults": {
      "model": "openrouter/openai/gpt-4o-mini",
      "workspace": "~/.PhyAgentOS/workspace"
    }
  },
  "providers": {
    "openrouter": {
      "api_key": "YOUR_API_KEY"
    }
  }
}
```

### Supported provider patterns

| Provider | Model string example | Config key |
|---|---|---|
| OpenRouter | `openrouter/openai/gpt-4o` | `providers.openrouter.api_key` |
| OpenAI | `openai/gpt-4o` | `providers.openai.api_key` |
| Azure OpenAI | `azure/gpt-4o` | `providers.azure.api_key`, `api_base` |
| Custom compatible | `custom/my-model` | `providers.custom.api_key`, `api_base` |

For fleet mode, the `embodiments` section is also required. See [03 Fleet Mode](03_FLEET_MODE.md).

---

## Workspace Initialization

Run once after installation or after any upgrade:

```bash
paos onboard
```

What it does:
- Creates `~/.PhyAgentOS/config.json` if missing
- Prepares the default workspace directory
- Syncs template Markdown files (`ENVIRONMENT.md`, `EMBODIED.md`, etc.)
- In fleet mode, prepares the shared workspace and per-robot workspaces

---

## Verify Installation

```bash
# Check CLI is available
paos --help

# Check config is loaded
paos onboard

# Quick smoke test with simulation
python hal/hal_watchdog.py --driver simulation &
paos agent -m "what is in the environment"
```

---

## Optional: Simulation Dependencies

For the built-in lightweight simulation (disk-mapping based):

```bash
pip install watchdog
```

For Isaac Sim-based simulation (see [PAOS Simulation Guide](../README_paos_env.md)):

- Install Isaac Sim 5.1 from NVIDIA
- Activate the `paos` conda environment

---

## Optional: External Plugins

To install the ReKep real-world plugin:

```bash
python scripts/deploy_rekep_real_plugin.py \
  --repo-url https://github.com/baiyu858/PhyAgentOS-rekep-real-plugin.git
```

For other plugins, use the same deployment script pattern. For plugin development, see [Plugin Development Guide](../user_development_guide/PLUGIN_DEVELOPMENT_GUIDE.md).

---

## Next Step

Continue to [02 - Basic Usage](02_BASIC_USAGE.md) to start the system.
