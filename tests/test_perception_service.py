from __future__ import annotations

from pathlib import Path

from hal.perception.service import PerceptionService
from hal.simulation.scene_io import load_environment_doc, save_environment_doc


def _seed_environment(path: Path) -> None:
    save_environment_doc(
        path,
        {
            "schema_version": "oea.environment.v1",
            "scene_graph": {"nodes": [], "edges": []},
            "robots": {
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
                }
            },
            "objects": {
                "apple": {"type": "fruit", "position": {"x": 1, "y": 2, "z": 0}, "location": "table"}
            },
        },
    )


def test_perception_service_tick_writes_scene_graph_map_tf_and_robot_state(tmp_path: Path) -> None:
    env_file = tmp_path / "ENVIRONMENT.md"
    _seed_environment(env_file)
    service = PerceptionService(tmp_path)

    updated = service.tick(
        robot_id="go2_edu_001",
        image={
            "detections": [
                {
                    "id": "fridge_1",
                    "label": "fridge",
                    "confidence": 0.96,
                    "object_key": "fridge_main",
                    "center": {"x": 2.0, "y": 1.0, "z": 0.0},
                    "size": {"x": 0.8, "y": 0.8, "z": 1.8},
                    "track_id": "track_fridge_1",
                    "relations": [{"relation": "IN", "target": "kitchen", "confidence": 0.9}],
                },
                {
                    "id": "cup_1",
                    "label": "cup",
                    "confidence": 0.88,
                    "center": {"x": 2.2, "y": 1.1, "z": 0.8},
                    "size": {"x": 0.1, "y": 0.1, "z": 0.2},
                    "track_id": "track_cup_1",
                },
            ]
        },
        pointcloud={
            "map": {"resolution": 0.03, "image_path": "maps/mock_map.pgm"},
            "zones": [{"name": "kitchen", "center": {"x": 2.0, "y": 1.0, "z": 0.0}}],
            "tf": {"camera_link_to_map": {"available": True}},
        },
        odom={"frame": "map", "x": 1.1, "y": 0.2, "z": 0.0, "yaw": 0.4, "stamp": "2026-03-18T10:00:00Z"},
        nav_state={"mode": "navigating", "status": "running", "recovery_count": 0},
    )

    assert updated["robots"]["go2_edu_001"]["robot_pose"]["x"] == 1.1
    assert updated["robots"]["go2_edu_001"]["nav_state"]["status"] == "running"
    assert updated["map"]["resolution"] == 0.03
    assert updated["tf"]["camera_link_to_map"]["available"] is True
    assert len(updated["scene_graph"]["nodes"]) == 2
    assert any(edge["relation"] == "IN" for edge in updated["scene_graph"]["edges"])
    assert any(edge["relation"] == "CLOSE_TO" for edge in updated["scene_graph"]["edges"])

    doc = load_environment_doc(env_file)
    assert doc["objects"]["apple"]["location"] == "table"
    assert doc["robots"]["desktop_pet_001"]["nav_state"]["status"] == "idle"


def test_perception_service_tick_with_no_image_keeps_empty_scene_graph(tmp_path: Path) -> None:
    env_file = tmp_path / "ENVIRONMENT.md"
    _seed_environment(env_file)
    service = PerceptionService(tmp_path)

    updated = service.tick(
        robot_id="go2_edu_001",
        image=None,
        pointcloud={},
        odom={"frame": "map", "x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0, "stamp": "2026-03-18T10:00:00Z"},
    )

    assert updated["scene_graph"]["nodes"] == []
    assert updated["scene_graph"]["edges"] == []
