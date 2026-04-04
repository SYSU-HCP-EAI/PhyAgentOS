from __future__ import annotations

import asyncio
import json
from pathlib import Path

import numpy as np
import pytest

from PhyAgentOS.agent.tools.embodied import EmbodiedActionTool
from PhyAgentOS.agent.tools.target_navigation import TargetNavigationTool
from hal.hal_watchdog import _poll_once
from hal.drivers import load_driver
from hal.drivers.go2_navigation_bridge import Go2BridgeConfig, VideoStateOccupancyReceiver
import hal.navigation.target_navigation_backend as target_navigation_backend_module
from hal.navigation import NavigationEngine, TargetNavigationBackend
from hal.navigation.bridge import SimulatedRobotBridge
from hal.simulation.scene_io import load_environment_doc, save_environment_doc

_FENCE_OPEN = "```json"
_FENCE_CLOSE = "```"


class _FakeResponse:
    def __init__(self, content: str):
        self.content = content


class _FakeProvider:
    def __init__(self):
        self.messages = []

    async def chat_with_retry(self, messages, model):  # noqa: ANN001
        self.messages.append({"messages": messages, "model": model})
        return _FakeResponse("VALID")


def _write_workspace_files(workspace: Path) -> None:
    (workspace / "EMBODIED.md").write_text(
        "# Embodied\n\n- Supports target navigation.\n",
        encoding="utf-8",
    )
    (workspace / "LESSONS.md").write_text("# Lessons\n", encoding="utf-8")
    save_environment_doc(
        workspace / "ENVIRONMENT.md",
        {
            "schema_version": "oea.environment.v1",
            "scene_graph": {"nodes": [], "edges": []},
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
                        "recovery_count": 0,
                    },
                }
            },
            "objects": {},
        },
    )


def _write_action(path: Path, payload: dict) -> Path:
    action_file = path / "ACTION.md"
    action_file.write_text(
        f"{_FENCE_OPEN}\n{json.dumps(payload, indent=2)}\n{_FENCE_CLOSE}\n",
        encoding="utf-8",
    )
    return action_file


def _enable_mock_depth_success(bridge) -> None:  # noqa: ANN001
    original_get_observation = bridge.get_observation

    def _with_depth():
        obs = original_get_observation()
        depth = np.full(obs.rgb.shape[:2], np.nan, dtype=np.float32)
        red_mask = obs.rgb[:, :, 0] > 0
        depth[red_mask] = 0.6
        return obs.__class__(
            rgb=obs.rgb,
            depth_m=depth,
            occupancy=obs.occupancy,
            pose_xy_yaw=obs.pose_xy_yaw,
            timestamp=obs.timestamp,
        )

    bridge.get_observation = _with_depth


def test_target_navigation_writes_action_md(tmp_path: Path) -> None:
    _write_workspace_files(tmp_path)
    provider = _FakeProvider()
    action_tool = EmbodiedActionTool(workspace=tmp_path, provider=provider, model="fake")
    tool = TargetNavigationTool(workspace=tmp_path, action_tool=action_tool)

    result = asyncio.run(
        tool.execute(
            robot_id="go2_edu_001",
            target_label="cup",
            detection_hint={"rgb_range": [[180, 0, 0], [255, 60, 60]]},
            reasoning="Need to approach the cup directly.",
        )
    )

    assert "validated and dispatched" in result
    action_doc = json.loads((tmp_path / "ACTION.md").read_text(encoding="utf-8").split(_FENCE_OPEN, 1)[1].split(_FENCE_CLOSE, 1)[0])
    assert action_doc["schema_version"] == "PhyAgentOS.action_queue.v1"
    assert action_doc["actions"][0]["action_type"] == "target_navigation"
    assert action_doc["actions"][0]["parameters"]["target_label"] == "cup"
    prompt = provider.messages[-1]["messages"][0]["content"]
    assert "do not require the target to already exist in the scene graph" in prompt


def test_target_navigation_reports_missing_target_label(tmp_path: Path) -> None:
    _write_workspace_files(tmp_path)
    action_tool = EmbodiedActionTool(workspace=tmp_path, provider=_FakeProvider(), model="fake")
    tool = TargetNavigationTool(workspace=tmp_path, action_tool=action_tool)

    result = asyncio.run(
        tool.execute(
            robot_id="go2_edu_001",
            target_label="   ",
            reasoning="Need to approach the missing target.",
        )
    )

    assert "target_label is required" in result


def test_go2_driver_target_navigation_updates_runtime_state(tmp_path: Path) -> None:
    _write_workspace_files(tmp_path)
    env_file = tmp_path / "ENVIRONMENT.md"
    action_file = _write_action(
        tmp_path,
        {
            "action_type": "target_navigation",
                "parameters": {
                    "robot_id": "go2_edu_001",
                    "target_label": "cup",
                    "detection_hint": {"rgb_range": [[180, 0, 0], [255, 60, 60]]},
                    "success_distance_m": 3.5,
                    "timeout_s": 2,
                },
                "status": "pending",
        },
    )

    with load_driver("go2_edu", gui=False, target_navigation_backend="mock") as driver:
        driver.connect()
        driver._target_navigation_backend._bridge.obstacle_cells = set()
        _enable_mock_depth_success(driver._target_navigation_backend._bridge)
        _poll_once(driver, action_file, env_file)

    updated = load_environment_doc(env_file)
    nav_state = updated["robots"]["go2_edu_001"]["nav_state"]
    assert nav_state["status"] == "arrived"
    assert nav_state["target_label"] == "cup"
    assert updated["robots"]["go2_edu_001"]["robot_pose"]["x"] >= 0.0


def test_go2_driver_target_navigation_not_found_maps_to_failed(tmp_path: Path) -> None:
    _write_workspace_files(tmp_path)
    env_file = tmp_path / "ENVIRONMENT.md"
    action_file = _write_action(
        tmp_path,
        {
            "action_type": "target_navigation",
            "parameters": {
                "robot_id": "go2_edu_001",
                "target_label": "cup",
                "timeout_s": 1,
            },
            "status": "pending",
        },
    )

    with load_driver("go2_edu", gui=False, target_navigation_backend="mock") as driver:
        _poll_once(driver, action_file, env_file)

    updated = load_environment_doc(env_file)
    nav_state = updated["robots"]["go2_edu_001"]["nav_state"]
    assert nav_state["status"] == "failed"
    assert nav_state["last_error"] == "target_not_found"


def test_go2_driver_stop_cancels_target_navigation_backend() -> None:
    with load_driver("go2_edu", gui=False, target_navigation_backend="mock") as driver:
        driver.connect()
        result = driver.execute_action("stop", {"robot_id": "go2_edu_001"})

    assert result == "Navigation stopped."


def test_watchdog_target_navigation_preserves_environment_shape(tmp_path: Path) -> None:
    _write_workspace_files(tmp_path)
    env_file = tmp_path / "ENVIRONMENT.md"
    action_file = _write_action(
        tmp_path,
        {
            "action_type": "target_navigation",
                "parameters": {
                    "robot_id": "go2_edu_001",
                    "target_label": "cup",
                    "detection_hint": {"rgb_range": [[180, 0, 0], [255, 60, 60]]},
                    "success_distance_m": 3.5,
                    "timeout_s": 2,
                },
                "status": "pending",
        },
    )

    with load_driver("go2_edu", gui=False, target_navigation_backend="mock") as driver:
        driver.connect()
        driver._target_navigation_backend._bridge.obstacle_cells = set()
        _enable_mock_depth_success(driver._target_navigation_backend._bridge)
        _poll_once(driver, action_file, env_file)

    updated = load_environment_doc(env_file)
    assert "scene_graph" in updated
    assert "objects" in updated
    assert updated["robots"]["go2_edu_001"]["nav_state"]["status"] in {"arrived", "blocked"}


def test_go2_driver_uses_configured_robot_id(tmp_path: Path) -> None:
    _write_workspace_files(tmp_path)
    custom_robot_id = "go2_lab_b"
    env = load_environment_doc(tmp_path / "ENVIRONMENT.md")
    env["robots"][custom_robot_id] = env["robots"].pop("go2_edu_001")
    save_environment_doc(tmp_path / "ENVIRONMENT.md", env)

    action_file = _write_action(
        tmp_path,
        {
            "action_type": "target_navigation",
            "parameters": {
                "robot_id": custom_robot_id,
                "target_label": "cup",
                "detection_hint": {"rgb_range": [[180, 0, 0], [255, 60, 60]]},
                "success_distance_m": 3.5,
                "timeout_s": 2,
            },
            "status": "pending",
        },
    )

    with load_driver("go2_edu", gui=False, target_navigation_backend="mock", robot_id=custom_robot_id) as driver:
        driver.connect()
        driver._target_navigation_backend._bridge.obstacle_cells = set()
        _enable_mock_depth_success(driver._target_navigation_backend._bridge)
        _poll_once(driver, action_file, tmp_path / "ENVIRONMENT.md")

    updated = load_environment_doc(tmp_path / "ENVIRONMENT.md")
    assert custom_robot_id in updated["robots"]
    assert updated["robots"][custom_robot_id]["nav_state"]["target_label"] == "cup"


def test_navigation_engine_max_steps_stops_active_horizon() -> None:
    bridge = SimulatedRobotBridge()
    stop_calls = []
    original_stop = bridge.stop

    def _recording_stop():
        stop_calls.append(True)
        return original_stop()

    bridge.stop = _recording_stop
    engine = NavigationEngine(bridge)
    engine.set_target("cup", detection_hint={"rgb_range": [[180, 0, 0], [255, 60, 60]]})
    engine.config.max_steps = 0

    result = engine.run_until_done(timeout_s=0.2, step_delay_s=0.0)

    assert result["phase"] == "blocked"
    assert result["active_horizon_target"] is None
    assert any(item["event"] == "max_steps_blocked" for item in result["history_tail"])
    assert stop_calls


def test_navigation_engine_resets_overrides_between_targets() -> None:
    bridge = SimulatedRobotBridge()
    engine = NavigationEngine(bridge)

    engine.set_target("cup", success_distance_m=2.5, control_mode="blocking")
    assert engine.config.success_distance_m == 2.5
    assert engine.config.control_mode == "blocking"

    engine.set_target("cup")

    assert engine.config.success_distance_m == pytest.approx(0.8)
    assert engine.config.control_mode == "preemptive"


def test_target_navigation_backend_real_connect_requires_ready(monkeypatch) -> None:
    class _FakeBridge:
        def __init__(self):
            self.stopped = False
            self.motion_server = None
            self.receiver = None

        def wait_until_ready(self):
            return {"ok": False, "reason": "bridge_not_ready"}

        def stop_remote_services(self):
            self.stopped = True
            return {"ok": True}

    fake_bridge = _FakeBridge()
    monkeypatch.setattr(target_navigation_backend_module, "Go2MoveBridge", lambda cfg: fake_bridge)

    backend = TargetNavigationBackend(backend_mode="real")
    connected = backend.connect()

    assert connected is False
    assert fake_bridge.stopped is True
    assert backend._bridge is None


def test_target_navigation_backend_run_navigation_returns_not_ready_status(monkeypatch) -> None:
    backend = TargetNavigationBackend(backend_mode="mock")

    def _fake_connect():
        backend._last_status = {"phase": "blocked", "message": "bridge_not_ready"}
        return False

    monkeypatch.setattr(backend, "connect", _fake_connect)

    result = backend.run_navigation({"target_label": "cup"})

    assert result["phase"] == "blocked"
    assert result["message"] == "bridge_not_ready"


def test_video_receiver_ignores_malformed_payloads() -> None:
    receiver = VideoStateOccupancyReceiver(Go2BridgeConfig())

    receiver._handle_state_payload(b"bad")
    receiver._handle_occupancy_payload(b"\x00\x00\x00\x01\x00\x00\x00\x02\x01")

    latest = receiver.get_latest()
    assert latest.timestamp == 0.0
