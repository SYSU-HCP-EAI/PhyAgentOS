# Robot Embodiment Declaration

This file describes the physical capabilities and constraints of the connected robot.
The Critic Agent reads this file to validate whether proposed actions are safe and feasible.

## Identity

- **Name**: Unitree Go2 EDU
- **Type**: Quadruped mobile robot

## Sensors

- **RGB-D**: Optional front camera pipeline via adapter nodes
- **LiDAR**: Mid-360 / 4D LiDAR compatible
- **Odometry**: IMU + locomotion odometry

## Supported Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| `semantic_navigate` | `robot_id, target_ref, goal_pose, approach_distance, timeout_s` | Navigate to a semantic target using scene graph lookup and Nav2-compatible goals |
| `localize` | `robot_id, mode, timeout_s` | Trigger relocalization workflow |
| `stop` | `robot_id` | Stop the current navigation task |

## Navigation Capabilities

- **Frames**: `map`, `odom`, `base_link`, `camera_link`, `lidar`
- **Max linear speed**: 1.5 m/s
- **Max angular speed**: 1.0 rad/s
- **Minimum obstacle clearance**: 0.5 m
- **Relocalization support**: yes
- **ROS2 command channels**: `/cmd_vel`, `/navigate_to_pose`, `/initialpose`

## Physical Constraints

- **Operating area**: bounded by environment map or geofence declared in `ENVIRONMENT.md`
- **Collision policy**: stop and mark `nav_state.last_error` on unrecoverable obstruction
