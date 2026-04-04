"""
tests/test_hal_simulation.py

Unit and integration tests for the HAL simulation layer.

Tests are organised in three groups:

1. scene_io  — pure I/O: load / save ENVIRONMENT.md
2. pybullet  — PyBullet simulator actions (headless DIRECT mode)
3. watchdog  — end-to-end poll loop: ACTION.md → execute → ENVIRONMENT.md

PyBullet tests are automatically skipped when the package is not installed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FENCE_OPEN = "```json"
_FENCE_CLOSE = "```"


def _make_env_md(tmp_path: Path, scene: dict) -> Path:
    """Write a well-formed ENVIRONMENT.md to *tmp_path* and return its path."""
    scene_json = json.dumps(scene, indent=2)
    content = (
        "# Environment Scene-Graph\n\n"
        f"{_FENCE_OPEN}\n{scene_json}\n{_FENCE_CLOSE}\n"
    )
    p = tmp_path / "ENVIRONMENT.md"
    p.write_text(content, encoding="utf-8")
    return p


def _make_action_md(tmp_path: Path, action: dict) -> Path:
    """Write a well-formed ACTION.md to *tmp_path* and return its path."""
    action_json = json.dumps(action, indent=2)
    content = f"{_FENCE_OPEN}\n{action_json}\n{_FENCE_CLOSE}\n"
    p = tmp_path / "ACTION.md"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Group 1: scene_io
# ---------------------------------------------------------------------------

# Add repo root to sys.path so we can import hal.*
sys.path.insert(0, str(Path(__file__).parent.parent))

from hal.simulation.scene_io import load_environment_doc, load_scene_from_md, save_scene_to_md


class TestSceneIO:
    def test_load_missing_file_returns_empty(self, tmp_path):
        p = tmp_path / "ENVIRONMENT.md"
        assert load_scene_from_md(p) == {}

    def test_load_empty_file_returns_empty(self, tmp_path):
        p = tmp_path / "ENVIRONMENT.md"
        p.write_text("", encoding="utf-8")
        assert load_scene_from_md(p) == {}

    def test_load_file_without_json_block_returns_empty(self, tmp_path):
        p = tmp_path / "ENVIRONMENT.md"
        p.write_text("# Some heading\nNo JSON here.", encoding="utf-8")
        assert load_scene_from_md(p) == {}

    def test_load_valid_scene(self, tmp_path):
        scene = {
            "apple": {"position": {"x": 5, "y": 5, "z": 0}, "location": "table"}
        }
        p = _make_env_md(tmp_path, scene)
        loaded = load_scene_from_md(p)
        assert loaded == scene

    def test_load_invalid_json_returns_empty(self, tmp_path):
        p = tmp_path / "ENVIRONMENT.md"
        p.write_text(f"{_FENCE_OPEN}\nnot valid json\n{_FENCE_CLOSE}\n",
                     encoding="utf-8")
        assert load_scene_from_md(p) == {}

    def test_roundtrip_save_then_load(self, tmp_path):
        scene = {
            "cup": {"position": {"x": -10, "y": 3, "z": 0}, "location": "table"},
            "book": {"position": {"x": 20, "y": 0, "z": 0}, "location": "table"},
        }
        p = tmp_path / "ENVIRONMENT.md"
        save_scene_to_md(p, scene)
        loaded = load_scene_from_md(p)
        assert loaded == scene

    def test_load_v1_structured_environment_returns_objects(self, tmp_path):
        p = tmp_path / "ENVIRONMENT.md"
        payload = {
            "schema_version": "PhyAgentOS.environment.v1",
            "scene_graph": {"nodes": [], "edges": []},
            "robots": {
                "go2_edu_001": {
                    "robot_pose": {"x": 1.0, "y": 2.0, "z": 0.0, "yaw": 0.0, "frame": "map"},
                    "nav_state": {"mode": "idle", "status": "idle"},
                }
            },
            "objects": {
                "apple": {"position": {"x": 5, "y": 5, "z": 0}, "location": "table"}
            },
        }
        p.write_text(
            "# Environment State\n\n"
            f"{_FENCE_OPEN}\n{json.dumps(payload, indent=2)}\n{_FENCE_CLOSE}\n",
            encoding="utf-8",
        )

        loaded = load_scene_from_md(p)
        assert "apple" in loaded
        assert loaded["apple"]["location"] == "table"

    def test_save_scene_writes_v1_envelope(self, tmp_path):
        p = tmp_path / "ENVIRONMENT.md"
        scene = {"apple": {"position": {"x": 0, "y": 0, "z": 0}, "location": "table"}}
        save_scene_to_md(p, scene)
        doc = load_environment_doc(p)
        assert doc.get("schema_version") == "PhyAgentOS.environment.v1"
        assert "objects" in doc
        assert "apple" in doc["objects"]

    def test_save_creates_human_readable_header(self, tmp_path):
        p = tmp_path / "ENVIRONMENT.md"
        save_scene_to_md(p, {})
        content = p.read_text(encoding="utf-8")
        assert "# Environment State" in content


# ---------------------------------------------------------------------------
# Group 2: PyBullet simulator (skipped if pybullet not installed)
# ---------------------------------------------------------------------------

def _is_pybullet_available() -> bool:
    try:
        import pybullet  # noqa: F401
        return True
    except ImportError:
        return False


pybullet_available = pytest.mark.skipif(
    not _is_pybullet_available(),
    reason="pybullet not installed",
)


@pybullet_available
class TestPyBulletSimulator:
    """All tests use headless DIRECT mode (gui=False)."""

    def test_init_and_close(self):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        with PyBulletSimulator(gui=False) as sim:
            assert sim is not None

    def test_load_empty_scene(self):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        with PyBulletSimulator(gui=False) as sim:
            sim.load_scene({})
            assert sim.get_scene() == {}

    def test_load_scene_with_objects(self):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        scene = {
            "apple": {"type": "fruit", "position": {"x": 5, "y": 5, "z": 0}},
            "cup":   {"type": "container", "position": {"x": -5, "y": 5, "z": 0}},
        }
        with PyBulletSimulator(gui=False) as sim:
            sim.load_scene(scene)
            result = sim.get_scene()
            assert "apple" in result
            assert "cup" in result

    def test_move_to_returns_success(self):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        with PyBulletSimulator(gui=False) as sim:
            msg = sim.execute_action("move_to", {"x": 10, "y": 0, "z": 0})
            assert "moved" in msg.lower()

    def test_pick_up_object(self):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        scene = {"apple": {"type": "fruit", "position": {"x": 5, "y": 5, "z": 0}}}
        with PyBulletSimulator(gui=False) as sim:
            sim.load_scene(scene)
            msg = sim.execute_action("pick_up", {"target": "apple"})
            assert "picked up" in msg.lower()
            # Scene should report the apple as 'held'
            result = sim.get_scene()
            assert result["apple"]["location"] == "held"

    def test_pick_up_nonexistent_returns_error(self):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        with PyBulletSimulator(gui=False) as sim:
            msg = sim.execute_action("pick_up", {"target": "ghost"})
            assert "failed" in msg.lower()

    def test_push_changes_location(self):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        scene = {"apple": {"type": "fruit", "position": {"x": 5, "y": 5, "z": 0}}}
        with PyBulletSimulator(gui=False) as sim:
            sim.load_scene(scene)
            msg = sim.execute_action("push", {"target": "apple", "direction": "forward"})
            assert "pushed" in msg.lower()

    def test_point_to_known_object(self):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        scene = {"apple": {"type": "fruit", "position": {"x": 5, "y": 5, "z": 0}}}
        with PyBulletSimulator(gui=False) as sim:
            sim.load_scene(scene)
            msg = sim.execute_action("point_to", {"target": "apple"})
            assert "pointed" in msg.lower()

    def test_nod_head(self):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        with PyBulletSimulator(gui=False) as sim:
            msg = sim.execute_action("nod_head", {})
            assert "nodded" in msg.lower()

    def test_shake_head(self):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        with PyBulletSimulator(gui=False) as sim:
            msg = sim.execute_action("shake_head", {})
            assert "shook" in msg.lower()

    def test_unknown_action_returns_error(self):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        with PyBulletSimulator(gui=False) as sim:
            msg = sim.execute_action("fly_to_moon", {})
            assert "unknown" in msg.lower()

    def test_reload_scene_removes_old_objects(self):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        scene1 = {"apple": {"type": "fruit", "position": {"x": 5, "y": 5, "z": 0}}}
        scene2 = {"cup": {"type": "container", "position": {"x": -5, "y": 5, "z": 0}}}
        with PyBulletSimulator(gui=False) as sim:
            sim.load_scene(scene1)
            sim.load_scene(scene2)
            result = sim.get_scene()
            assert "cup" in result
            assert "apple" not in result


# ---------------------------------------------------------------------------
# Group 3: End-to-end watchdog poll (skipped if pybullet not installed)
# ---------------------------------------------------------------------------

@pybullet_available
class TestWatchdogPollLoop:
    """Drives _poll_once directly without spawning a process."""

    def test_poll_noop_when_action_empty(self, tmp_path):
        """Nothing should happen if ACTION.md is empty."""
        from hal.simulation.pybullet_sim import PyBulletSimulator
        from hal.hal_watchdog import _poll_once

        action_file = tmp_path / "ACTION.md"
        action_file.write_text("", encoding="utf-8")
        env_file = _make_env_md(tmp_path, {})

        with PyBulletSimulator(gui=False) as sim:
            _poll_once(sim, action_file, env_file)

        # ENVIRONMENT.md should still only contain the header (no change)
        assert load_scene_from_md(env_file) == {}

    def test_poll_marks_action_completed_after_execution(self, tmp_path):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        from hal.hal_watchdog import _poll_once

        scene = {"apple": {"type": "fruit", "position": {"x": 5, "y": 5, "z": 0}}}
        env_file = _make_env_md(tmp_path, scene)
        action_file = _make_action_md(tmp_path, {
            "action_type": "point_to",
            "parameters": {"target": "apple"},
            "status": "pending",
        })

        with PyBulletSimulator(gui=False) as sim:
            sim.load_scene(scene)
            _poll_once(sim, action_file, env_file)

        action_doc = json.loads(action_file.read_text(encoding="utf-8").split(_FENCE_OPEN, 1)[1].split(_FENCE_CLOSE, 1)[0])
        assert action_doc["actions"][0]["status"] == "completed"

    def test_poll_updates_environment_after_pick_up(self, tmp_path):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        from hal.hal_watchdog import _poll_once

        scene = {"apple": {"type": "fruit", "position": {"x": 5, "y": 5, "z": 0}}}
        env_file = _make_env_md(tmp_path, scene)
        action_file = _make_action_md(tmp_path, {
            "action_type": "pick_up",
            "parameters": {"target": "apple"},
            "status": "pending",
        })

        with PyBulletSimulator(gui=False) as sim:
            sim.load_scene(scene)
            _poll_once(sim, action_file, env_file)

        updated = load_scene_from_md(env_file)
        assert updated["apple"]["location"] == "held"

    def test_poll_preserves_existing_robots_partition(self, tmp_path):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        from hal.hal_watchdog import _poll_once

        env_file = tmp_path / "ENVIRONMENT.md"
        initial = {
            "schema_version": "PhyAgentOS.environment.v1",
            "scene_graph": {"nodes": [], "edges": []},
            "robots": {
                "go2_edu_001": {
                    "robot_pose": {"frame": "map", "x": 1.0, "y": 2.0, "z": 0.0, "yaw": 0.0},
                    "nav_state": {"mode": "navigating", "status": "running"},
                }
            },
            "objects": {
                "apple": {"type": "fruit", "position": {"x": 5, "y": 5, "z": 0}}
            },
        }
        env_file.write_text(
            "# Environment State\n\n"
            f"{_FENCE_OPEN}\n{json.dumps(initial, indent=2)}\n{_FENCE_CLOSE}\n",
            encoding="utf-8",
        )

        action_file = _make_action_md(tmp_path, {
            "action_type": "point_to",
            "parameters": {"target": "apple"},
            "status": "pending",
        })

        with PyBulletSimulator(gui=False) as sim:
            sim.load_scene(initial["objects"])
            _poll_once(sim, action_file, env_file)

        doc = load_environment_doc(env_file)
        assert "robots" in doc
        assert "go2_edu_001" in doc["robots"]
        assert doc["robots"]["go2_edu_001"]["nav_state"]["status"] == "running"

    def test_poll_skips_invalid_json_block(self, tmp_path):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        from hal.hal_watchdog import _poll_once

        env_file = _make_env_md(tmp_path, {})
        action_file = tmp_path / "ACTION.md"
        action_file.write_text("some text without a json block", encoding="utf-8")

        before_mtime = env_file.stat().st_mtime

        with PyBulletSimulator(gui=False) as sim:
            _poll_once(sim, action_file, env_file)

        # ENVIRONMENT.md should be untouched
        assert env_file.stat().st_mtime == before_mtime

    def test_poll_skips_non_pending_queue_items(self, tmp_path):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        from hal.hal_watchdog import _poll_once

        scene = {"apple": {"type": "fruit", "position": {"x": 5, "y": 5, "z": 0}}}
        env_file = _make_env_md(tmp_path, scene)
        action_file = _make_action_md(tmp_path, {
            "schema_version": "PhyAgentOS.action_queue.v1",
            "actions": [
                {
                    "id": "done1",
                    "action_type": "pick_up",
                    "parameters": {"target": "apple"},
                    "status": "completed",
                }
            ],
        })

        with PyBulletSimulator(gui=False) as sim:
            sim.load_scene(scene)
            _poll_once(sim, action_file, env_file)

        updated = load_scene_from_md(env_file)
        assert updated["apple"]["position"]["x"] == 5
        assert "completed" in action_file.read_text(encoding="utf-8")

    def test_poll_executes_first_pending_queue_item_only(self, tmp_path):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        from hal.hal_watchdog import _poll_once

        scene = {"apple": {"type": "fruit", "position": {"x": 5, "y": 5, "z": 0}}}
        env_file = _make_env_md(tmp_path, scene)
        action_file = _make_action_md(tmp_path, {
            "schema_version": "PhyAgentOS.action_queue.v1",
            "actions": [
                {
                    "id": "act1",
                    "action_type": "pick_up",
                    "parameters": {"target": "apple"},
                    "status": "pending",
                },
                {
                    "id": "act2",
                    "action_type": "point_to",
                    "parameters": {"target": "apple"},
                    "status": "pending",
                },
            ],
        })

        with PyBulletSimulator(gui=False) as sim:
            sim.load_scene(scene)
            _poll_once(sim, action_file, env_file)

        action_doc = json.loads(action_file.read_text(encoding="utf-8").split(_FENCE_OPEN, 1)[1].split(_FENCE_CLOSE, 1)[0])
        assert action_doc["actions"][0]["status"] == "completed"
        assert action_doc["actions"][1]["status"] == "pending"

    def test_poll_treats_missing_status_as_pending_for_compatibility(self, tmp_path):
        from hal.simulation.pybullet_sim import PyBulletSimulator
        from hal.hal_watchdog import _poll_once

        scene = {"apple": {"type": "fruit", "position": {"x": 5, "y": 5, "z": 0}}}
        env_file = _make_env_md(tmp_path, scene)
        action_file = _make_action_md(tmp_path, {
            "action_type": "pick_up",
            "parameters": {"target": "apple"},
        })

        with PyBulletSimulator(gui=False) as sim:
            sim.load_scene(scene)
            _poll_once(sim, action_file, env_file)

        updated = load_scene_from_md(env_file)
        assert updated["apple"]["location"] == "held"

    def test_parse_action_valid(self):
        from hal.hal_watchdog import parse_action

        raw = f"{_FENCE_OPEN}\n" + '{"action_type": "nod_head", "parameters": {}}' + f"\n{_FENCE_CLOSE}\n"
        result = parse_action(raw)
        assert result is not None
        assert result["action_type"] == "nod_head"

    def test_parse_action_no_block_returns_none(self):
        from hal.hal_watchdog import parse_action

        assert parse_action("no json here") is None

    def test_parse_action_invalid_json_returns_none(self):
        from hal.hal_watchdog import parse_action

        raw = f"{_FENCE_OPEN}\nnot-json\n{_FENCE_CLOSE}\n"
        assert parse_action(raw) is None
