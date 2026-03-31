"""Remote XLerobot2Wheels driver backed by lerobot ZMQ client."""

from __future__ import annotations

import copy
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from hal.base_driver import BaseDriver

_PROFILES_DIR = Path(__file__).resolve().parent.parent / "profiles"


def _parse_int(raw: str | None, default: int) -> int:
    if raw in (None, ""):
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _parse_float(raw: str | None, default: float) -> float:
    if raw in (None, ""):
        return default
    try:
        return float(raw)
    except ValueError:
        return default


class XLerobot2WheelsRemoteDriver(BaseDriver):
    """Control a remote XLerobot2Wheels host through ZMQ."""

    def __init__(
        self,
        gui: bool = False,
        *,
        remote_ip: str | None = None,
        cmd_port: int | None = None,
        obs_port: int | None = None,
        robot_id: str | None = None,
        loop_hz: float | None = None,
        max_move_duration_s: float | None = None,
        safe_max_linear_m_s: float | None = None,
        safe_max_angular_deg_s: float | None = None,
        lerobot_src: str | None = None,
        reconnect_policy: str = "auto",
        **_kwargs: Any,
    ) -> None:
        self._gui = gui
        self.remote_ip = (remote_ip or os.environ.get("OEA_XLEROBOT_REMOTE_IP", "192.168.86.31")).strip()
        self.cmd_port = cmd_port or _parse_int(os.environ.get("OEA_XLEROBOT_CMD_PORT"), 5555)
        self.obs_port = obs_port or _parse_int(os.environ.get("OEA_XLEROBOT_OBS_PORT"), 5556)
        self.robot_id = (robot_id or os.environ.get("OEA_XLEROBOT_ROBOT_ID") or "my_xlerobot_2wheels_lab").strip()
        self.loop_hz = max(loop_hz or _parse_float(os.environ.get("OEA_XLEROBOT_LOOP_HZ"), 20.0), 1.0)
        self.max_move_duration_s = max(
            max_move_duration_s
            or _parse_float(os.environ.get("OEA_XLEROBOT_MAX_MOVE_DURATION_S"), 10.0),
            0.1,
        )
        self.safe_max_linear_m_s = max(
            safe_max_linear_m_s
            or _parse_float(os.environ.get("OEA_XLEROBOT_SAFE_MAX_LINEAR_M_S"), 0.4),
            0.0,
        )
        self.safe_max_angular_deg_s = max(
            safe_max_angular_deg_s
            or _parse_float(os.environ.get("OEA_XLEROBOT_SAFE_MAX_ANGULAR_DEG_S"), 120.0),
            0.0,
        )
        self.lerobot_src = (
            lerobot_src
            or os.environ.get("OEA_LEROBOT_SRC")
            or "/home/ubuntu/lerobot/src"
        )
        self.reconnect_policy = reconnect_policy

        self._objects: dict[str, dict] = {}
        self._client: Any | None = None
        self._runtime_state = {"robots": {self.robot_id: self._make_robot_state()}}

    def get_profile_path(self) -> Path:
        return _PROFILES_DIR / "xlerobot_2wheels_remote.md"

    def load_scene(self, scene: dict[str, dict]) -> None:
        self._objects = dict(scene)

    def execute_action(self, action_type: str, params: dict) -> str:
        try:
            self._validate_robot_id(params)
            if action_type == "connect_robot":
                return "Robot connection established." if self.connect() else self._conn_error()
            if action_type == "check_connection":
                return "connected" if self.health_check() else "disconnected"
            if action_type == "disconnect_robot":
                self.disconnect()
                return "Robot connection closed."
            if action_type == "stop":
                return self._stop_motion("stopped")

            if action_type == "move_base":
                return self._execute_move_base(params)
            if action_type == "set_joint_targets":
                return self._execute_set_joint_targets(params)
            if action_type == "set_gripper":
                return self._execute_set_gripper(params)

            return f"Unknown action: {action_type}"
        except ValueError as exc:
            return self._error_result(str(exc))
        except Exception as exc:
            return self._error_result(f"{action_type} failed: {exc}")

    def get_scene(self) -> dict[str, dict]:
        return dict(self._objects)

    def connect(self) -> bool:
        if self.is_connected():
            self._set_connection_status("connected", last_error=None)
            self._touch_heartbeat()
            return True

        if not self.remote_ip:
            self._set_connection_status("error", last_error="missing OEA_XLEROBOT_REMOTE_IP")
            return False

        try:
            self._client = self._build_client()
            self._client.connect()
            _ = self._client.get_observation()
            self._set_connection_status("connected", last_error=None)
            self._touch_heartbeat()
            self._set_nav_state(mode="idle", status="idle", last_error=None)
            return True
        except Exception as exc:
            self._client = None
            self._set_connection_status("error", last_error=str(exc))
            return False

    def disconnect(self) -> None:
        if self._client is None:
            self._set_connection_status("disconnected", last_error=None)
            self._set_nav_state(mode="idle", status="idle", last_error=None)
            return

        try:
            if self.is_connected():
                self._safe_send_action({"x.vel": 0.0, "theta.vel": 0.0})
        except Exception:
            pass

        try:
            self._client.disconnect()
        except Exception as exc:
            self._set_connection_status("error", last_error=str(exc))
        finally:
            self._client = None
            self._set_connection_status("disconnected", last_error=None)
            self._set_nav_state(mode="idle", status="idle", last_error=None)

    def is_connected(self) -> bool:
        return bool(self._client) and bool(getattr(self._client, "is_connected", False))

    def health_check(self) -> bool:
        if not self.is_connected():
            if self.reconnect_policy == "auto":
                self._inc_reconnect_attempts()
                self._set_connection_status("reconnecting", last_error="disconnected")
                connected = self.connect()
                if not connected:
                    self._stop_motion(
                        "failed",
                        last_error=self._robot_state().get("connection_state", {}).get("last_error"),
                    )
                return connected
            self._set_connection_status("disconnected", last_error="disconnected")
            self._stop_motion("failed", last_error="disconnected")
            return False

        try:
            _ = self._client.get_observation()
            self._touch_heartbeat()
            self._set_connection_status("connected", last_error=None)
            self._touch_pose()
            return True
        except Exception as exc:
            self._set_connection_status("error", last_error=str(exc))
            self._stop_motion("failed", last_error=str(exc))
            return False

    def get_runtime_state(self) -> dict[str, Any]:
        return copy.deepcopy(self._runtime_state)

    def close(self) -> None:
        self.disconnect()

    def _build_client(self):
        source = Path(self.lerobot_src).expanduser().resolve()
        source_str = str(source)
        if source_str not in sys.path:
            sys.path.insert(0, source_str)

        try:
            from lerobot.robots.xlerobot_2wheels import (  # type: ignore
                XLerobot2WheelsClient,
                XLerobot2WheelsClientConfig,
            )
        except Exception as exc:
            raise RuntimeError(
                "Failed to import lerobot xlerobot_2wheels client. "
                f"Check OEA_LEROBOT_SRC ({source}) and dependencies (draccus/pyzmq). "
                f"Original error: {exc}"
            ) from exc

        config = XLerobot2WheelsClientConfig(
            id=self.robot_id,
            remote_ip=self.remote_ip,
            port_zmq_cmd=self.cmd_port,
            port_zmq_observations=self.obs_port,
        )
        return XLerobot2WheelsClient(config)

    def _validate_robot_id(self, params: dict[str, Any]) -> None:
        requested = str(params.get("robot_id", "")).strip()
        if requested and requested != self.robot_id:
            raise ValueError(
                f"robot_id mismatch: requested={requested}, configured={self.robot_id}"
            )

    def _execute_move_base(self, params: dict[str, Any]) -> str:
        if not self.is_connected():
            return self._conn_error()

        try:
            x_vel = self._clip(
                float(params.get("x_vel_m_s", params.get("x.vel", 0.0))),
                self.safe_max_linear_m_s,
            )
            theta_vel = self._clip(
                float(params.get("theta_deg_s", params.get("theta.vel", 0.0))),
                self.safe_max_angular_deg_s,
            )
            duration_s = float(params.get("duration_s", 1.0))
            duration_s = max(0.0, min(duration_s, self.max_move_duration_s))
        except (TypeError, ValueError) as exc:
            return self._error_result(f"invalid move_base parameters: {exc}")

        if duration_s <= 0:
            return self._error_result("duration_s must be > 0.")

        self._set_nav_state(
            mode="velocity_control",
            status="running",
            goal={"x_vel_m_s": x_vel, "theta_deg_s": theta_vel, "duration_s": duration_s},
            last_error=None,
        )

        loop_dt = 1.0 / self.loop_hz
        deadline = time.monotonic() + duration_s
        try:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self._safe_send_action({"x.vel": x_vel, "theta.vel": theta_vel})
                time.sleep(min(loop_dt, remaining))
            self._stop_motion("stopped")
            return (
                f"Base moved for {duration_s:.2f}s at x={x_vel:.3f} m/s, "
                f"theta={theta_vel:.2f} deg/s."
            )
        except Exception as exc:
            return self._error_result(f"move_base failed: {exc}")

    def _execute_set_joint_targets(self, params: dict[str, Any]) -> str:
        if not self.is_connected():
            return self._conn_error()

        joints = params.get("joints")
        if not isinstance(joints, dict) or not joints:
            return "Error: joints must be a non-empty object."

        payload: dict[str, float] = {}
        try:
            for key, value in joints.items():
                payload[str(key)] = float(value)
            self._safe_send_action(payload)
            self._touch_pose()
            return f"Applied {len(payload)} joint target(s)."
        except Exception as exc:
            return self._error_result(f"set_joint_targets failed: {exc}")

    def _execute_set_gripper(self, params: dict[str, Any]) -> str:
        if not self.is_connected():
            return self._conn_error()

        side = str(params.get("side", "left")).strip().lower()
        if side not in {"left", "right"}:
            return "Error: side must be 'left' or 'right'."
        if "value" not in params:
            return "Error: value is required."

        try:
            value = float(params["value"])
            joint = "left_arm_gripper.pos" if side == "left" else "right_arm_gripper.pos"
            self._safe_send_action({joint: value})
            return f"Set {joint} to {value:.2f}."
        except Exception as exc:
            return self._error_result(f"set_gripper failed: {exc}")

    def _stop_motion(self, status: str, last_error: str | None = None) -> str:
        try:
            if self.is_connected():
                self._safe_send_action({"x.vel": 0.0, "theta.vel": 0.0})
        except Exception:
            pass
        self._set_nav_state(mode="idle", status=status, last_error=last_error)
        return "Motion stopped." if status == "stopped" else f"Motion {status}."

    def _safe_send_action(self, action: dict[str, float]) -> None:
        if not self.is_connected():
            raise RuntimeError("robot is not connected")
        self._client.send_action(action)
        self._touch_heartbeat()

    def _conn_error(self) -> str:
        details = self._robot_state().get("connection_state", {}).get("last_error")
        suffix = f" Details: {details}" if details else ""
        return (
            "Connection error: robot is not connected. "
            "Run connect_robot first and ensure Orin host is running."
            + suffix
        )

    def _mark_nav_failed(self, reason: str) -> None:
        self._set_nav_state(mode="idle", status="failed", last_error=reason)

    def _error_result(self, reason: str) -> str:
        self._mark_nav_failed(reason)
        self._stop_motion("failed", last_error=reason)
        return f"Error: {reason}"

    @staticmethod
    def _clip(value: float, maximum: float) -> float:
        return max(-maximum, min(maximum, value))

    def _robot_state(self) -> dict[str, Any]:
        robots = self._runtime_state.setdefault("robots", {})
        if self.robot_id not in robots:
            robots[self.robot_id] = self._make_robot_state()
        return robots[self.robot_id]

    def _make_robot_state(self) -> dict[str, Any]:
        stamp = self._stamp()
        return {
            "connection_state": {
                "status": "disconnected",
                "transport": "zmq",
                "host": self.remote_ip,
                "port": self.cmd_port,
                "obs_port": self.obs_port,
                "last_heartbeat": None,
                "last_error": None,
                "reconnect_attempts": 0,
            },
            "robot_pose": {
                "frame": "map",
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "yaw": 0.0,
                "stamp": stamp,
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

    def _set_connection_status(self, status: str, last_error: str | None) -> None:
        state = self._robot_state()
        conn = dict(state.get("connection_state", {}))
        conn.update(
            {
                "status": status,
                "transport": "zmq",
                "host": self.remote_ip,
                "port": self.cmd_port,
                "obs_port": self.obs_port,
                "last_error": last_error,
            }
        )
        state["connection_state"] = conn

    def _set_nav_state(
        self,
        *,
        mode: str,
        status: str,
        goal: dict[str, Any] | None = None,
        last_error: str | None = None,
    ) -> None:
        state = self._robot_state()
        current = dict(state.get("nav_state", {}))
        state["nav_state"] = {
            "mode": mode,
            "status": status,
            "goal_id": None,
            "target_ref": None,
            "goal": goal,
            "path_progress": None,
            "recovery_count": current.get("recovery_count", 0),
            "last_error": last_error,
            "relocalization_confidence": None,
        }

    def _inc_reconnect_attempts(self) -> None:
        state = self._robot_state()
        conn = dict(state.get("connection_state", {}))
        conn["reconnect_attempts"] = int(conn.get("reconnect_attempts", 0)) + 1
        state["connection_state"] = conn

    def _touch_heartbeat(self) -> None:
        state = self._robot_state()
        conn = dict(state.get("connection_state", {}))
        conn["last_heartbeat"] = self._stamp()
        state["connection_state"] = conn

    def _touch_pose(self) -> None:
        state = self._robot_state()
        pose = dict(state.get("robot_pose", {}))
        pose.setdefault("frame", "map")
        pose.setdefault("x", 0.0)
        pose.setdefault("y", 0.0)
        pose.setdefault("z", 0.0)
        pose.setdefault("yaw", 0.0)
        pose["stamp"] = self._stamp()
        state["robot_pose"] = pose

    @staticmethod
    def _stamp() -> str:
        return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
