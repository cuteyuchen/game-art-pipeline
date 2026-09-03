#!/usr/bin/env python3
"""Build an engine-neutral animation frame manifest from a plan and final PNG frames."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def natural_key(path: Path) -> list[Any]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def durations(value: Any, count: int) -> list[int]:
    if isinstance(value, int) and value > 0:
        return [value] * count
    if isinstance(value, list) and len(value) == count and all(isinstance(x, int) and x > 0 for x in value):
        return value
    raise ValueError(f"durations_ms must be a positive integer or {count} positive integers")


def discover_frames(root: Path, animation_id: str) -> list[Path]:
    nested = root / animation_id
    if nested.is_dir():
        frames = sorted((p for p in nested.glob("*.png") if p.is_file()), key=natural_key)
        if frames:
            return frames
    return sorted((p for p in root.glob(f"{animation_id}-*.png") if p.is_file()), key=natural_key)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("animation_plan")
    parser.add_argument("--frames-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--relative-to", default=None)
    args = parser.parse_args()

    plan_path = Path(args.animation_plan).resolve()
    frames_root = Path(args.frames_root).resolve()
    output = Path(args.output).resolve()
    relative_to = Path(args.relative_to).resolve() if args.relative_to else output.parent

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    animations = plan.get("animations")
    if not isinstance(animations, list) or not animations:
        raise SystemExit("animation plan has no animations")

    result: list[dict[str, Any]] = []
    for item in animations:
        animation_id = str(item.get("id") or "").strip()
        expected = item.get("frames")
        if not animation_id or not isinstance(expected, int) or expected <= 0:
            raise SystemExit(f"invalid animation entry: {item}")
        frames = discover_frames(frames_root, animation_id)
        if len(frames) != expected:
            raise SystemExit(f"{animation_id}: expected {expected} PNG frames, found {len(frames)} in {frames_root}")
        try:
            timing = durations(item.get("durations_ms"), expected)
        except ValueError as exc:
            raise SystemExit(f"{animation_id}: {exc}") from exc
        frame_values: list[str] = []
        for frame in frames:
            try:
                frame_values.append(frame.relative_to(relative_to).as_posix())
            except ValueError:
                frame_values.append(str(frame))
        result.append(
            {
                "id": animation_id,
                "frames": frame_values,
                "durations_ms": timing,
                "loop": bool(item.get("loop", False)),
            }
        )

    payload = {
        "schema_version": 1,
        "kind": "sprite-frame-sequences",
        "anchor": plan.get("anchor"),
        "animations": result,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
