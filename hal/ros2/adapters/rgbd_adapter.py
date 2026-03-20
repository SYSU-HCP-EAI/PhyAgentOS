"""RGB-D adapter node skeleton."""

from __future__ import annotations

from typing import Any


class RGBDAdapter:
    """Normalizes vendor RGB-D streams into OEA-friendly payloads."""

    def normalize(self, color: Any, depth: Any, camera_info: dict | None = None) -> dict:
        return {
            "color": color,
            "depth": depth,
            "camera_info": camera_info or {},
        }
