# Perception & Navigation

> **English** | [中文](PERCEPTION_NAVIGATION_zh.md)

This guide explains how PhyAgentOS handles semantic navigation and multimodal perception.

---

## Table of Contents

- [Overview](#overview)
- [Perception Pipeline](#perception-pipeline)
- [Semantic Navigation](#semantic-navigation)
- [ROS2 Bridge](#ros2-bridge)
- [Environment Writeback](#environment-writeback)
- [Extending Perception](#extending-perception)

---

## Overview

PhyAgentOS bridges high-level semantic goals ("go to the kitchen table") with low-level physical coordinates through two key subsystems:

- **PerceptionService**: Converts raw sensor data into structured scene graphs
- **SemanticNavigationTool**: Resolves semantic targets into physical coordinates

---

## Perception Pipeline

Located in `hal/perception/`, the pipeline consists of four stages:

### 1. Geometry Pipeline (`geometry_pipeline.py`)

- Processes point clouds and odometry
- Extracts geometric features and obstacle information

### 2. Segmentation Pipeline (`segmentation_pipeline.py`)

- Uses vision models (e.g., SAM) to perform semantic segmentation
- Identifies object categories in the scene

### 3. Fusion Pipeline (`fusion_pipeline.py`)

- Combines geometric features with semantic labels
- Produces a unified scene graph with 3D coordinates, categories, and topological relationships

### 4. Environment Writer (`environment_writer.py`)

- Formats the fused scene graph into `ENVIRONMENT.md`
- Updates robot state, object positions, and map data

---

## Semantic Navigation

The `SemanticNavigationTool` (in `PhyAgentOS/agent/tools/target_navigation.py`) allows the Agent to resolve high-level navigation goals.

### How it works

1. **Target Resolution**: Reads `ENVIRONMENT.md` scene graph, locates target by `target_class`, `target_id`, or `zone_name`
2. **Pose Calculation**: Computes an approach pose based on robot current pose and target location
3. **Action Generation**: Produces a `target_navigation` action for `EmbodiedActionTool`

### Requirements

- The robot profile must declare navigation actions
- `ENVIRONMENT.md` must contain necessary target/map/state fields
- The driver must return sufficient navigation state in `get_runtime_state()`

---

## ROS2 Bridge

Located in `hal/ros2/`, the bridge connects PhyAgentOS to ROS2 ecosystems:

| File | Purpose |
|---|---|
| `bridge.py` | Bridge logic and topic routing |
| `messages.py` | Message structure definitions |
| `adapters/` | Concrete adapters for topics: `cmd_vel`, `lidar`, `odom`, `rgbd` |

To add a new ROS2 topic, create a new adapter in `hal/ros2/adapters/` rather than adding logic directly to a driver.

---

## Environment Writeback

After every action execution, the watchdog calls `driver.get_scene()` and `driver.get_runtime_state()`. The perception module then:

1. Updates the scene graph with new object positions
2. Refreshes robot pose and connection status
3. Writes everything back to `ENVIRONMENT.md`
4. Updates `ROBOTS.md` with a concise summary

This closed loop is what makes the Agent's next planning step grounded in fresh physical evidence.

---

## Extending Perception

To add a new perception modality:

1. Add a processing stage in `hal/perception/`
2. Ensure it outputs data compatible with `fusion_pipeline.py`
3. Update `EnvironmentWriter` to include new fields in `ENVIRONMENT.md`
4. Update the relevant robot profile to declare new sensor capabilities

---

## Next Steps

- [ROS2 Integration](ROS2_INTEGRATION.md) for deeper ROS2 topic mapping
- [HAL Driver Development](HAL_DRIVER.md) for adding navigation-capable drivers
- [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md) for packaging perception-heavy plugins
