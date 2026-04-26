# HAL Driver Development

> **English** | [中文](HAL_DRIVER_zh.md)

This guide explains how to implement a new HAL driver, write an embodiment profile, and register it in PhyAgentOS.

---

## Table of Contents

- [When to Build a Built-in Driver vs a Plugin](#when-to-build-a-built-in-driver-vs-a-plugin)
- [The BaseDriver Contract](#the-basedriver-contract)
- [Minimal Driver Implementation](#minimal-driver-implementation)
- [Profile: What to Include](#profile-what-to-include)
- [Registration Flow](#registration-flow)
- [driver-config JSON Pattern](#driver-config-json-pattern)
- [Testing Your Driver](#testing-your-driver)
- [Common Patterns](#common-patterns)

---

## When to Build a Built-in Driver vs a Plugin

| Built-in Driver (modify main repo) | External Plugin (separate repo) |
|---|---|
| Fix existing driver bugs | Heavy third-party SDK dependency |
| Enhance built-in simulation | Proprietary vendor runtime |
| Universally useful changes | Complex deployment logic |
| Small, self-contained additions | Independent versioning desired |

For plugins, see [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md).

---

## The BaseDriver Contract

All drivers must inherit from `hal/base_driver.py`. Four abstract methods are required:

| Method | Purpose |
|---|---|
| `get_profile_path()` | Returns the Path to the embodiment profile `.md` file |
| `load_scene(scene)` | Initializes internal state from the parsed `ENVIRONMENT.md` scene |
| `execute_action(action_type, params)` | Executes one action, returns human-readable result string |
| `get_scene()` | Returns current environment state dict for `ENVIRONMENT.md` update |

Optional but commonly useful:

| Method | Purpose |
|---|---|
| `connect()` | Establish hardware connection |
| `disconnect()` | Tear down hardware connection |
| `is_connected()` | Return current connection boolean |
| `health_check()` | Lightweight health probe |
| `get_runtime_state()` | Return runtime status for environment writeback |

---

## Minimal Driver Implementation

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
            # ... actual hardware call ...
            return f"moved to ({x}, {y}, {z})"
        return f"unknown action: {action_type}"

    def get_scene(self) -> dict[str, dict]:
        return dict(self._scene)
```

---

## Profile: What to Include

The profile is a "hardware instruction sheet for the Agent." A good profile includes:

- **Identity**: robot name, type, manufacturer
- **Sensors**: what sensors are available and their specs
- **Supported Actions**: exhaustive list of action types with parameter schemas
- **Physical Constraints**: workspace bounds, max load, max speed, joint limits
- **Connection**: how to connect, IP/port, protocol
- **Runtime Protocol Mapping**: how action names map to hardware commands

Reference profiles:
- `hal/profiles/simulation.md`
- `hal/profiles/go2_edu.md`
- `hal/profiles/franka_research3.md`

---

## Registration Flow

### For built-in drivers

1. Implement driver in `hal/drivers/my_robot_driver.py`
2. Add profile in `hal/profiles/my_robot.md`
3. Register in `hal/drivers/__init__.py`:

```python
from .my_robot_driver import MyRobotDriver

DRIVER_REGISTRY = {
    # ... existing entries ...
    "my_robot": MyRobotDriver,
}
```

4. Test: `python hal/hal_watchdog.py --driver my_robot`

---

## driver-config JSON Pattern

Watchdog passes the JSON config object directly to the driver constructor:

```bash
python hal/hal_watchdog.py \
  --driver my_robot \
  --driver-config examples/my_robot.driver.json
```

Example `my_robot.driver.json`:

```json
{
  "ip": "192.168.1.100",
  "port": 502,
  "control_rate": 100,
  "safe_max_speed": 0.5
}
```

These keys arrive as `**kwargs` in `__init__`.

---

## Testing Your Driver

Recommended test layers:

1. **Unit test**: mock hardware, test action routing
2. **Smoke test**: `python hal/hal_watchdog.py --driver my_robot`
3. **Dry-run**: execute without motion (`execute_motion: false`)
4. **Full loop**: `paos agent -m "do something with my_robot"`

---

## Common Patterns

### Pattern 1: Driver stays thin, runtime handles complexity

The ReKep plugin demonstrates this: `ReKepRealDriver` adapts the BaseDriver interface, while `runtime/dobot_bridge.py` handles all real-world execution logic.

### Pattern 2: Action dispatch table

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
    return f"unsupported action: {action_type}"
```

### Pattern 3: State synchronization

Always implement `get_runtime_state()` to return connection status, battery, current pose, etc. This data is written back to `ENVIRONMENT.md` so the Agent and Critic can reason about it.

---

## Next Steps

- Build an external plugin: [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)
- Understand the protocol: [Communication Architecture](COMMUNICATION.md)
- See existing tests: `tests/test_hal_base_driver.py`
