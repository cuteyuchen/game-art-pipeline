#!/usr/bin/env python3
"""Create a deterministic art run scaffold with request and manifest contracts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

ASSET_TYPES = {"static-sprite", "animated-sprite", "ui", "fx"}
CANONICAL_POLICIES = {"required", "optional", "none"}


def slug(value: str) -> str:
    value = value.strip().lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        raise ValueError("asset id must contain at least one ASCII letter or digit")
    return value


def load_profile(project_root: Path) -> dict:
    path = project_root / ".game-art" / "profile.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--asset-type", required=True, choices=sorted(ASSET_TYPES))
    parser.add_argument("--description", required=True)
    parser.add_argument("--canonical", choices=sorted(CANONICAL_POLICIES), default=None)
    parser.add_argument("--reference", action="append", default=[])
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--engine-target", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    profile = load_profile(project_root)
    runs_rel = profile.get("paths", {}).get("runs", ".game-art/runs")
    runs_root = (project_root / runs_rel).resolve() if not Path(runs_rel).is_absolute() else Path(runs_rel)
    asset_id = slug(args.asset_id)
    run_id = slug(args.run_id) if args.run_id else dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ").lower()
    run = runs_root / asset_id / run_id
    if run.exists() and any(run.iterdir()) and not args.force:
        raise SystemExit(f"run already exists and is not empty: {run}")
    for name in ("prompts", "references", "generated", "processed", "final", "qa"):
        (run / name).mkdir(parents=True, exist_ok=True)

    canonical = args.canonical or ("required" if args.asset_type in {"static-sprite", "animated-sprite", "ui"} else "optional")
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    request = {
        "schema_version": 1,
        "asset_id": asset_id,
        "asset_type": args.asset_type,
        "description": args.description,
        "created_at": now,
        "canonical_policy": canonical,
        "references": [{"path": ref, "role": None} for ref in args.reference],
        "engine_target": args.engine_target,
        "notes": [],
    }
    manifest = {
        "schema_version": 1,
        "asset_id": asset_id,
        "run_id": run_id,
        "status": "prepared",
        "canonical": {"path": None, "approved": False, "approval_note": None},
        "generations": [],
        "processing": [],
        "final_assets": [],
        "qa": {"deterministic": [], "visual_review": None, "warnings": []},
        "engine": {"adapter": None, "imports": [], "readback": None, "preview": None},
    }
    (run / "request.json").write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (run / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
