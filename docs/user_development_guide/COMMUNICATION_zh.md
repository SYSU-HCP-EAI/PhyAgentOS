# 通信架构说明

> [English](COMMUNICATION.md) | **中文**

本文说明 PhyAgentOS 在运行时如何通信。

---

## 目录

- [核心原则](#核心原则)
- [工作区拓扑](#工作区拓扑)
- [文件职责](#文件职责)
- [模板与 Profile 的区别](#模板与-profile-的区别)
- [谁读取什么](#谁读取什么)
- [典型运行流程](#典型运行流程)
- [设计意图](#设计意图)

---

## 核心原则

PhyAgentOS 采用 Markdown-first 设计：

- Track A（Agent 侧）负责理解、规划、校验。
- Track B（HAL 侧）负责通过 driver 和 watchdog 执行。
- 跨层共享状态优先通过 Markdown 文件暴露，而不是直接跨层 Python 调用。

---

## 工作区拓扑

### 单实例模式

- 只有一个 workspace，通常是 `~/.PhyAgentOS/workspace`
- Agent 和 watchdog 围绕同一个运行目录工作

### Fleet 模式

- 一个 shared workspace，通常是 `~/.PhyAgentOS/workspaces/shared`
- 每个机器人实例一个 robot workspace，例如：
  - `~/.PhyAgentOS/workspaces/go2_edu_001`
  - `~/.PhyAgentOS/workspaces/desktop_pet_001`

---

## 文件职责

### 共享工作区文件

- `ENVIRONMENT.md`
  - 全局环境真相源
  - 保存 scene graph、map、TF 和各机器人的运行态
- `ROBOTS.md`
  - 自动生成的机器人目录
  - 摘要记录 robot id、driver、类型、简要能力、workspace、启用状态、连接状态、导航状态
- `LESSONS.md`
  - 共享失败经验和动作拒绝记录
- `TASK.md`
  - 多步骤任务拆解状态
- `ORCHESTRATOR.md`
  - 全局监督与协调状态

### 机器人工作区文件

- `ACTION.md`
  - 单个机器人实例自己的动作队列
- `EMBODIED.md`
  - 从 `hal/profiles/*.md` 复制来的运行时机器人 profile
  - 被 Critic 用来校验这台机器人的具体动作

---

## 模板与 Profile 的区别

`PhyAgentOS/templates/EMBODIED.md` 只是结构模板。它用于说明：

- `EMBODIED.md` 应包含哪些 section
- 每个 section 的作用是什么
- 哪些信息属于静态 profile
- 哪些信息应该写进运行态文件

具体机器人参数必须写在 `hal/profiles/*.md`。

---

## 谁读取什么

### Planner / 主 Agent

默认主要读取 shared workspace：
- `ENVIRONMENT.md`
- `ROBOTS.md`
- `LESSONS.md`
- `TASK.md`
- `ORCHESTRATOR.md`

在 fleet 模式下，不会默认把每台机器人的完整 profile 全量注入上下文。

### Critic（通过 `EmbodiedActionTool`）

对某个机器人做动作校验时，会读取：
- shared `ENVIRONMENT.md`
- 目标机器人的 runtime `EMBODIED.md`
- 当前动作草案与 reasoning

也就是说，针对具体机器人能力的精确判断发生在动作派发阶段。

### Watchdog

每个 watchdog 实例读取：
- 自己 robot workspace 里的 `ACTION.md`
- shared `ENVIRONMENT.md`

每个 watchdog 写入：
- 自己 robot workspace 里的 runtime `EMBODIED.md`
- shared `ENVIRONMENT.md` 里的本机器人运行态
- shared `ROBOTS.md` 里的摘要目录

---

## 典型运行流程

1. `paos onboard` 准备工作区。
2. Fleet 配置定义有哪些机器人实例。
3. shared `ROBOTS.md` 根据配置和运行摘要自动生成。
4. 用户为每个机器人实例启动一个 watchdog。
5. watchdog 将该机器人的 profile 安装为 runtime `EMBODIED.md`。
6. 用户启动 `paos agent`。
7. Agent 基于 shared 状态规划并选择机器人。
8. `EmbodiedActionTool` 使用目标机器人的 runtime `EMBODIED.md` 做校验。
9. 动作被写入该机器人 workspace 的 `ACTION.md`。
10. 对应 watchdog 执行动作，并把运行结果回写到 shared 文件。

---

## 设计意图

- 让 shared 上下文足够简洁，便于规划
- 让机器人级校验保持精确
- 让运行态保持可见、可检查
- 避免把硬件事实藏在不可见的黑盒代码路径里
