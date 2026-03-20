"""Public API for the HAL simulation package."""

from .scene_io import load_environment_doc, load_scene_from_md, save_environment_doc, save_scene_to_md

__all__ = [
    "PyBulletSimulator",
    "load_environment_doc",
    "load_scene_from_md",
    "save_environment_doc",
    "save_scene_to_md",
]


def __getattr__(name: str):
    if name == "PyBulletSimulator":
        from .pybullet_sim import PyBulletSimulator

        return PyBulletSimulator
    raise AttributeError(name)
