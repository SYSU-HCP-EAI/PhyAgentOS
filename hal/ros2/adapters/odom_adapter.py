"""Odometry adapter node skeleton."""

from __future__ import annotations

from datetime import datetime

from hal.ros2.messages import RobotPose


class OdomAdapter:
    """Converts odometry payloads into RobotPose snapshots."""

    def normalize(
        self,
        *,
        frame: str,
        x: float,
        y: float,
        z: float = 0.0,
        yaw: float = 0.0,
    ) -> RobotPose:
        return RobotPose(
            frame=frame,
            x=x,
            y=y,
            z=z,
            yaw=yaw,
            stamp=datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        )
