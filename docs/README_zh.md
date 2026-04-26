# PhyAgentOS 文档中心

> [English](README.md) | **中文**

欢迎来到 PhyAgentOS 文档中心。本页面根据你的角色和目标，帮助你快速找到所需的文档。

---

## 按角色快速导航

| 你的身份 | 推荐阅读路径 |
|---|---|
| 首次使用，想跑通演示 | [用户手册：安装](user_manual/01_INSTALLATION_zh.md) → [基础使用](user_manual/02_BASIC_USAGE_zh.md) |
| 想接入真实机器人或仿真环境 | [本体接入指南](user_manual/04_EMBODIMENTS_zh.md) |
| 开发者，想编写插件或驱动 | [开发指南总览](user_development_guide/README_zh.md) → [插件开发](user_development_guide/PLUGIN_DEVELOPMENT_GUIDE_zh.md) |
| 研究者，想了解架构设计 | [技术报告](plans/Report.md) |
| 想使用 Isaac Sim 仿真 | [PAOS 仿真指南](README_paos_env_zh.md) |

---

## 文档地图

### 面向使用者

| 文档 | 内容说明 |
|---|---|
| [用户手册总览](user_manual/README_zh.md) | 简介、阅读路径与用户文档地图 |
| [01 - 安装与环境准备](user_manual/01_INSTALLATION_zh.md) | 环境搭建、依赖安装与首次配置 |
| [02 - 基础使用](user_manual/02_BASIC_USAGE_zh.md) | CLI 命令、单机模式、命令速查表与交互示例 |
| [03 - Fleet 多机模式](user_manual/03_FLEET_MODE_zh.md) | 多机器人配置、启动顺序与协同交互 |
| [04 - 本体接入指南](user_manual/04_EMBODIMENTS_zh.md) | 各支持机器人的接入方式：Franka、Go2、XLeRobot、G1仿真、PIPER、IoT |
| [附录：Franka 能力矩阵](user_manual/appendix/franka_capabilities.md) | Franka Research 3 后端能力支持表 |
| [附录：Franka 兼容性](user_manual/appendix/franka_compatibility.md) | Franka 版本兼容性表格 |
| [附录：Franka 版本指南](user_manual/appendix/franka_version_guide.md) | Franka 软件包升级/降级指南 |
| [附录：Franka 配置参考](user_manual/appendix/franka_research3_driver_json_example.md) | Franka 驱动 JSON 配置参数说明 |

### 面向开发者

| 文档 | 内容说明 |
|---|---|
| [开发指南总览](user_development_guide/README_zh.md) | 仓库结构、模块职责与推荐阅读顺序 |
| [通信架构说明](user_development_guide/COMMUNICATION_zh.md) | Track A 与 Track B 如何通过工作区文件通信 |
| [插件开发指南](user_development_guide/PLUGIN_DEVELOPMENT_GUIDE_zh.md) | 如何开发、部署和发布外部 HAL 插件 |
| [ReKep 插件部署](user_development_guide/REKEP_PLUGIN_DEPLOYMENT_zh.md) | ReKep 真机插件的一键部署与执行 |
| [HAL 驱动开发](user_development_guide/HAL_DRIVER_zh.md) | 如何实现 `BaseDriver`、编写 profile 与注册驱动 |
| [感知与导航](user_development_guide/PERCEPTION_NAVIGATION_zh.md) | 感知管线、语义导航与 ROS2 桥接的工作原理 |
| [ROS2 集成](user_development_guide/ROS2_INTEGRATION_zh.md) | *（开发中）* ROS2 适配器模式、Topic 映射与导航栈 |

### 架构与规划

| 文档 | 内容说明 |
|---|---|
| [技术报告（英文）](plans/Report_en.md) | PhyAgentOS 架构的完整学术/技术报告 |
| [技术报告（中文）](plans/Report.md) | 技术报告的中文版本 |
| [更新日志 v0.0.5](changelog/v0.0.5.md) | v0.0.5 版本发布说明 |

### 仿真环境

| 文档 | 内容说明 |
|---|---|
| [PAOS 仿真指南（英文）](README_paos_env.md) | Isaac Sim 5.1 安装、环境准备与演示流程 |
| [PAOS 仿真指南（中文）](README_paos_env_zh.md) | 仿真指南的中文版本 |

---

## 推荐阅读路径

### 路径 A："我只想先跑起来"
1. [安装](user_manual/01_INSTALLATION_zh.md)
2. [基础使用](user_manual/02_BASIC_USAGE_zh.md)
3. 实操：`paos onboard` → `python hal/hal_watchdog.py --driver simulation` → `paos agent`

### 路径 B："我想接入我的机器人"
1. [安装](user_manual/01_INSTALLATION_zh.md)
2. [基础使用](user_manual/02_BASIC_USAGE_zh.md)
3. [本体接入指南](user_manual/04_EMBODIMENTS_zh.md) → 找到你的机器人型号
4. 如果需要插件：[插件开发指南](user_development_guide/PLUGIN_DEVELOPMENT_GUIDE_zh.md)

### 路径 C："我想理解架构设计"
1. [技术报告](plans/Report.md)
2. [通信架构](user_development_guide/COMMUNICATION_zh.md)
3. [开发指南总览](user_development_guide/README_zh.md)

### 路径 D："我想开发插件"
1. [开发指南总览](user_development_guide/README_zh.md)
2. [HAL 驱动开发](user_development_guide/HAL_DRIVER_zh.md)
3. [插件开发指南](user_development_guide/PLUGIN_DEVELOPMENT_GUIDE_zh.md)
4. [ReKep 插件部署](user_development_guide/REKEP_PLUGIN_DEPLOYMENT_zh.md)（作为具体示例）

---

## 语言切换

- 英文文档：`*.md`
- 中文文档：`*_zh.md`

每篇配对文档的顶部均提供语言切换链接。
