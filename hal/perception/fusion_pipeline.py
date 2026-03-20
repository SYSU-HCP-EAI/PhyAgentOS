"""Fusion pipeline for building scene graph nodes from fake detections."""

from __future__ import annotations

import math
from datetime import datetime


class FusionPipeline:
    """Fuses detections into a structured scene graph."""

    def process(self, detections: list[dict], geometry: dict | None = None) -> dict:
        timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        nodes = []
        edges = []
        for idx, detection in enumerate(detections):
            center = detection.get("center") or {"x": 0.0, "y": 0.0, "z": 0.0}
            size = detection.get("size") or {"x": 0.5, "y": 0.5, "z": 0.5}
            node_id = detection.get("id", f"det_{idx}")
            nodes.append(
                {
                    "id": node_id,
                    "class": detection.get("label", "unknown"),
                    "object_key": detection.get("object_key"),
                    "confidence": detection.get("confidence", 0.0),
                    "center": center,
                    "size": size,
                    "frame": detection.get("frame", "map"),
                    "track_id": detection.get("track_id", f"track_{idx}"),
                    "last_seen_at": timestamp,
                }
            )
            for relation in detection.get("relations", []):
                if all(key in relation for key in ("relation", "target")):
                    edges.append(
                        {
                            "source": node_id,
                            "relation": relation["relation"],
                            "target": relation["target"],
                            "confidence": float(relation.get("confidence", detection.get("confidence", 0.0))),
                        }
                    )

        for idx, source in enumerate(nodes):
            for target in nodes[idx + 1:]:
                s_center = source.get("center") or {}
                t_center = target.get("center") or {}
                if not {"x", "y"}.issubset(s_center) or not {"x", "y"}.issubset(t_center):
                    continue
                distance = math.hypot(s_center["x"] - t_center["x"], s_center["y"] - t_center["y"])
                if distance <= 0.5:
                    edges.append(
                        {
                            "source": source["id"],
                            "relation": "CLOSE_TO",
                            "target": target["id"],
                            "confidence": 0.75,
                        }
                    )

        return {"nodes": nodes, "edges": edges}
