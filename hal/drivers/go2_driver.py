"""Mock-friendly Go2 navigation driver."""

from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path
from typing import Any

from hal.base_driver import BaseDriver
from hal.ros2 import ROS2Bridge

_PROFILES_DIR = Path(__file__).resolve().parent.parent / "profiles"


class Go2Driver(BaseDriver):
    """Navigation-oriented driver with a dependency-free mock runtime."""

    ROBOT_ID = "go2_edu_001"

    def __init__(self, gui: bool = False, bridge: ROS2Bridge | None = None, **_kwargs: Any):
        self._gui = gui
        self._bridge = bridge or ROS2Bridge(enabled=False)
        self._objects: dict[str, dict] = {}
        self._runtime_state = {"robots": {self.ROBOT_ID: self._make_robot_state()}}

    def get_profile_path(self) -> Path:
        return _PROFILES_DIR / "go2_edu.md"

    def load_scene(self, scene: dict[str, dict]) -> None:
        self._objects = dict(scene)

    def execute_action(self, action_type: str, params: dict) -> str:
        if action_type == "semantic_navigate":
            return self._semantic_navigate(params)
        if action_type == "localize":
            return self._localize(params)
        if action_type == "stop":
            robot_id = params.get("robot_id", self.ROBOT_ID)
            self._update_nav_state(
                robot_id,
                mode="idle",
                status="stopped",
                last_error=None,
            )
            return "Navigation stopped."
        return f"Unknown action: {action_type}"

    def get_scene(self) -> dict[str, dict]:
        return dict(self._objects)

    def get_runtime_state(self) -> dict[str, Any]:
        return self._runtime_state

    def _semantic_navigate(self, params: dict[str, Any]) -> str:
        robot_id = params.get("robot_id", self.ROBOT_ID)
        goal_pose = params.get("goal_pose") or {}
        target_ref = params.get("target_ref") or {}
        mock_status = params.get("mock_status")

        if not target_ref:
            self._update_nav_state(
                robot_id,
                mode="navigating",
                status="failed",
                target_ref={},
                goal=None,
                path_progress=0.0,
                last_error="target_not_found",
            )
            return "Navigation failed: target reference missing."

        if "x" not in goal_pose or "y" not in goal_pose:
            self._update_nav_state(
                robot_id,
                mode="navigating",
                status="failed",
                target_ref=target_ref,
                goal=None,
                path_progress=0.0,
                last_error="planner_timeout",
            )
            return "Navigation failed: goal pose missing."

        if mock_status == "blocked":
            self._update_nav_state(
                robot_id,
                mode="navigating",
                status="blocked",
                target_ref=target_ref,
                goal={
                    "x": float(goal_pose["x"]),
                    "y": float(goal_pose["y"]),
                    "yaw": float(goal_pose.get("yaw", 0.0)),
                },
                path_progress=0.5,
                last_error="recoverable_obstacle",
                recovery_count=1,
            )
            return f"Navigation blocked near {target_ref.get('label', 'target')}."

        state = self._robot_state(robot_id)
        dx = float(goal_pose["x"]) - float(state["robot_pose"]["x"])
        dy = float(goal_pose["y"]) - float(state["robot_pose"]["y"])
        yaw = float(goal_pose.get("yaw", math.atan2(dy, dx) if dx or dy else 0.0))
        state["robot_pose"] = {
            "frame": goal_pose.get("frame", "map"),
            "x": float(goal_pose["x"]),
            "y": float(goal_pose["y"]),
            "z": float(goal_pose.get("z", 0.0)),
            "yaw": yaw,
            "stamp": self._stamp(),
        }
        self._update_nav_state(
            robot_id,
            mode="navigating",
            status="arrived",
            target_ref=target_ref,
            goal={
                "x": float(goal_pose["x"]),
                "y": float(goal_pose["y"]),
                "yaw": yaw,
            },
            path_progress=1.0,
            last_error=None,
        )
        self._bridge.publish("/navigate_to_pose", goal_pose)
        return f"Navigation success: arrived near {target_ref.get('label', 'target')}."

    def _localize(self, params: dict[str, Any]) -> str:
        robot_id = params.get("robot_id", self.ROBOT_ID)
        state = self._robot_state(robot_id)
        state["robot_pose"]["stamp"] = self._stamp()
        self._update_nav_state(
            robot_id,
            mode="localizing",
            status="localized",
            last_error=None,
            relocalization_confidence=0.82,
        )
        return f"Localization success for {robot_id}."

    def _update_nav_state(
        self,
        robot_id: str,
        *,
        mode: str,
        status: str,
        target_ref: dict[str, Any] | None = None,
        goal: dict[str, Any] | None = None,
        path_progress: float | None = None,
        last_error: str | None = None,
        recovery_count: int | None = None,
        relocalization_confidence: float | None = None,
    ) -> None:
        state = self._robot_state(robot_id)
        current = dict(state.get("nav_state", {}))
        state["nav_state"] = {
            "mode": mode,
            "status": status,
            "goal_id": (target_ref or {}).get("id"),
            "target_ref": target_ref,
            "goal": goal,
            "path_progress": path_progress,
            "recovery_count": current.get("recovery_count", 0) if recovery_count is None else recovery_count,
            "last_error": last_error,
            "relocalization_confidence": relocalization_confidence,
        }

    def _robot_state(self, robot_id: str | None) -> dict[str, Any]:
        robot_id = robot_id or self.ROBOT_ID
        robots = self._runtime_state.setdefault("robots", {})
        if robot_id not in robots:
            robots[robot_id] = self._make_robot_state()
        return robots[robot_id]

    def _make_robot_state(self) -> dict[str, Any]:
        return {
            "robot_pose": {
                "frame": "map",
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "yaw": 0.0,
                "stamp": self._stamp(),
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
        }

    @staticmethod
    def _stamp() -> str:
        return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
