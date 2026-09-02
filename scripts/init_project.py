#!/usr/bin/env python3
"""Initialize a reusable .game-art project profile without overwriting existing files by default."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        print(f"SKIP existing: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"WRITE: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    parser.add_argument("--name", required=True)
    parser.add_argument("--engine", default="engine-neutral")
    parser.add_argument("--engine-version", default=None)
    parser.add_argument("--runtime-assets", default="assets")
    parser.add_argument("--generator", default="auto")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cfg = root / ".game-art"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "source").mkdir(exist_ok=True)
    (cfg / "runs").mkdir(exist_ok=True)
    (cfg / "references").mkdir(exist_ok=True)

    profile = {
        "schema_version": 1,
        "project": {"name": args.name},
        "engine": {"type": args.engine, "version": args.engine_version, "adapter": "auto", "instructions_file": None},
        "generation": {"preferred": args.generator, "fallbacks": []},
        "art_direction": {"style_file": ".game-art/style.md", "camera_file": None, "additional_files": []},
        "paths": {"runs": ".game-art/runs", "source_assets": ".game-art/source", "runtime_assets": args.runtime_assets},
        "defaults": {"format": "png", "background": "transparent"},
        "review": {"canonical_gate": True, "visual_qa": True, "engine_preview_gate": True},
    }

    profile_path = cfg / "profile.json"
    if profile_path.exists() and not args.force:
        print(f"SKIP existing: {profile_path}")
    else:
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"WRITE: {profile_path}")

    write_text(cfg / "style.md", "# Project Art Direction\n\nDescribe visual style, palette, shape language, materials, readability targets, and explicit avoidances here.\n", args.force)
    write_text(cfg / "README.md", "# .game-art\n\nProject-local configuration and auditable art-production runs used by game-art-pipeline.\n", args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
