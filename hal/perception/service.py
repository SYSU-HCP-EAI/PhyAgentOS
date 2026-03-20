"""Side-loaded perception daemon with fake-data friendly inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hal.perception.environment_writer import EnvironmentWriter
from hal.perception.fusion_pipeline import FusionPipeline
from hal.perception.geometry_pipeline import GeometryPipeline
from hal.perception.segmentation_pipeline import SegmentationPipeline


class PerceptionService:
    """Coordinates geometry, segmentation, fusion, and environment writes."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.geometry = GeometryPipeline()
        self.segmentation = SegmentationPipeline()
        self.fusion = FusionPipeline()
        self.writer = EnvironmentWriter(workspace)

    def tick(
        self,
        *,
        robot_id: str,
        image: Any = None,
        pointcloud: Any = None,
        odom: dict | None = None,
        nav_state: dict | None = None,
    ) -> dict:
        geometry = self.geometry.process(pointcloud=pointcloud, odom=odom)
        detections = self.segmentation.process(image=image)
        scene_graph = self.fusion.process(detections=detections, geometry=geometry)
        return self.writer.write(
            robot_id=robot_id,
            robot_pose=odom,
            nav_state=nav_state,
            scene_graph=scene_graph,
            map_data=geometry.get("map"),
            tf_data=geometry.get("tf"),
        )
