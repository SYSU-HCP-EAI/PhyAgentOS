from __future__ import annotations

import json
from pathlib import Path

from hal.drivers import load_driver
from hal.hal_watchdog import _poll_once
from hal.simulation.scene_io import load_environment_doc, save_environment_doc

_FENCE_OPEN = "```json"
_FENCE_CLOSE = "```"


def _write_action(path: Path, payload: dict) -> Path:
    action_file = path / "ACTION.md"
    action_file.write_text(
        f"{_FENCE_OPEN}\n{json.dumps(payload, indent=2)}\n{_FENCE_CLOSE}\n",
        encoding="utf-8",
    )
    return action_file


def _base_environment() -> dict:
    return {
        "schema_version": "oea.environment.v1",
        "scene_graph": {
            "nodes": [
                {
                    "id": "fridge_1",
                    "class": "fridge",
                    "center": {"x": 1.5, "y": 0.5, "z": 0.0},
                    "size": {"x": 0.8, "y": 0.8, "z": 1.8},
                    "frame": "map",
                }
            ],
            "edges": [],
        },
        "robots": {
            "go2_edu_001": {
                "robot_pose": {
                    "frame": "map",
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0,
                    "yaw": 0.0,
                    "stamp": "2026-03-18T00:00:00Z",
                },
                "nav_state": {
                    "mode": "idle",
                    "status": "idle",
                    "goal_id": None,
                    "target_ref": None,
                    "goal": None,
                    "path_progress": None,
                    "recovery_count": 0,
                    "last_error": None,
                    "relocalization_confidence": None,
                },
            },
            "desktop_pet_001": {
                "robot_pose": {
                    "frame": "desk",
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0,
                    "yaw": 0.0,
                    "stamp": "2026-03-18T00:00:00Z",
                },
                "nav_state": {"mode": "idle", "status": "idle"},
            },
        },
        "objects": {"apple": {"type": "fruit", "position": {"x": 0, "y": 0, "z": 0}}},
    }


def test_go2_driver_semantic_navigation_updates_runtime_state(tmp_path: Path) -> None:
    env_payload = _base_environment()
    env_file = tmp_path / "ENVIRONMENT.md"
    save_environment_doc(env_file, env_payload)
    action_file = _write_action(
        tmp_path,
        {
            "action_type": "semantic_navigate",
            "parameters": {
                "robot_id": "go2_edu_001",
                "target_ref": {"kind": "node", "id": "fridge_1", "label": "fridge"},
                "goal_pose": {"frame": "map", "x": 1.0, "y": 0.3, "yaw": 0.0},
                "approach_distance": 0.5,
                "timeout_s": 60,
            },
            "status": "pending",
        },
    )

    with load_driver("go2_edu", gui=False) as driver:
        driver.load_scene(env_payload["objects"])
        _poll_once(driver, action_file, env_file)

    updated = load_environment_doc(env_file)
    state = updated["robots"]["go2_edu_001"]["nav_state"]
    assert state["status"] == "arrived"
    assert state["last_error"] is None
    assert state["goal_id"] == "fridge_1"
    assert updated["scene_graph"]["nodes"][0]["id"] == "fridge_1"
    assert updated["robots"]["desktop_pet_001"]["nav_state"]["status"] == "idle"
    assert action_file.read_text(encoding="utf-8").strip() == ""


def test_go2_driver_semantic_navigation_blocked_sets_recoverable_state(tmp_path: Path) -> None:
    env_file = tmp_path / "ENVIRONMENT.md"
    save_environment_doc(env_file, _base_environment())
    action_file = _write_action(
        tmp_path,
        {
            "action_type": "semantic_navigate",
            "parameters": {
                "robot_id": "go2_edu_001",
                "target_ref": {"kind": "node", "id": "fridge_1", "label": "fridge"},
                "goal_pose": {"frame": "map", "x": 1.0, "y": 0.3, "yaw": 0.0},
                "approach_distance": 0.5,
                "timeout_s": 60,
                "mock_status": "blocked",
            },
            "status": "pending",
        },
    )

    with load_driver("go2_edu", gui=False) as driver:
        _poll_once(driver, action_file, env_file)

    updated = load_environment_doc(env_file)
    nav_state = updated["robots"]["go2_edu_001"]["nav_state"]
    assert nav_state["status"] == "blocked"
    assert nav_state["last_error"] == "recoverable_obstacle"
    assert nav_state["recovery_count"] == 1


def test_go2_driver_semantic_navigation_missing_goal_is_failed(tmp_path: Path) -> None:
    env_file = tmp_path / "ENVIRONMENT.md"
    save_environment_doc(env_file, _base_environment())
    action_file = _write_action(
        tmp_path,
        {
            "action_type": "semantic_navigate",
            "parameters": {
                "robot_id": "go2_edu_001",
                "target_ref": {"kind": "node", "id": "fridge_1", "label": "fridge"},
                "approach_distance": 0.5,
                "timeout_s": 60,
            },
            "status": "pending",
        },
    )

    with load_driver("go2_edu", gui=False) as driver:
        _poll_once(driver, action_file, env_file)

    updated = load_environment_doc(env_file)
    nav_state = updated["robots"]["go2_edu_001"]["nav_state"]
    assert nav_state["status"] == "failed"
    assert nav_state["last_error"] == "planner_timeout"


def test_go2_driver_localize_sets_relocalization_confidence(tmp_path: Path) -> None:
    env_file = tmp_path / "ENVIRONMENT.md"
    save_environment_doc(env_file, _base_environment())
    action_file = _write_action(
        tmp_path,
        {
            "action_type": "localize",
            "parameters": {"robot_id": "go2_edu_001", "mode": "spin_and_match", "timeout_s": 90},
            "status": "pending",
        },
    )

    with load_driver("go2_edu", gui=False) as driver:
        _poll_once(driver, action_file, env_file)

    updated = load_environment_doc(env_file)
    nav_state = updated["robots"]["go2_edu_001"]["nav_state"]
    assert nav_state["status"] == "localized"
    assert nav_state["relocalization_confidence"] > 0.0


def test_go2_driver_stop_sets_stopped_status(tmp_path: Path) -> None:
    env_file = tmp_path / "ENVIRONMENT.md"
    save_environment_doc(env_file, _base_environment())
    action_file = _write_action(
        tmp_path,
        {
            "action_type": "stop",
            "parameters": {"robot_id": "go2_edu_001"},
            "status": "pending",
        },
    )

    with load_driver("go2_edu", gui=False) as driver:
        _poll_once(driver, action_file, env_file)

    updated = load_environment_doc(env_file)
    nav_state = updated["robots"]["go2_edu_001"]["nav_state"]
    assert nav_state["status"] == "stopped"
    assert nav_state["mode"] == "idle"
