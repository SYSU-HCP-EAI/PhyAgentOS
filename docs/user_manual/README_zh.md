# PhyAgentOS 用户手册

> [English](README.md) | **中文**

本手册面向 PhyAgentOS 的使用者、集成者和演示操作者，帮助完成安装、运行和日常操作。

如需了解架构设计或进行二次开发，请参阅 [开发指南](../user_development_guide/README_zh.md)。

---

## 目录

- [推荐阅读路径](#推荐阅读路径)
- [文档地图](#文档地图)
- [5 分钟快速开始](#5-分钟快速开始)

---

## 推荐阅读路径

| 目标 | 推荐阅读顺序 |
|---|---|
| 首次运行 PhyAgentOS | [01 安装](01_INSTALLATION_zh.md) → [02 基础使用](02_BASIC_USAGE_zh.md) |
| 接入特定机器人 | [01 安装](01_INSTALLATION_zh.md) → [04 本体接入指南](04_EMBODIMENTS_zh.md) |
| 多机器人协同 | [02 基础使用](02_BASIC_USAGE_zh.md) → [03 Fleet 模式](03_FLEET_MODE_zh.md) |
| 使用 Isaac Sim 仿真 | [PAOS 仿真指南](../README_paos_env_zh.md) |

---

## 文档地图

| 文档 | 用途 |
|---|---|
| [01 - 安装与环境准备](01_INSTALLATION_zh.md) | 环境搭建、Python/conda 安装、LLM 提供方配置 |
| [02 - 基础使用](02_BASIC_USAGE_zh.md) | `paos onboard`、`paos agent`、`paos gateway`、单机模式、命令速查表 |
| [03 - Fleet 多机模式](03_FLEET_MODE_zh.md) | 多机器人拓扑、`config.json` 配置、逐机器人启动看门狗 |
| [04 - 本体接入指南](04_EMBODIMENTS_zh.md) | 各支持机器人的启动方式：Franka、Go2、XLeRobot、G1仿真、PIPER、IoT |
| [附录：Franka 能力矩阵](appendix/franka_capabilities.md) | 后端能力支持表 |
| [附录：Franka 兼容性](appendix/franka_compatibility.md) | 版本兼容性表格 |
| [附录：Franka 版本指南](appendix/franka_version_guide.md) | 升级/降级指南 |
| [附录：Franka 配置参考](appendix/franka_research3_driver_json_example.md) | 驱动 JSON 配置参数说明 |

---

## 5 分钟快速开始

```bash
# 1. 安装
git clone https://github.com/SYSU-HCP-EAI/PhyAgentOS.git
cd PhyAgentOS
pip install -e .

# 2. 配置 LLM 提供方
# 编辑 ~/.PhyAgentOS/config.json

# 3. 初始化工作区
paos onboard

# 4. 终端 A：启动仿真看门狗
python hal/hal_watchdog.py --driver simulation

# 5. 终端 B：启动 Agent
paos agent -m "看看周围有什么"
```

详细步骤请继续阅读 [01 安装](01_INSTALLATION_zh.md)。
