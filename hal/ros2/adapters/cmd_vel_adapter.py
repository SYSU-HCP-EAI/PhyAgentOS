"""cmd_vel adapter node skeleton."""

from __future__ import annotations


class CmdVelAdapter:
    """Normalizes velocity command payloads for platform SDK bridges."""

    def normalize(self, *, vx: float, vy: float = 0.0, wz: float = 0.0) -> dict:
        return {"vx": vx, "vy": vy, "wz": wz}
