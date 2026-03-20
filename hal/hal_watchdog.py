#!/usr/bin/env python3
"""
hal/hal_watchdog.py

HAL Watchdog — polls ACTION.md for commands, dispatches them to the
active driver, and writes updated state back to ENVIRONMENT.md.

The driver is selected at startup via ``--driver <name>`` and loaded
dynamically from the driver registry.  The driver's EMBODIED.md profile
is automatically copied into the workspace.

Usage
-----
    python hal/hal_watchdog.py                          # simulation (default)
    python hal/hal_watchdog.py --driver simulation --gui
    python hal/hal_watchdog.py --driver go2_edu
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

from hal.simulation.scene_io import (
    load_environment_doc,
    load_scene_from_md,
    merge_environment_doc,
    save_environment_doc,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[HAL Watchdog {ts}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# ACTION.md parsing
# ---------------------------------------------------------------------------

_ACTION_RE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def parse_action(content: str) -> dict | None:
    """Extract the first JSON code block from ACTION.md content."""
    m = _ACTION_RE.search(content)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# Scene I/O (thin wrapper so watchdog doesn't depend on hal.simulation)
# ---------------------------------------------------------------------------

_FENCE_OPEN = "```json"
_FENCE_CLOSE = "```"


def _load_scene(path: Path) -> dict[str, dict]:
    return load_scene_from_md(path)


def _save_scene(driver, path: Path, scene: dict[str, dict]) -> None:
    existing = load_environment_doc(path)
    runtime_state = {}
    runtime_getter = getattr(driver, "get_runtime_state", None)
    if callable(runtime_getter):
        runtime_state = runtime_getter() or {}
    updated = merge_environment_doc(
        existing,
        objects=scene,
        robots=runtime_state.get("robots"),
        scene_graph=runtime_state.get("scene_graph"),
        map_data=runtime_state.get("map"),
        tf_data=runtime_state.get("tf"),
        updated_at=datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    )
    save_environment_doc(path, updated)


# ---------------------------------------------------------------------------
# Profile auto-copy
# ---------------------------------------------------------------------------

def _install_profile(driver, workspace: Path) -> None:
    """Copy the driver's EMBODIED.md profile into the workspace."""
    src = driver.get_profile_path()
    dst = workspace / "EMBODIED.md"
    if src.exists():
        shutil.copy2(src, dst)
        _log(f"Profile installed: {src.name} -> EMBODIED.md")
    else:
        _log(f"WARNING: profile not found at {src}")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def watch_loop(
    workspace: Path,
    driver_name: str = "simulation",
    gui: bool = False,
    poll_interval: float = 1.0,
) -> None:
    """Load a driver, install its profile, then poll ACTION.md forever."""
    from hal.drivers import load_driver

    _log(f"Workspace : {workspace}")
    _log(f"Driver    : {driver_name}")
    _log(f"GUI       : {gui}")

    driver = load_driver(driver_name, gui=gui)

    with driver:
        _install_profile(driver, workspace)

        # Initialise scene
        env_file = workspace / "ENVIRONMENT.md"
        scene = _load_scene(env_file)
        driver.load_scene(scene)
        _log(f"Scene loaded ({len(scene)} object(s))")
        _log("Watching ACTION.md … Ctrl+C to stop.\n")

        action_file = workspace / "ACTION.md"
        try:
            while True:
                _poll_once(driver, action_file, env_file)
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            _log("Shutdown.")


def _poll_once(driver, action_file: Path, env_file: Path) -> None:
    """Single poll: read ACTION.md → execute → update ENVIRONMENT.md."""
    if not action_file.exists():
        return
    content = action_file.read_text(encoding="utf-8").strip()
    if not content:
        return

    action = parse_action(content)
    if action is None:
        _log("ACTION.md has content but no valid JSON — skipping.")
        return

    action_type = action.get("action_type", "unknown")
    params = action.get("parameters", {})
    _log(f"Action: {action_type!r}  params={params}")

    time.sleep(0.3)  # simulate motor spin-up

    result = driver.execute_action(action_type, params)
    _log(f"Result: {result}")

    _save_scene(driver, env_file, driver.get_scene())
    _log("ENVIRONMENT.md updated.")

    action_file.write_text("", encoding="utf-8")
    _log("ACTION.md cleared.\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    from hal.drivers import list_drivers

    parser = argparse.ArgumentParser(
        description="HAL Watchdog — OpenEmbodiedAgent hardware layer",
    )
    parser.add_argument(
        "--driver",
        default="simulation",
        help=f"Driver name (available: {', '.join(list_drivers())})",
    )
    parser.add_argument(
        "--workspace",
        default=str(Path.home() / ".nanobot" / "workspace"),
        help="Workspace directory (default: ~/.nanobot/workspace)",
    )
    parser.add_argument("--gui", action="store_true", help="Open 3-D viewer")
    parser.add_argument(
        "--interval", type=float, default=1.0, help="Poll interval (seconds)",
    )
    args = parser.parse_args()

    ws = Path(args.workspace).expanduser().resolve()
    if not ws.exists():
        print(f"Error: workspace not found: {ws}", file=sys.stderr)
        print("Run 'nanobot onboard' first.", file=sys.stderr)
        sys.exit(1)

    watch_loop(ws, driver_name=args.driver, gui=args.gui,
               poll_interval=args.interval)


if __name__ == "__main__":
    main()
