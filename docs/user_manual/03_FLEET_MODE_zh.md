# 03 - Fleet 多机模式

> [English](03_FLEET_MODE.md) | **中文**

Fleet 模式支持一个 Agent 同时规划和协同多台异构机器人运行。

---

## 目录

- [何时使用 Fleet 模式](#何时使用-fleet-模式)
- [配置方法](#配置方法)
- [启动顺序](#启动顺序)
- [工作区拓扑](#工作区拓扑)
- [Fleet 模式下的交互](#fleet-模式下的交互)
- [常见问题排查](#常见问题排查)

---

## 何时使用 Fleet 模式

以下场景应启用 Fleet 模式：

- 需要让一个 Agent 面向多个机器人实例协同规划
- 需要共享环境与机器人私有动作队列分开维护
- 需要每台机器人拥有独立的 `EMBODIED.md` 与 `ACTION.md`

---

## 配置方法

编辑 `~/.PhyAgentOS/config.json`：

```json
{
  "embodiments": {
    "mode": "fleet",
    "shared_workspace": "~/.PhyAgentOS/workspaces/shared",
    "instances": [
      {
        "robot_id": "go2_edu_001",
        "driver": "go2_edu",
        "workspace": "~/.PhyAgentOS/workspaces/go2_edu_001"
      },
      {
        "robot_id": "franka_lab_001",
        "driver": "franka_multi",
        "workspace": "~/.PhyAgentOS/workspaces/franka_lab_001"
      }
    ]
  }
}
```

编辑后执行：

```bash
paos onboard
```

---

## 启动顺序

1. 配置 `embodiments.mode = "fleet"`
2. 执行 `paos onboard`
3. 为每个机器人实例启动一个看门狗
4. 启动一个 `paos agent` 或 `paos gateway`

示例：

```bash
# 终端 A：Go2 看门狗
python hal/hal_watchdog.py \
  --robot-id go2_edu_001 \
  --driver-config examples/go2_driver_config.json

# 终端 B：Franka 看门狗
python hal/hal_watchdog.py \
  --robot-id franka_lab_001 \
  --driver-config examples/franka_research3.driver.json

# 终端 C：Agent
paos agent
```

> 在 Fleet 模式下，`--robot-id` 决定该看门狗绑定哪个机器人实例；驱动名从 `config.json` 中解析。

---

## 工作区拓扑

```text
~/.PhyAgentOS/workspaces/
├── shared/
│   ├── ENVIRONMENT.md      # 全局环境状态
│   ├── ROBOTS.md           # 自动生成的机器人目录
│   ├── TASK.md             # 多步任务状态
│   ├── ORCHESTRATOR.md     # 协调状态
│   └── LESSONS.md          # 共享失败经验
├── go2_edu_001/
│   ├── ACTION.md           # 该机器人的动作队列
│   └── EMBODIED.md         # 该机器人的运行时 profile
└── franka_lab_001/
    ├── ACTION.md
    └── EMBODIED.md
```

---

## Fleet 模式下的交互

用户指令应尽量明确指出目标机器人：

```text
让 Go2 先去门口巡检，再让机械臂把桌上的包裹抓起来。
```

Agent 的工作流程：
1. 读取 `ROBOTS.md` 发现可用机器人
2. 读取 `ENVIRONMENT.md` 获取共享场景状态
3. 将动作分发到对应机器人的工作区
4. Critic 针对每台机器人的 `EMBODIED.md` 校验动作

---

## 常见问题排查

### 任务没有派发到正确机器人

- 检查配置中的 `robot_id`、`driver`、`workspace` 是否匹配
- 确认看门狗是通过 `--robot-id` 启动的
- 检查共享工作区的 `ROBOTS.md` 是否已正确生成
- 确认指令中明确指出了目标机器人

### 一台机器人的动作影响了另一台

- 确认每个看门狗绑定到不同的工作区
- 确认 `robot_id` 值唯一

---

## 下一步

- [04 - 本体接入指南](04_EMBODIMENTS_zh.md) 了解各机器人的具体启动方式
- [开发指南](../user_development_guide/README_zh.md) 了解 Fleet 架构内部实现
