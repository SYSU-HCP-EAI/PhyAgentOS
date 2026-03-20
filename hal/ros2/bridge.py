"""Thin ROS2 bridge with a dependency-free mock mode."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ROS2Bridge:
    """
    Minimal ROS2 facade.

    The initial implementation intentionally supports a mock mode so the
    navigation stack can be exercised in tests without a ROS2 install.
    """

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self._subscriptions: dict[str, list[Callable[[Any], None]]] = {}
        self._published: list[tuple[str, Any]] = []

    def publish(self, topic: str, msg: Any) -> None:
        self._published.append((topic, msg))
        for callback in self._subscriptions.get(topic, []):
            callback(msg)

    def subscribe(self, topic: str, callback: Callable[[Any], None]) -> None:
        self._subscriptions.setdefault(topic, []).append(callback)

    def create_action_client(self, action_name: str) -> str:
        return action_name

    def get_buffered_messages(self, topic: str) -> list[Any]:
        return [msg for published_topic, msg in self._published if published_topic == topic]
