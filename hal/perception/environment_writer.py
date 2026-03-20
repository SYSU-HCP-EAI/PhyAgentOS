"""Environment writer for side-loaded perception updates."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from hal.simulation.scene_io import load_environment_doc, merge_environment_doc, save_environment_doc


class EnvironmentWriter:
    """Writes structured perception outputs into ENVIRONMENT.md."""

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def write(
        self,
        *,
        robot_id: str,
        robot_pose: dict[str, Any] | None = None,
        nav_state: dict[str, Any] | None = None,
        scene_graph: dict[str, Any] | None = None,
        map_data: dict[str, Any] | None = None,
        tf_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        env_path = self.workspace / "ENVIRONMENT.md"
        existing = load_environment_doc(env_path)
        robots = dict(existing.get("robots", {}))
        robot_entry = dict(robots.get(robot_id, {}))
        if robot_pose is not None:
            robot_entry["robot_pose"] = robot_pose
        if nav_state is not None:
            robot_entry["nav_state"] = nav_state
        if robot_entry:
            robots[robot_id] = robot_entry

        merged = merge_environment_doc(
            existing,
            robots=robots,
            scene_graph=scene_graph,
            map_data=map_data,
            tf_data=tf_data,
            updated_at=datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        )
        save_environment_doc(env_path, merged)
        return merged
