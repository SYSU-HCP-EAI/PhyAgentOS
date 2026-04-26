# ROS2 集成

> [English](ROS2_INTEGRATION.md) | **中文**

> **状态：开发中** — 本章涵盖计划中或部分实现的 ROS2 集成功能。部分章节描述的能力尚未完全稳定。

---

## 目录

- [当前 ROS2 覆盖范围](#当前-ros2-覆盖范围)
- [适配器架构](#适配器架构)
- [现有适配器](#现有适配器)
- [添加新适配器](#添加新适配器)
- [Topic 映射约定](#topic-映射约定)
- [导航栈集成](#导航栈集成)
- [计划功能](#计划功能)

---

## 当前 ROS2 覆盖范围

PhyAgentOS 目前通过 `hal/ros2/` 提供 ROS2 桥接支持：

- `cmd_vel` 适配器：发布速度指令
- `lidar` 适配器：接收激光雷达数据
- `odom` 适配器：读取里程计状态
- `rgbd` 适配器：接收 RGB-D 相机数据

这些适配器允许驱动与基于 ROS2 的机器人栈通信，而无需在每个驱动内部硬编码 ROS2 逻辑。

---

## 适配器架构

`hal/ros2/adapters/` 中的每个适配器遵循一致的模式：

1. **初始化**：用 topic 名和消息类型创建发布者/订阅者
2. **转换**：在 PhyAgentOS 内部状态与 ROS2 消息之间转换
3. **生命周期**：驱动启动时连接，驱动停止时断开

`hal/ros2/bridge.py` 负责编排给定驱动会话中的所有活动适配器。

---

## 现有适配器

| 适配器 | 方向 | ROS2 消息类型 | 用途 |
|---|---|---|---|
| `cmd_vel_adapter.py` | 发布 | `geometry_msgs/Twist` | 发送运动指令 |
| `lidar_adapter.py` | 订阅 | `sensor_msgs/LaserScan` | 接收障碍物数据 |
| `odom_adapter.py` | 订阅 | `nav_msgs/Odometry` | 接收位姿估计 |
| `rgbd_adapter.py` | 订阅 | `sensor_msgs/Image` + `sensor_msgs/CameraInfo` | 接收视觉数据 |

---

## 添加新适配器

1. 创建 `hal/ros2/adapters/my_sensor_adapter.py`
2. 继承基础适配器模式（或实现 init/translate/shutdown）
3. 在 `hal/ros2/bridge.py` 或相关驱动中注册
4. 在 `tests/test_ros2_*.py` 中添加测试

模板：

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
        # 将 ROS2 消息转换为 PhyAgentOS 状态
        pass
```

---

## Topic 映射约定

未提供覆盖时，PhyAgentOS 使用以下默认 topic 名：

| 用途 | 默认 Topic |
|---|---|
| 速度指令 | `/cmd_vel` |
| 里程计 | `/odom` |
| 激光雷达 | `/scan` |
| RGB 图像 | `/camera/color/image_raw` |
| 深度图像 | `/camera/depth/image_rect_raw` |
| 相机参数 | `/camera/color/camera_info` |

这些可以在驱动配置 JSON 的 `ros2` 键下覆盖。

---

## 导航栈集成

对于具备完整 ROS2 导航栈（如 Nav2）的机器人：

1. 驱动适配器向 `/goal_pose` 发布目标
2. 导航栈负责路径规划与避障
3. 驱动订阅 `/amcl_pose` 或 `/odom` 获取定位反馈
4. `get_runtime_state()` 将 `nav_state` 回写到 `ENVIRONMENT.md`

这使得 Agent 可以发布高层目标，而 ROS2 栈处理底层控制。

---

## 计划功能

以下 ROS2 功能计划在未来版本实现：

- **TF 树集成**：自动发现 TF 坐标系和变换
- **地图服务器**：从 `/map` 加载和更新占用栅格地图
- **动作服务器**：使用 ROS2 actions 处理长程任务（如 `navigate_to_pose`）
- **多机器人 ROS2**：Fleet 模式下支持 ROS2 命名空间

---

## 下一步

- [感知与导航](PERCEPTION_NAVIGATION_zh.md) 了解场景图构建
- [HAL 驱动开发](HAL_DRIVER_zh.md) 了解驱动端的 ROS2 集成
- 参考现有测试：`tests/test_go2_navigation_stack.py`
