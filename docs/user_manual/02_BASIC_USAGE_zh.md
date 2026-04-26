# 02 - 基础使用

> [English](02_BASIC_USAGE.md) | **中文**

本章涵盖核心 CLI 命令、单机模式操作以及如何与 Agent 交互。

---

## 目录

- [理解双轨架构](#理解双轨架构)
- [核心 CLI 命令](#核心-cli-命令)
- [单机模式快速开始](#单机模式快速开始)
- [命令速查表](#命令速查表)
- [运行时 Markdown 文件](#运行时-markdown-文件)
- [常见交互示例](#常见交互示例)
- [常见问题排查](#常见问题排查)

---

## 理解双轨架构

PhyAgentOS 将认知与执行显式解耦：

- **Track A（大脑）**：`paos agent` 或 `paos gateway` —— 负责理解、规划、通过 Critic 校验动作
- **Track B（HAL）**：`python hal/hal_watchdog.py` —— 读取 `ACTION.md`，通过 driver 执行，回写 `ENVIRONMENT.md`

两者通过工作区 Markdown 文件通信，而非直接 Python 调用。

---

## 核心 CLI 命令

### `paos onboard`

初始化或刷新工作区和配置模板。

```bash
paos onboard
```

安装后、升级后、或切换 single/fleet 模式后都应执行。

### `paos agent`

交互式 CLI，支持单轮或多轮对话。

```bash
# 交互模式
paos agent

# 单轮模式
paos agent -m "看看周围有什么"
```

### `paos gateway`

长期在线服务模式，支持渠道接入（飞书、Slack 等）、心跳与定时任务。

```bash
paos gateway
```

当需要 Agent 保持在线并响应外部渠道消息时使用此模式。

---

## 单机模式快速开始

### 第一步：初始化

```bash
paos onboard
```

### 第二步：启动 HAL 看门狗（Track B）

```bash
# 终端 A
python hal/hal_watchdog.py --driver simulation
```

看门狗会：
- 加载 `simulation` 驱动
- 将驱动 profile 复制为 `EMBODIED.md`
- 定期轮询 `ACTION.md`
- 执行动作并更新 `ENVIRONMENT.md`

### 第三步：启动 Agent（Track A）

```bash
# 终端 B
paos agent
```

在提示符处输入自然语言指令。

### 第四步：观察文件变化

关注以下文件以理解运行时闭环：

| 文件 | 检查要点 |
|---|---|
| `EMBODIED.md` | 机器人 profile 是否正确安装？ |
| `ACTION.md` | Agent 是否成功写入待执行动作？ |
| `ENVIRONMENT.md` | 动作执行后环境状态是否更新？ |
| `LESSONS.md` | Critic 是否拒绝了某些动作？ |

---

## 命令速查表

| 目标 | 命令 |
|---|---|
| 初始化工作区 | `paos onboard` |
| 交互式 Agent | `paos agent` |
| 单轮发送消息 | `paos agent -m "..."` |
| 启动网关服务 | `paos gateway` |
| 启动仿真看门狗 | `python hal/hal_watchdog.py --driver simulation` |
| 指定工作区启动 | `python hal/hal_watchdog.py --workspace <path> --driver <name>` |
| 传入驱动配置 | `python hal/hal_watchdog.py --driver <name> --driver-config <file>` |
| 运行测试 | `pytest tests/` |

---

## 运行时 Markdown 文件

这些文件是 Track A 与 Track B 之间的共享状态：

| 文件 | 位置 | 作用 |
|---|---|---|
| `ACTION.md` | 工作区根目录 | 待执行动作队列 |
| `EMBODIED.md` | 工作区根目录 | 机器人能力、约束与连接状态 |
| `ENVIRONMENT.md` | 工作区根目录 | 当前场景图、物体与机器人状态 |
| `LESSONS.md` | 工作区根目录 | Critic 记录的失败经验 |
| `TASK.md` | 工作区根目录 | 多步骤任务拆解状态 |
| `ORCHESTRATOR.md` | 工作区根目录 | 编排层状态 |

Fleet 模式详见 [03 Fleet 模式](03_FLEET_MODE_zh.md)。

---

## 常见交互示例

### 环境查询

```text
桌子上有什么物体？
```

验证：Agent 能读取 `ENVIRONMENT.md`，看门狗能正确回写。

### 抓取/操作任务

```text
把桌上的红苹果拿起来，放到托盘里。
```

验证：目标物体存在于场景中，机器人支持 `pick_up`/`put_down`，看门狗执行后清空 `ACTION.md`。

### 导航任务

```text
移动到冰箱附近并停下。
```

验证：语义位置存在于场景图中，机器人支持导航动作。

---

## 常见问题排查

### 提示没有 API Key

- 检查 `~/.PhyAgentOS/config.json`
- 确认 `agents.defaults.model` 与已配置的提供方匹配
- 确认该提供方已填写有效 `api_key`

### 找不到 `EMBODIED.md`

- 执行 `paos onboard`
- 确认看门狗已成功启动
- 确认所选驱动的 profile 文件存在且可读

### `ACTION.md` 有内容但动作未执行

- 确认对应看门狗仍在运行
- 检查 `ACTION.md` 中 JSON 代码块格式是否完整
- 查看看门狗终端是否有驱动报错
- 检查 `driver-config` 是否缺失关键参数

### 动作被 Critic 拒绝

- 查看 `LESSONS.md` 了解拒绝原因
- 确认动作已在 `EMBODIED.md` 的 Supported Actions 中声明
- 确认目标物体/位置存在于 `ENVIRONMENT.md`

---

## 下一步

- 接入真实机器人：[04 - 本体接入指南](04_EMBODIMENTS_zh.md)
- 多机器人协同：[03 - Fleet 模式](03_FLEET_MODE_zh.md)
- 开发插件：[插件开发指南](../user_development_guide/PLUGIN_DEVELOPMENT_GUIDE_zh.md)
