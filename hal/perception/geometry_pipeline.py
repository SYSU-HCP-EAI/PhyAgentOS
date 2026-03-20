"""Geometry pipeline for fake-data SLAM and map updates."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class GeometryPipeline:
    """Consumes geometric sensor streams and emits map/TF summaries."""

    def process(self, *, pointcloud: Any = None, odom: dict | None = None) -> dict:
        stamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        pointcloud = pointcloud or {}
        map_data = {
            "frame": "map",
            "resolution": 0.05,
            "origin": {"x": 0.0, "y": 0.0, "z": 0.0},
            "stamp": stamp,
        }
        tf_data = {
            "map_to_odom": {"available": True, "stamp": stamp},
            "odom_to_base_link": {"available": odom is not None, "stamp": stamp},
        }

        if isinstance(pointcloud, dict):
            if isinstance(pointcloud.get("map"), dict):
                map_data.update(pointcloud["map"])
            if "zones" in pointcloud and isinstance(pointcloud["zones"], list):
                map_data["zones"] = pointcloud["zones"]
            if isinstance(pointcloud.get("tf"), dict):
                tf_data.update(pointcloud["tf"])
            if "frame" in pointcloud and "frame" not in map_data:
                map_data["frame"] = pointcloud["frame"]

        return {"map": map_data, "tf": tf_data}
