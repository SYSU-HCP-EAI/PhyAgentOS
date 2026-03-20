"""LiDAR adapter node skeleton."""

from __future__ import annotations

from typing import Any


class LidarAdapter:
    """Normalizes point cloud or scan data into OEA transport payloads."""

    def normalize(self, cloud: Any, frame: str = "lidar") -> dict:
        return {"frame": frame, "cloud": cloud}
