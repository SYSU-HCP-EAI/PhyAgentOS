# PhyAgentOS 开发指南

> [English](README.md) | **中文**

本指南面向 PhyAgentOS 的二次开发者、硬件接入者、插件作者与维护者，帮助你理解、扩展或修改系统。

如需日常操作说明，请参阅 [用户手册](../user_manual/README_zh.md)。

---

## 目录

- [推荐阅读路径](#推荐阅读路径)
- [文档地图](#文档地图)
- [项目结构速览](#项目结构速览)
- [Track A 与 Track B](#track-a-与-track-b)
- [开发者快速开始](#开发者快速开始)

---

## 推荐阅读路径

| 目标 | 推荐阅读顺序 |
|---|---|
| 理解运行时通信 | [通信架构](COMMUNICATION_zh.md) |
| 通过插件接入真实机器人 | [插件开发指南](PLUGIN_DEVELOPMENT_GUIDE_zh.md) → [ReKep 插件部署](REKEP_PLUGIN_DEPLOYMENT_zh.md) |
| 开发 HAL 驱动 | [HAL 驱动开发](HAL_DRIVER_zh.md) → [插件开发指南](PLUGIN_DEVELOPMENT_GUIDE_zh.md) |
| 理解感知/导航 | [感知与导航](PERCEPTION_NAVIGATION_zh.md) |
| 理解 ROS2 集成 | [ROS2 集成](ROS2_INTEGRATION_zh.md) *（开发中）* |

---

## 文档地图

| 文档 | 用途 |
|---|---|
| [通信架构](COMMUNICATION_zh.md) | Track A 与 Track B 如何通过工作区文件通信 |
| [插件开发指南](PLUGIN_DEVELOPMENT_GUIDE_zh.md) | 如何开发、部署和发布外部 HAL 插件 |
| [ReKep 插件部署](REKEP_PLUGIN_DEPLOYMENT_zh.md) | ReKep 真机插件的一键部署指南 |
| [HAL 驱动开发](HAL_DRIVER_zh.md) | 如何实现 `BaseDriver`、编写 profile 与注册驱动 |
| [感知与导航](PERCEPTION_NAVIGATION_zh.md) | 感知管线、语义导航与 ROS2 桥接的工作原理 |
| [ROS2 集成](ROS2_INTEGRATION_zh.md) | *（开发中）* ROS2 适配器模式、Topic 映射与导航栈 |

---

## 项目结构速览

```text
PhyAgentOS/                # Track A：软件大脑核心
├── agent/                 # AgentLoop、上下文、记忆、子代理、工具
├── cli/                   # CLI 入口：paos onboard、agent、gateway
├── providers/             # LLM 提供方适配层
├── channels/              # 外部渠道接入
├── heartbeat/             # 心跳与周期任务调度
├── cron/                  # 定时任务服务
└── templates/             # 工作区 Markdown 模板

hal/                       # Track B：硬件 HAL 与仿真
├── hal_watchdog.py        # 硬件看门狗守护进程
├── base_driver.py         # BaseDriver 抽象接口
├── drivers/               # 内置驱动实现
├── plugins.py             # 外部插件注册与加载
├── profiles/              # 机器人/本体静态 profile
├── navigation/            # 导航后端与语义导航
├── perception/            # 感知、几何、分割、融合
├── ros2/                  # ROS2 桥接与适配器
└── simulation/            # 仿真环境

scripts/                   # 插件部署脚本
examples/                  # 驱动配置示例
tests/                     # 自动化测试
docs/                      # 文档
```

---

## Track A 与 Track B

| 层级 | 职责 | 关键入口 |
|---|---|---|
| **Track A** | 自然语言理解、规划、工具调用、Critic 校验、记忆 | `paos agent`、`paos gateway` |
| **Track B** | 动作执行、驱动管理、状态反馈、环境更新 | `hal/hal_watchdog.py` |
| **协议** | 共享工作区 Markdown 文件：`ENVIRONMENT.md`、`ACTION.md`、`EMBODIED.md`、`LESSONS.md` 等 | `~/.PhyAgentOS/workspace/` 下的文件 |

核心原则：**不要把硬件事实藏在不可见的黑盒代码路径里。** 所有运行时状态都应该可以通过打开一个 Markdown 文件来检查。

---

## 开发者快速开始

```bash
# 1. 克隆并安装
git clone https://github.com/SYSU-HCP-EAI/PhyAgentOS.git
cd PhyAgentOS
pip install -e .

# 2. 初始化工作区
paos onboard

# 3. 运行测试
pytest tests/

# 4. 启动开发循环
# 终端 A：python hal/hal_watchdog.py --driver simulation
# 终端 B：paos agent
```

---

## 下一步

- 理解通信协议：[通信架构](COMMUNICATION_zh.md)
- 开发插件：[插件开发指南](PLUGIN_DEVELOPMENT_GUIDE_zh.md)
- 添加驱动：[HAL 驱动开发](HAL_DRIVER_zh.md)
