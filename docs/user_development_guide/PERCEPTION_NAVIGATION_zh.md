# 感知与导航

> [English](PERCEPTION_NAVIGATION.md) | **中文**

本指南说明 PhyAgentOS 如何处理语义导航和多模态感知。

---

## 目录

- [概览](#概览)
- [感知管线](#感知管线)
- [语义导航](#语义导航)
- [ROS2 桥接](#ros2-桥接)
- [环境回写](#环境回写)
- [扩展感知能力](#扩展感知能力)

---

## 概览

PhyAgentOS 通过两个关键子系统把高层语义目标（"移动到厨房的桌子旁"）解析为底层物理坐标：

- **PerceptionService**：将原始传感器数据转化为结构化场景图
- **SemanticNavigationTool**：将语义目标解析为物理坐标

---

## 感知管线

位于 `hal/perception/`，管线分为四个阶段：

### 1. 几何管线（`geometry_pipeline.py`）

- 处理点云和里程计数据
- 提取几何特征和障碍物信息

### 2. 分割管线（`segmentation_pipeline.py`）

- 使用视觉模型（如 SAM）进行语义分割
- 识别场景中的物体类别

### 3. 融合管线（`fusion_pipeline.py`）

- 将几何特征与语义标签结合
- 生成包含三维坐标、类别和拓扑关系的统一场景图

### 4. 环境写回（`environment_writer.py`）

- 将融合后的场景图格式化为 `ENVIRONMENT.md`
- 更新机器人状态、物体位置和地图数据

---

## 语义导航

`SemanticNavigationTool`（位于 `PhyAgentOS/agent/tools/target_navigation.py`）允许 Agent 解析高层导航目标。

### 工作原理

1. **目标解析**：读取 `ENVIRONMENT.md` 场景图，根据 `target_class`、`target_id` 或 `zone_name` 定位目标
2. **位姿计算**：结合机器人当前位姿和目标位置计算接近位姿
3. **动作生成**：为 `EmbodiedActionTool` 生成 `target_navigation` 动作

### 前提条件

- 机器人 profile 必须声明导航动作
- `ENVIRONMENT.md` 必须包含必要的目标/地图/状态字段
- 驱动必须在 `get_runtime_state()` 中返回足够的导航状态

---

## ROS2 桥接

位于 `hal/ros2/`，桥接模块连接 PhyAgentOS 与 ROS2 生态：

| 文件 | 用途 |
|---|---|
| `bridge.py` | 桥接逻辑与 topic 路由 |
| `messages.py` | 消息结构定义 |
| `adapters/` | 具体 topic 适配器：`cmd_vel`、`lidar`、`odom`、`rgbd` |

如需接入新的 ROS2 topic，建议在 `hal/ros2/adapters/` 中创建新适配器，而非在驱动内部堆砌临时逻辑。

---

## 环境回写

每次动作执行后，看门狗调用 `driver.get_scene()` 和 `driver.get_runtime_state()`。感知模块随后：

1. 用新物体位置更新场景图
2. 刷新机器人位姿和连接状态
3. 将所有信息回写到 `ENVIRONMENT.md`
4. 在 `ROBOTS.md` 中更新摘要

这个闭环使 Agent 的下一步规划基于最新的物理证据。

---

## 扩展感知能力

如需添加新的感知模态：

1. 在 `hal/perception/` 中添加处理阶段
2. 确保输出数据与 `fusion_pipeline.py` 兼容
3. 更新 `EnvironmentWriter` 在 `ENVIRONMENT.md` 中包含新字段
4. 更新相关机器人 profile 声明新的传感器能力

---

## 下一步

- [ROS2 集成](ROS2_INTEGRATION_zh.md) 了解更深入的 ROS2 topic 映射
- [HAL 驱动开发](HAL_DRIVER_zh.md) 了解如何添加支持导航的驱动
- [插件开发指南](PLUGIN_DEVELOPMENT_GUIDE_zh.md) 了解如何打包重感知插件
