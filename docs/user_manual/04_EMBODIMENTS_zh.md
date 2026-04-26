# 04 - 本体接入指南

> [English](04_EMBODIMENTS.md) | **中文**

本指南涵盖 PhyAgentOS 中每台支持机器人的启动与操作方式。

---

## 目录

- [支持的本体总览](#支持的本体总览)
- [内置仿真](#内置仿真)
- [Franka Research 3](#franka-research-3)
- [Unitree Go2](#unitree-go2)
- [XLeRobot 远程底盘](#xlerobot-远程底盘)
- [G1 人形机器人仿真](#g1-人形机器人仿真)
- [松灵 PIPER（通过 ReKep 插件）](#松灵-piper通过-rekep-插件)
- [小智 IoT 设备](#小智-iot-设备)
- [接入新机器人](#接入新机器人)

---

## 支持的本体总览

| 类型 | 机器人 | 驱动名 | 状态 | 启动方式 |
|---|---|---|---|---|
| 内置仿真 | — | `simulation` | 可用 | `python hal/hal_watchdog.py --driver simulation` |
| 桌面机械臂 | Franka Research 3 | `franka_research3` / `franka_multi` | 可用 | 见 [Franka 章节](#franka-research-3) |
| 四足机器人 | Unitree Go2 | `go2_edu` | 部分 | 见 [Go2 章节](#unitree-go2) |
| 远程底盘 | XLeRobot | `xlerobot_2wheels_remote` | 可用 | 见 [XLeRobot 章节](#xlerobot-远程底盘) |
| 人形仿真 | G1 | `g1_simulation` | 可用 | 见 [G1 章节](#g1-人形机器人仿真) |
| 桌面机械臂 | 松灵 PIPER | `rekep_real`（插件） | 可用 | 见 [PIPER 章节](#松灵-piper通过-rekep-插件) |
| IoT 设备 | 小智（ESP32） | 待定 | 部分 | 见 [小智 章节](#小智-iot-设备) |

---

## 内置仿真

无需任何硬件即可验证全链路的最快方式。

```bash
python hal/hal_watchdog.py --driver simulation
paos agent -m "看看周围有什么"
```

仿真支持的动作：
`move_to`、`pick_up`、`put_down`、`push`、`grasp`、`stop`

Isaac Sim 仿真详见 [PAOS 仿真指南](../README_paos_env_zh.md)。

---

## Franka Research 3

### 网络架构

```
工作站 PC --> 控制柜（Shop Floor: 172.16.0.x）--> 机械臂
```

### 首次设置

1. 网线连接 PC 与控制柜 Shop Floor 接口
2. PC 有线网络 IP 设为 `172.16.0.x`（如 `172.16.0.1`）
3. 在 Control Box Desk 界面激活 FCI
4. 安装后端驱动

### 后端安装

```bash
# 官方 Python 绑定
pip install pylibfranka

# 备选高层库（兼容性更宽松）
pip install git+https://github.com/TimSchneider42/franky.git
```

> 安装前请检查版本兼容性。详见 [Franka 兼容性](appendix/franka_compatibility.md)。

### 启动

```bash
# 多后端自动协商（推荐）
python hal/hal_watchdog.py --driver franka_multi

# 或带配置启动
python hal/hal_watchdog.py \
  --driver franka_multi \
  --driver-config examples/franka_research3.driver.json
```

### 支持的动作

`move_to`、`move_joints`、`grasp`、`move_gripper`、`stop`

### 更多参考

- [Franka 能力矩阵](appendix/franka_capabilities.md)
- [Franka 兼容性](appendix/franka_compatibility.md)
- [Franka 版本指南](appendix/franka_version_guide.md)
- [Franka 配置参考](appendix/franka_research3_driver_json_example.md)

---

## Unitree Go2

Go2 需要真实机器人或基于 ROS2 的仿真栈。

### 配置

驱动配置示例：[`examples/go2_driver_config.json`](../../examples/go2_driver_config.json)

### 启动

```bash
python hal/hal_watchdog.py \
  --driver go2_edu \
  --driver-config examples/go2_driver_config.json
```

### 能力

- 移动（前进、转向、停止）
- 语义导航（移动到标记目标）
- 通过 ROS2 topic 状态监控

> Go2 支持为部分：完整感知融合和高级导航仍在开发中。

---

## XLeRobot 远程底盘

XLeRobot 通过 ZMQ 从远程主机控制。

### 配置

驱动配置示例：[`examples/xlerobot_2wheels_remote.driver.json`](../../examples/xlerobot_2wheels_remote.driver.json)

### 启动

```bash
python hal/hal_watchdog.py \
  --driver xlerobot_2wheels_remote \
  --driver-config examples/xlerobot_2wheels_remote.driver.json
```

### 能力

- 底盘移动（前进、后退、转向）
- 双臂运动（如配备）
- 远程状态检查与安全确认

---

## G1 人形机器人仿真

G1 仿真驱动在 Isaac Sim 或兼容物理仿真器中运行。

### 启动

```bash
python hal/hal_watchdog.py --driver g1_simulation
```

### 配置

示例：[`examples/g1_simulation_driver.json`](../../examples/g1_simulation_driver.json)

---

## 松灵 PIPER（通过 ReKep 插件）

PIPER 通过外部 `rekep_real` 插件支持。

### 安装插件

```bash
python scripts/deploy_rekep_real_plugin.py \
  --repo-url https://github.com/baiyu858/PhyAgentOS-rekep-real-plugin.git
```

### 启动

```bash
python hal/hal_watchdog.py --driver rekep_real
```

### 自动接入新机器人到 ReKep

1. 将机器人 SDK 放入 `runtime/third_party/<robot_slug>/`
2. 对 Agent 说：`帮我接入新机器人 <机器人名> 到 ReKep`
3. Skill 自动检查 SDK 并返回部署说明

详细说明见 [ReKep 插件部署](../user_development_guide/REKEP_PLUGIN_DEPLOYMENT_zh.md)。

---

## 小智 IoT 设备

小智（基于 ESP32）目前支持语音对话交互。

> 完整 IoT 设备集成计划在 v0.0.7 实现。详见 [技术报告](../plans/Report.md) 路线图。

---

## 接入新机器人

如果你的机器人不在上述列表中，有两条路径：

1. **内置驱动**（修改主仓库）：参考 [HAL 驱动开发](../user_development_guide/HAL_DRIVER_zh.md)
2. **外部插件**（复杂硬件推荐）：参考 [插件开发指南](../user_development_guide/PLUGIN_DEVELOPMENT_GUIDE_zh.md)

ReKep 插件是外部插件的最佳参考实现。

---

## 下一步

- 多机器人协同：[03 - Fleet 模式](03_FLEET_MODE_zh.md)
- 插件开发：[插件开发指南](../user_development_guide/PLUGIN_DEVELOPMENT_GUIDE_zh.md)
- 架构理解：[通信架构](../user_development_guide/COMMUNICATION_zh.md)
