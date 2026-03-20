"""Segmentation pipeline with deterministic fake-data support."""

from __future__ import annotations

from typing import Any


class SegmentationPipeline:
    """Produces semantic detections from RGB frames or test payloads."""

    def process(self, image: Any = None) -> list[dict]:
        if image is None:
            return []
        if isinstance(image, dict) and isinstance(image.get("detections"), list):
            return [self._normalize_detection(det, idx) for idx, det in enumerate(image["detections"])]
        if isinstance(image, list):
            return [self._normalize_detection(det, idx) for idx, det in enumerate(image)]
        return [{"label": "unknown", "confidence": 0.0, "track_id": "track_0"}]

    @staticmethod
    def _normalize_detection(detection: dict, idx: int) -> dict:
        center = detection.get("center") or {"x": 0.0, "y": 0.0, "z": 0.0}
        size = detection.get("size") or {"x": 0.5, "y": 0.5, "z": 0.5}
        return {
            "id": detection.get("id", f"det_{idx}"),
            "label": detection.get("label", detection.get("class", "unknown")),
            "confidence": float(detection.get("confidence", 0.0)),
            "object_key": detection.get("object_key"),
            "center": center,
            "size": size,
            "frame": detection.get("frame", "map"),
            "track_id": detection.get("track_id", f"track_{idx}"),
            "relations": detection.get("relations", []),
        }
