# 01 - 安装与环境准备

> [English](01_INSTALLATION.md) | **中文**

本章涵盖 PhyAgentOS 的环境准备、依赖安装与首次配置。

---

## 目录

- [前置要求](#前置要求)
- [克隆与安装](#克隆与安装)
- [LLM 提供方配置](#llm-提供方配置)
- [工作区初始化](#工作区初始化)
- [验证安装](#验证安装)
- [可选：仿真依赖](#可选仿真依赖)
- [可选：外部插件](#可选外部插件)

---

## 前置要求

| 要求 | 最低版本 | 说明 |
|---|---|---|
| Python | 3.11+ | 推荐 3.11 或 3.12 |
| Git | 任意 | 用于克隆仓库和部署插件 |
| LLM API Key | — | OpenAI 兼容、OpenRouter、Azure 等 |
| Node.js | 18+ | 仅桥接/渠道功能需要 |
| CUDA | 可选 | 本地视觉模型或大规模感知管线需要 |

---

## 克隆与安装

```bash
git clone https://github.com/SYSU-HCP-EAI/PhyAgentOS.git
cd PhyAgentOS
pip install -e .
```

这会安装 `paos` CLI 入口。

---

## LLM 提供方配置

安装后，创建或编辑配置文件：

**配置路径**：`~/.PhyAgentOS/config.json`

### 最小配置示例

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

### 支持的提供方模式

| 提供方 | 模型字符串示例 | 配置键 |
|---|---|---|
| OpenRouter | `openrouter/openai/gpt-4o` | `providers.openrouter.api_key` |
| OpenAI | `openai/gpt-4o` | `providers.openai.api_key` |
| Azure OpenAI | `azure/gpt-4o` | `providers.azure.api_key`, `api_base` |
| 自定义兼容 | `custom/my-model` | `providers.custom.api_key`, `api_base` |

Fleet 模式还需要配置 `embodiments` 节，详见 [03 Fleet 模式](03_FLEET_MODE_zh.md)。

---

## 工作区初始化

安装后或每次升级后执行一次：

```bash
paos onboard
```

作用：
- 若缺失则创建 `~/.PhyAgentOS/config.json`
- 准备默认工作区目录
- 同步模板 Markdown 文件（`ENVIRONMENT.md`、`EMBODIED.md` 等）
- Fleet 模式下准备共享工作区和各机器人工作区

---

## 验证安装

```bash
# 确认 CLI 可用
paos --help

# 确认配置已加载
paos onboard

# 用仿真快速冒烟测试
python hal/hal_watchdog.py --driver simulation &
paos agent -m "环境里有什么"
```

---

## 可选：仿真依赖

内置轻量级仿真（基于磁盘映射）：

```bash
pip install watchdog
```

Isaac Sim 仿真（详见 [PAOS 仿真指南](../README_paos_env_zh.md)）：

- 从 NVIDIA 安装 Isaac Sim 5.1
- 激活 `paos` conda 环境

---

## 可选：外部插件

安装 ReKep 真机插件：

```bash
python scripts/deploy_rekep_real_plugin.py \
  --repo-url https://github.com/baiyu858/PhyAgentOS-rekep-real-plugin.git
```

其他插件使用相同的部署脚本模式。插件开发详见 [插件开发指南](../user_development_guide/PLUGIN_DEVELOPMENT_GUIDE_zh.md)。

---

## 下一步

继续阅读 [02 - 基础使用](02_BASIC_USAGE_zh.md) 启动系统。
