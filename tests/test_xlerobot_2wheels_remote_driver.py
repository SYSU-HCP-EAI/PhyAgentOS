from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure repo root is on sys.path for direct test execution.
sys.path.insert(0, str(Path(__file__).parent.parent))

import hal.drivers.xlerobot_2wheels_remote_driver as remote_module
from hal.drivers.xlerobot_2wheels_remote_driver import XLerobot2WheelsRemoteDriver


class FakeClient:
    def __init__(
        self,
        *,
        fail_connect: bool = False,
        fail_observation: bool = False,
        fail_send: bool = False,
        fail_disconnect: bool = False,
    ) -> None:
        self.fail_connect = fail_connect
        self.fail_observation = fail_observation
        self.fail_send = fail_send
        self.fail_disconnect = fail_disconnect
        self.is_connected = False
        self.actions: list[dict[str, float]] = []
        self.observation_calls = 0

    def connect(self) -> None:
        if self.fail_connect:
            raise RuntimeError("connect failed")
        self.is_connected = True

    def get_observation(self) -> dict[str, object]:
        if self.fail_observation:
            raise RuntimeError("observation failed")
        self.observation_calls += 1
        return {"ok": True}

    def send_action(self, action: dict[str, float]) -> None:
        if self.fail_send:
            raise RuntimeError("send failed")
        self.actions.append(dict(action))

    def disconnect(self) -> None:
        if self.fail_disconnect:
            raise RuntimeError("disconnect failed")
        self.is_connected = False


def _driver_with_fake_client(monkeypatch, client: FakeClient | None = None) -> tuple[XLerobot2WheelsRemoteDriver, FakeClient]:
    client = client or FakeClient()
    driver = XLerobot2WheelsRemoteDriver(
        remote_ip="127.0.0.1",
        robot_id="xlerobot_2wheels_001",
        loop_hz=10.0,
        max_move_duration_s=5.0,
        safe_max_linear_m_s=0.4,
        safe_max_angular_deg_s=120.0,
    )
    monkeypatch.setattr(driver, "_build_client", lambda: client)
    return driver, client


def _write_action_md(path: Path, payload: dict) -> Path:
    action_file = path / "ACTION.md"
    action_file.write_text(
        "```json\n" + json.dumps(payload, indent=2) + "\n```\n",
        encoding="utf-8",
    )
    return action_file


def test_connect_check_disconnect_lifecycle(monkeypatch) -> None:
    driver, client = _driver_with_fake_client(monkeypatch)

    assert driver.execute_action("connect_robot", {}) == "Robot connection established."
    assert client.is_connected is True
    assert driver.execute_action("check_connection", {}) == "connected"
    assert client.observation_calls >= 2

    state = driver.get_runtime_state()["robots"][driver.robot_id]
    assert state["connection_state"]["status"] == "connected"
    assert state["connection_state"]["last_heartbeat"] is not None

    assert driver.execute_action("disconnect_robot", {}) == "Robot connection closed."
    assert client.is_connected is False
    assert client.actions[-1] == {"x.vel": 0.0, "theta.vel": 0.0}
    assert driver.get_runtime_state()["robots"][driver.robot_id]["connection_state"]["status"] == "disconnected"


def test_check_connection_auto_reconnect_when_disconnected(monkeypatch) -> None:
    driver, client = _driver_with_fake_client(monkeypatch)
    assert client.is_connected is False

    assert driver.execute_action("check_connection", {}) == "connected"
    assert client.is_connected is True


def test_connect_robot_missing_ip_returns_diagnostic_error() -> None:
    driver = XLerobot2WheelsRemoteDriver(remote_ip="")
    result = driver.execute_action("connect_robot", {})
    assert "Connection error" in result
    assert "missing OEA_XLEROBOT_REMOTE_IP" in result


def test_connect_robot_client_failure_returns_diagnostic_error(monkeypatch) -> None:
    driver, _client = _driver_with_fake_client(monkeypatch, FakeClient(fail_connect=True))
    result = driver.execute_action("connect_robot", {})
    assert "Connection error" in result
    assert "connect failed" in result


def test_move_base_repeats_by_loop_rate_and_auto_stops(monkeypatch) -> None:
    driver, client = _driver_with_fake_client(monkeypatch)
    assert driver.execute_action("connect_robot", {}) == "Robot connection established."
    client.actions.clear()

    ticks = iter([10.0, 10.0, 10.1, 10.2, 10.3])
    monkeypatch.setattr(remote_module.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(remote_module.time, "sleep", lambda _seconds: None)

    result = driver.execute_action(
        "move_base",
        {"x_vel_m_s": 0.9, "theta_deg_s": 180.0, "duration_s": 0.3},
    )
    assert "Base moved for 0.30s" in result

    assert len(client.actions) == 4
    for action in client.actions[:-1]:
        assert action == {"x.vel": 0.4, "theta.vel": 120.0}
    assert client.actions[-1] == {"x.vel": 0.0, "theta.vel": 0.0}

    nav_state = driver.get_runtime_state()["robots"][driver.robot_id]["nav_state"]
    assert nav_state["mode"] == "idle"
    assert nav_state["status"] == "stopped"


def test_move_base_invalid_parameter_triggers_safe_stop(monkeypatch) -> None:
    driver, client = _driver_with_fake_client(monkeypatch)
    assert driver.execute_action("connect_robot", {}) == "Robot connection established."
    client.actions.clear()

    result = driver.execute_action(
        "move_base",
        {"x_vel_m_s": "fast", "theta_deg_s": 20.0, "duration_s": 0.5},
    )
    assert "invalid move_base parameters" in result
    assert client.actions[-1] == {"x.vel": 0.0, "theta.vel": 0.0}


def test_set_joint_targets_and_set_gripper_mapping(monkeypatch) -> None:
    driver, client = _driver_with_fake_client(monkeypatch)
    assert driver.execute_action("connect_robot", {}) == "Robot connection established."
    client.actions.clear()

    result = driver.execute_action(
        "set_joint_targets",
        {"joints": {"left_arm_shoulder_pan.pos": 0.5, "head_pan.pos": "-0.2"}},
    )
    assert result == "Applied 2 joint target(s)."
    assert client.actions[-1] == {"left_arm_shoulder_pan.pos": 0.5, "head_pan.pos": -0.2}

    result = driver.execute_action("set_gripper", {"side": "left", "value": "0.15"})
    assert result == "Set left_arm_gripper.pos to 0.15."
    assert client.actions[-1] == {"left_arm_gripper.pos": 0.15}

    result = driver.execute_action("set_gripper", {"side": "right", "value": 0.22})
    assert result == "Set right_arm_gripper.pos to 0.22."
    assert client.actions[-1] == {"right_arm_gripper.pos": 0.22}


def test_robot_id_mismatch_is_rejected_and_stops_base(monkeypatch) -> None:
    driver, client = _driver_with_fake_client(monkeypatch)
    assert driver.execute_action("connect_robot", {}) == "Robot connection established."
    client.actions.clear()

    result = driver.execute_action(
        "set_joint_targets",
        {
            "robot_id": "another_robot",
            "joints": {"left_arm_shoulder_pan.pos": 0.1},
        },
    )
    assert result.startswith("Error: robot_id mismatch:")
    assert client.actions == [{"x.vel": 0.0, "theta.vel": 0.0}]

    nav_state = driver.get_runtime_state()["robots"][driver.robot_id]["nav_state"]
    assert nav_state["status"] == "failed"
    assert "robot_id mismatch" in str(nav_state["last_error"])


def test_runtime_state_has_required_channels_and_is_deep_copy() -> None:
    driver = XLerobot2WheelsRemoteDriver(remote_ip="192.168.1.10")
    runtime = driver.get_runtime_state()

    robot = runtime["robots"][driver.robot_id]
    assert "connection_state" in robot
    assert "robot_pose" in robot
    assert "nav_state" in robot

    runtime["robots"][driver.robot_id]["connection_state"]["status"] = "tampered"
    fresh = driver.get_runtime_state()
    assert fresh["robots"][driver.robot_id]["connection_state"]["status"] == "disconnected"


def test_watchdog_poll_once_updates_environment_and_clears_action(monkeypatch, tmp_path: Path) -> None:
    from hal.hal_watchdog import _poll_once
    from hal.simulation.scene_io import load_environment_doc, save_environment_doc

    driver, client = _driver_with_fake_client(monkeypatch)
    assert driver.execute_action("connect_robot", {}) == "Robot connection established."
    driver.load_scene({"apple": {"type": "fruit", "position": {"x": 0, "y": 0, "z": 0}}})

    env_file = tmp_path / "ENVIRONMENT.md"
    save_environment_doc(
        env_file,
        {
            "schema_version": "oea.environment.v1",
            "scene_graph": {"nodes": [], "edges": []},
            "robots": {
                "desktop_pet_001": {
                    "connection_state": {"status": "connected"},
                    "robot_pose": {"frame": "desk", "x": 0, "y": 0, "z": 0, "yaw": 0},
                    "nav_state": {"mode": "idle", "status": "idle"},
                }
            },
            "objects": {"apple": {"type": "fruit", "position": {"x": 0, "y": 0, "z": 0}}},
        },
    )
    action_file = _write_action_md(
        tmp_path,
        {
            "action_type": "set_gripper",
            "parameters": {"side": "left", "value": 0.3},
            "status": "pending",
        },
    )

    _poll_once(driver, action_file, env_file)

    assert action_file.read_text(encoding="utf-8").strip() == ""
    doc = load_environment_doc(env_file)
    assert driver.robot_id in doc["robots"]
    assert doc["robots"][driver.robot_id]["connection_state"]["status"] == "connected"
    assert doc["robots"][driver.robot_id]["nav_state"]["status"] in {"idle", "stopped"}
    assert doc["robots"]["desktop_pet_001"]["connection_state"]["status"] == "connected"
    assert client.actions[-1] == {"left_arm_gripper.pos": 0.3}
