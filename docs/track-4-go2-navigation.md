# Track 4: Unitree Go2 EDU — Quadruped Navigation

> Owner: TBD | Status: Planning | Priority: High

## 1. Objective

Build a driver for the Unitree Go2 EDU quadruped robot that enables LLM-controlled autonomous navigation. The Go2 receives high-level movement commands via `ACTION.md` (e.g., "walk to the kitchen") and uses its onboard 4D LiDAR + Jetson Orin for obstacle avoidance and localization.

## 2. Scope

### In Scope
- Implement `Go2Driver(BaseDriver)` in `hal/drivers/go2_driver.py`
- ROS2/DDS communication with Go2's onboard controller
- Navigation actions: `move_to`, `turn_to`, `follow_path`, `stop`
- Odometry and pose feedback → update `ENVIRONMENT.md` with robot position
- Basic obstacle avoidance (leveraging Go2's built-in capabilities)
- Write `hal/profiles/go2_edu.md` describing the Go2's capabilities

### Out of Scope
- Object manipulation (no arm)
- Vision-based object detection (handled by MCP Vision Server)
- Multi-robot coordination (Track 5)

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `hal/drivers/go2_driver.py` | Create | `Go2Driver(BaseDriver)` implementation |
| `hal/profiles/go2_edu.md` | Create | EMBODIED.md profile for Go2 EDU |
| `tests/test_go2_driver.py` | Create | Driver tests (with ROS2 mock) |

## 4. EMBODIED.md Profile Requirements

- Robot model: Unitree Go2 EDU
- Locomotion type: quadruped (12-DOF legs)
- Max speed: 3.7 m/s
- Sensors: 4D LiDAR, IMU, foot force sensors
- Compute: Jetson Orin (onboard)
- Communication: ROS2/DDS over WiFi or Ethernet
- Supported actions: `move_to`, `turn_to`, `follow_path`, `stop`, `sit`, `stand`
- Navigation constraints: max slope, step height, operating temperature
- No manipulation capability — explicitly stated

## 5. Action Specification

| Action | Parameters | Expected Behavior |
|--------|-----------|-------------------|
| `semantic_navigate` | `robot_id, target_ref, goal_pose, approach_distance, timeout_s` | Walk to a semantic target resolved from `scene_graph` |
| `move_to` | `x, y` (metres, map frame) | Walk to target position, avoid obstacles |
| `turn_to` | `heading: float` (degrees) | Rotate in place to target heading |
| `follow_path` | `waypoints: list of x,y` | Follow a sequence of waypoints |
| `stop` | — | Halt immediately |
| `sit` | — | Transition to sitting posture |
| `stand` | — | Transition to standing posture |

### Semantic Navigation Notes

- Agent-side target resolution happens in OEA tools, not inside the driver.
- The driver accepts concrete `goal_pose` and `target_ref` data from `ACTION.md`.
- Runtime state should be written back under `robots.<robot_id>.nav_state`.

### Navigation Feedback in ENVIRONMENT.md

```json
{
  "go2_robot": {
    "type": "quadruped",
    "position": {"x": 120, "y": 350, "z": 0},
    "heading": 45.0,
    "state": "walking",
    "battery": 85
  }
}
```

## 6. Milestones & Acceptance Criteria

### Milestone M1: Driver Scaffold
- [ ] `Go2Driver` exists in `hal/drivers/go2_driver.py` and imports without error
- [ ] Driver registered as `"go2_edu"` in registry
- [ ] `hal/profiles/go2_edu.md` exists with locomotion specs, sensor list, workspace geofence
- [ ] `pytest tests/test_hal_base_driver.py -k go2_edu` — all 10 contract tests green (mock/no-ROS mode)

### Milestone M2: ROS2 Communication
- [ ] `hal/hal_ros2_bridge.py` (or equivalent) can subscribe to `/odom` and publish to `/cmd_vel`
- [ ] `Go2Driver.load_scene()` initialises robot pose from `ENVIRONMENT.md` without error
- [ ] `get_scene()` reflects current odometry position in cm (updated at ≥ 2 Hz)

### Milestone M3: Navigation Commands (physical Go2 required)
- [ ] `move_to(x=200, y=0)` — robot walks to 2 m forward, arrives within 30 cm tolerance
- [ ] `stop({})` — robot halts within 500 ms of command receipt
- [ ] `turn_to(heading=90)` — robot rotates to face 90° within ±5°
- [ ] `sit({})` / `stand({})` — robot transitions to correct posture

### Milestone M4: Safety
- [ ] Out-of-geofence `move_to` is rejected by Critic (checks `EMBODIED.md` bounds)
- [ ] Battery < 10%: driver returns error string and refuses movement actions
- [ ] Emergency stop via `stop` action reaches robot in < 200 ms (measured with stopwatch)

### Milestone M5: Full Pipeline
- [ ] User types "go to the kitchen" in CLI → `ENVIRONMENT.md` contains a `kitchen` zone → Planner writes `move_to` → Watchdog dispatches → Robot navigates → `ENVIRONMENT.md` updates Go2 position
- [ ] `ENVIRONMENT.md` correctly shows `go2_robot.location = "kitchen"` after arrival

## 7. Dependencies

- ROS2 Humble (or later)
- `unitree_ros2` package (Unitree's official ROS2 driver)
- `rclpy` (ROS2 Python client)
- `nav2` (ROS2 Navigation2 stack, optional for path planning)
- Network access to Go2's onboard controller

## 8. ROS2 Integration Architecture

```
ACTION.md
    │
    ▼
┌──────────────┐
│ go2_driver.py │  ← Publishes to /cmd_vel or /navigate_to_pose
└──────┬───────┘
       │ ROS2 topics
       ▼
┌──────────────┐
│ Go2 onboard  │  ← Unitree controller handles low-level gait
│ controller   │
└──────┬───────┘
       │ /odom, /scan
       ▼
┌──────────────┐
│ go2_driver.py │  ← Subscribes to odometry, updates ENVIRONMENT.md
└──────────────┘
```

## 9. Safety Considerations

- **Geofence**: Define allowed operating area in `EMBODIED.md`; driver rejects `move_to` outside bounds
- **Emergency stop**: `/stop` action must have < 200ms latency
- **Battery monitoring**: Driver should report low battery in `ENVIRONMENT.md` and refuse actions below 10%
