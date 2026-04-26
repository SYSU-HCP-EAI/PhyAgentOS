# ROS2 Integration

> **English** | [中文](ROS2_INTEGRATION_zh.md)

> **Status: In Development** — This chapter covers planned and partially implemented ROS2 integration features. Some sections describe capabilities that are not yet fully stabilized.

---

## Table of Contents

- [Current ROS2 Coverage](#current-ros2-coverage)
- [Adapter Architecture](#adapter-architecture)
- [Existing Adapters](#existing-adapters)
- [Adding a New Adapter](#adding-a-new-adapter)
- [Topic Mapping Conventions](#topic-mapping-conventions)
- [Navigation Stack Integration](#navigation-stack-integration)
- [Planned Features](#planned-features)

---

## Current ROS2 Coverage

PhyAgentOS currently provides ROS2 bridge support through `hal/ros2/`:

- `cmd_vel` adapter: velocity command publishing
- `lidar` adapter: laser scan ingestion
- `odom` adapter: odometry state reading
- `rgbd` adapter: RGB-D camera data ingestion

These adapters allow drivers to communicate with ROS2-based robot stacks without hard-coding ROS2 logic inside each driver.

---

## Adapter Architecture

Each adapter in `hal/ros2/adapters/` follows a consistent pattern:

1. **Initialize**: Create publisher/subscriber with topic name and message type
2. **Translate**: Convert between PhyAgentOS internal state and ROS2 messages
3. **Lifecycle**: Connect on driver start, disconnect on driver stop

The `hal/ros2/bridge.py` orchestrates all active adapters for a given driver session.

---

## Existing Adapters

| Adapter | Direction | ROS2 Message Type | Purpose |
|---|---|---|---|
| `cmd_vel_adapter.py` | Publish | `geometry_msgs/Twist` | Send movement commands |
| `lidar_adapter.py` | Subscribe | `sensor_msgs/LaserScan` | Receive obstacle data |
| `odom_adapter.py` | Subscribe | `nav_msgs/Odometry` | Receive pose estimates |
| `rgbd_adapter.py` | Subscribe | `sensor_msgs/Image` + `sensor_msgs/CameraInfo` | Receive visual data |

---

## Adding a New Adapter

1. Create `hal/ros2/adapters/my_sensor_adapter.py`
2. Inherit from a base adapter pattern (or implement init/translate/shutdown)
3. Register in `hal/ros2/bridge.py` or the relevant driver
4. Add tests in `tests/test_ros2_*.py`

Template:

```python
class MySensorAdapter:
    def __init__(self, node, topic_name: str):
        self._node = node
        self._topic = topic_name
        self._sub = None

    def connect(self):
        self._sub = self._node.create_subscription(
            MySensorMsg, self._topic, self._on_message, 10
        )

    def disconnect(self):
        if self._sub:
            self._node.destroy_subscription(self._sub)

    def _on_message(self, msg):
        # Translate ROS2 message to PhyAgentOS state
        pass
```

---

## Topic Mapping Conventions

PhyAgentOS uses these default topic names when no override is given:

| Purpose | Default Topic |
|---|---|
| Velocity commands | `/cmd_vel` |
| Odometry | `/odom` |
| Laser scan | `/scan` |
| RGB image | `/camera/color/image_raw` |
| Depth image | `/camera/depth/image_rect_raw` |
| Camera info | `/camera/color/camera_info` |

These can be overridden in the driver config JSON under a `ros2` key.

---

## Navigation Stack Integration

For robots with a full ROS2 navigation stack (e.g., Nav2):

1. The driver adapter publishes goals to `/goal_pose`
2. The navigation stack handles path planning and obstacle avoidance
3. The driver subscribes to `/amcl_pose` or `/odom` for localization feedback
4. `get_runtime_state()` reports `nav_state` back to `ENVIRONMENT.md`

This allows the Agent to issue high-level goals while the ROS2 stack handles low-level control.

---

## Planned Features

The following ROS2 features are planned for future releases:

- **TF Tree Integration**: Automatic TF frame discovery and transformation
- **Map Server**: Load and update occupancy grids from `/map`
- **Action Server**: Use ROS2 actions for long-running tasks (e.g., `navigate_to_pose`)
- **Multi-Robot ROS2**: Support for ROS2 namespaces in fleet mode

---

## Next Steps

- [Perception & Navigation](PERCEPTION_NAVIGATION.md) for scene graph construction
- [HAL Driver Development](HAL_DRIVER.md) for driver-side ROS2 integration
- See existing tests: `tests/test_go2_navigation_stack.py`
