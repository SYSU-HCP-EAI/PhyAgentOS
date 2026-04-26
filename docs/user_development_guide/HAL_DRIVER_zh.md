# HAL 驱动开发

> [English](HAL_DRIVER.md) | **中文**

本指南说明如何实现新的 HAL 驱动、编写本体 profile 并在 PhyAgentOS 中注册。

---

## 目录

- [何时做内置驱动，何时做插件](#何时做内置驱动何时做插件)
- [BaseDriver 契约](#basedriver-契约)
- [最小驱动实现](#最小驱动实现)
- [Profile 应包含什么](#profile-应包含什么)
- [注册流程](#注册流程)
- [driver-config JSON 模式](#driver-config-json-模式)
- [测试驱动](#测试驱动)
- [常见模式](#常见模式)

---

## 何时做内置驱动，何时做插件

| 内置驱动（修改主仓库） | 外部插件（独立仓库） |
|---|---|
| 修复已有驱动 bug | 依赖较重的第三方 SDK |
| 增强内置仿真 | 厂商私有运行时 |
| 对全体用户有用的改动 | 复杂的部署逻辑 |
| 小而自包含的新增 | 希望独立发版 |

插件开发详见 [插件开发指南](PLUGIN_DEVELOPMENT_GUIDE_zh.md)。

---

## BaseDriver 契约

所有驱动都必须继承 `hal/base_driver.py`。必须实现四个抽象方法：

| 方法 | 用途 |
|---|---|
| `get_profile_path()` | 返回本体 profile `.md` 文件的路径 |
| `load_scene(scene)` | 从解析后的 `ENVIRONMENT.md` scene 初始化内部状态 |
| `execute_action(action_type, params)` | 执行一个动作，返回人类可读的结果字符串 |
| `get_scene()` | 返回当前环境状态字典，用于更新 `ENVIRONMENT.md` |

可选但常用：

| 方法 | 用途 |
|---|---|
| `connect()` | 建立硬件连接 |
| `disconnect()` | 断开硬件连接 |
| `is_connected()` | 返回当前连接状态 |
| `health_check()` | 轻量健康检查 |
| `get_runtime_state()` | 返回运行时状态用于环境回写 |

---

## 最小驱动实现

```python
from pathlib import Path
from hal.base_driver import BaseDriver


class MyRobotDriver(BaseDriver):
    def __init__(self, gui: bool = False, **kwargs):
        super().__init__(gui=gui, **kwargs)
        self._scene = {}

    def get_profile_path(self) -> Path:
        return Path(__file__).resolve().parent / "profiles" / "my_robot.md"

    def load_scene(self, scene: dict[str, dict]) -> None:
        self._scene = dict(scene)

    def execute_action(self, action_type: str, params: dict) -> str:
        if action_type == "move_to":
            x = params.get("x", 0)
            y = params.get("y", 0)
            z = params.get("z", 0)
            return f"移动到 ({x}, {y}, {z})"
        return f"未知动作: {action_type}"

    def get_scene(self) -> dict[str, dict]:
        return dict(self._scene)
```

---

## Profile 应包含什么

Profile 是"给 Agent 看的硬件说明书"。一个好的 profile 应包含：

- **身份**：机器人名称、类型、制造商
- **传感器**：可用传感器及其规格
- **支持动作**：完整的动作类型列表及参数模式
- **物理约束**：工作空间边界、最大负载、最大速度、关节极限
- **连接方式**：连接方法、IP/端口、协议
- **运行时协议映射**：动作名称如何映射到硬件命令

参考 profile：
- `hal/profiles/simulation.md`
- `hal/profiles/go2_edu.md`
- `hal/profiles/franka_research3.md`

---

## 注册流程

### 内置驱动

1. 在 `hal/drivers/my_robot_driver.py` 实现驱动
2. 在 `hal/profiles/my_robot.md` 添加 profile
3. 在 `hal/drivers/__init__.py` 注册：

```python
from .my_robot_driver import MyRobotDriver

DRIVER_REGISTRY = {
    "my_robot": MyRobotDriver,
}
```

4. 测试：`python hal/hal_watchdog.py --driver my_robot`

---

## driver-config JSON 模式

看门狗将 JSON 配置对象直接透传给驱动构造器：

```bash
python hal/hal_watchdog.py \
  --driver my_robot \
  --driver-config examples/my_robot.driver.json
```

示例 `my_robot.driver.json`：

```json
{
  "ip": "192.168.1.100",
  "port": 502,
  "control_rate": 100,
  "safe_max_speed": 0.5
}
```

这些键以 `**kwargs` 形式传入 `__init__`。

---

## 测试驱动

推荐测试层次：

1. **单元测试**：mock 硬件，测试动作路由
2. **冒烟测试**：`python hal/hal_watchdog.py --driver my_robot`
3. **Dry-run**：不带真实运动执行
4. **全链路联调**：`paos agent -m "用 my_robot 做点什么"`

---

## 常见模式

### 模式 1：驱动保持薄，runtime 处理复杂逻辑

ReKep 插件展示了这一点：`ReKepRealDriver` 适配 BaseDriver 接口，而 `runtime/dobot_bridge.py` 处理所有真机执行逻辑。

### 模式 2：动作分发表

```python
def execute_action(self, action_type: str, params: dict) -> str:
    dispatcher = {
        "move_to": self._do_move_to,
        "grasp": self._do_grasp,
        "stop": self._do_stop,
    }
    handler = dispatcher.get(action_type)
    if handler:
        return handler(params)
    return f"不支持的动作: {action_type}"
```

### 模式 3：状态同步

务必实现 `get_runtime_state()` 返回连接状态、电量、当前位姿等信息。这些数据回写到 `ENVIRONMENT.md`，供 Agent 和 Critic 推理使用。

---

## 下一步

- 开发外部插件：[插件开发指南](PLUGIN_DEVELOPMENT_GUIDE_zh.md)
- 理解通信协议：[通信架构](COMMUNICATION_zh.md)
- 参考现有测试：`tests/test_hal_base_driver.py`
