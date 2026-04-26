# PAOS 仿真环境指南

> [English](README_paos_env.md) | **中文**

本指南涵盖如何设置和运行 PhyAgentOS 仿真环境，包括内置轻量级仿真和 NVIDIA Isaac Sim 5.1。

---

## 目录

- [内置仿真（首次使用推荐）](#内置仿真首次使用推荐)
- [Isaac Sim 5.1 仿真](#isaac-sim-51-仿真)
- [G1 人形机器人仿真](#g1-人形机器人仿真)
- [多机器人仿真](#多机器人仿真)
- [常见问题排查](#常见问题排查)

---

## 内置仿真（首次使用推荐）

内置仿真除了 `watchdog` 外无需额外安装：

```bash
pip install watchdog
```

### 快速开始

```bash
# 终端 1：启动仿真看门狗
python hal/hal_watchdog.py --driver simulation

# 终端 2：启动 Agent
paos agent -m "看看周围有什么"
```

### 支持的动作

`move_to`、`pick_up`、`put_down`、`push`、`grasp`、`stop`

### 注意事项

- 同时只运行一个看门狗进程
- 如仿真卡顿，可调整 `--interval`（默认 0.05s = 20Hz）
- 修改驱动或 skill 文件后需重启看门狗

---

## Isaac Sim 5.1 仿真

用于高保真物理仿真与视觉渲染。

### 前置要求

1. 安装 Isaac Sim 5.1.0：
   - 下载页面：[https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/download.html](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/download.html)
   - 快速安装：[https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/quick-install.html](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/quick-install.html)

2. 准备 Python 环境：

```bash
conda activate paos
```

3. 安装依赖：

```bash
cd /path/to/PhyAgentOS
conda env create -f environment.yml
pip install -e .
```

### 启动 HAL 看门狗（GUI 模式）

```bash
cd /path/to/PhyAgentOS
conda activate paos
python hal/hal_watchdog.py \
  --gui \
  --interval 0.05 \
  --driver pipergo2_manipulation \
  --driver-config examples/pipergo2_manipulation_driver.json
```

### 发送 PAOS Agent 指令

另开一个终端：

```bash
cd /path/to/PhyAgentOS
conda activate paos
paos agent -m "打开仿真"
paos agent -m "去桌子那边"
paos agent -m "抓起红色方块并返回起始位置"
```

### Isaac Sim 配置文件

| 文件 | 用途 |
|---|---|
| `examples/pipergo2_manipulation_driver.json` | PIPER + Go2 操纵配置 |
| `examples/franka_simulation_driver.json` | Franka 仿真配置 |
| `examples/g1_simulation_driver.json` | G1 人形仿真配置 |
| `examples/multi_robot_simulation_internutopia_driver.json` | 多机器人场景配置 |

---

## G1 人形机器人仿真

```bash
python hal/hal_watchdog.py --driver g1_simulation
```

配置选项见 `examples/g1_simulation_driver.json`。

---

## 多机器人仿真

在同一 Isaac Sim 场景中运行多台机器人：

```bash
# 示例：同一场景中的 PIPER + Go2 + Franka
python hal/hal_watchdog.py \
  --driver multi_robot_simulation \
  --driver-config examples/pipergo2_franka_same_scene_internutopia_config.json
```

如需为每台机器人使用独立工作区的 Fleet 模式，详见 [Fleet 模式指南](user_manual/03_FLEET_MODE_zh.md)。

---

## 常见问题排查

### 找不到 Isaac Sim

- 确认 Isaac Sim 5.1 已安装且 `isaacsim` 包在 Python 路径中
- 尝试：`python -c "import isaacsim; print(isaacsim.__version__)"`

### GUI 模式启动失败

- 检查 GPU 驱动和 CUDA 兼容性
- 尝试去掉 `--gui` 以无头模式运行
- 查看 Isaac Sim 日志中的渲染错误

### 仿真中动作未执行

- 确认只有一个看门狗在运行
- 检查 `--interval` 设置是否合适（0.05 对应 20Hz）
- 确认驱动配置 JSON 指向有效的场景文件（`.usd`）

---

## 下一步

- [用户手册：基础使用](user_manual/02_BASIC_USAGE_zh.md) 了解通用命令
- [本体接入指南](user_manual/04_EMBODIMENTS_zh.md) 了解如何接入真实机器人
- [插件开发指南](user_development_guide/PLUGIN_DEVELOPMENT_GUIDE_zh.md) 了解如何添加新仿真后端
