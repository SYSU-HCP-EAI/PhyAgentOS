# Track 8: Semantic Navigation Stack

> Owner: TBD | Status: In Progress | Priority: High

## 1. Objective

Integrate the `new_module.md` design into OpenEmbodiedAgent as a Markdown-first semantic navigation subsystem. The stack keeps Track A and Track B decoupled while adding a scene-graph-aware navigation toolchain, ROS2 bridge layer, and side-loaded perception daemon.

## 2. Scope

### In Scope
- Expand `ENVIRONMENT.md` and `EMBODIED.md` protocol fields for semantic navigation
- Add OEA tools for scene-graph query and semantic navigation dispatch
- Add a navigation-oriented Go2 driver with mock-friendly runtime state
- Add a thin ROS2 bridge abstraction and adapter skeletons
- Add a side-loaded perception daemon skeleton that writes back to `ENVIRONMENT.md`
- Preserve compatibility with current `objects`-based HAL drivers

### Out of Scope
- Full production ROS2/Nav2 integration details
- Real FAST-LIO2 / YOLOv8-Seg deployments
- Multi-robot orchestration and manipulation planning

## 3. Public Protocol Extensions

### ENVIRONMENT.md
- `scene_graph.nodes[]`: `id`, `class`, `object_key`, `center`, `size`, `confidence`, `frame`, `track_id`, `last_seen_at`
- `scene_graph.edges[]`: `source`, `relation`, `target`, `confidence`
- `robots.<robot_id>.robot_pose`: `frame`, `x`, `y`, `z`, `yaw`, `stamp`, `covariance?`
- `robots.<robot_id>.nav_state`: `mode`, `status`, `goal_id`, `target_ref`, `goal`, `path_progress`, `recovery_count`, `last_error`, `relocalization_confidence?`
- `map`: `frame`, `resolution`, `origin`, `image_path?`, `zones?`, `stamp?`
- `tf`: summarized transform availability and timestamps

### ACTION.md
- `semantic_navigate`: `robot_id`, `target_ref`, `goal_pose`, `approach_distance`, `timeout_s`
- `localize`: `robot_id`, `mode`, `timeout_s`

### EMBODIED.md
- Navigation capabilities, supported frames, minimum obstacle clearance, relocalization support, and ROS2 command channels

## 4. Runtime Architecture

1. Agent resolves a semantic target from `scene_graph`.
2. `SemanticNavigationTool` computes an approach pose and dispatches `semantic_navigate`.
3. `EmbodiedActionTool` validates safety and writes `ACTION.md`.
4. `hal_watchdog.py` forwards the action to the active driver.
5. The navigation driver updates robot runtime state.
6. The side-loaded perception service keeps `scene_graph`, `map`, `tf`, and pose fresh in `ENVIRONMENT.md`.

## 5. Milestones

- M1: Protocol docs and templates updated
- M2: `query_scene_graph` and `semantic_navigate` tools registered
- M3: `go2_edu` driver passes contract tests in mock mode
- M4: watchdog preserves `scene_graph`, `robots`, `map`, and `tf` on writes
- M5: side-loaded perception service can write environment updates without breaking the Markdown envelope
