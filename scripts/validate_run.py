#!/usr/bin/env python3
"""Validate a game-art-pipeline run contract for a requested lifecycle phase."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PHASES = ("prepared", "generated", "final", "integrated")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"invalid JSON {path}: {exc}") from exc


def find_profile(run: Path) -> dict[str, Any]:
    for current in (run, *run.parents):
        candidate = current / ".game-art" / "profile.json"
        if candidate.is_file():
            try:
                return read_json(candidate)
            except ValueError:
                return {}
    return {}


def validate_handoff(run: Path, request: dict[str, Any], profile: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    path = run / "engine-handoff.json"
    if not path.is_file():
        warnings.append("engine-handoff.json is missing; integration is not resumable/auditable")
        return
    try:
        handoff = read_json(path)
    except ValueError as exc:
        errors.append(str(exc))
        return

    imports = handoff.get("imports", [])
    if not imports:
        errors.append("engine handoff import plan is empty")
    for item in imports:
        if item.get("status") != "imported":
            errors.append(f"engine import not complete: {item.get('source')} ({item.get('status')})")

    if request.get("asset_type") == "animated-sprite":
        animations = handoff.get("animations", [])
        if not animations:
            errors.append("animated-sprite has no engine animation records")
        for item in animations:
            if item.get("status") not in {"created", "ready"}:
                errors.append(f"engine animation not ready: {item.get('id')} ({item.get('status')})")

    runtime = handoff.get("runtime_object") or {}
    if runtime.get("status") == "failed":
        errors.append("engine runtime object creation failed")

    preview_gate = bool(profile.get("review", {}).get("engine_preview_gate", False))
    if preview_gate:
        preview = handoff.get("preview") or {}
        if preview.get("status") != "pass":
            errors.append(f"engine preview gate not satisfied: {preview.get('status')}")
        if not preview.get("path"):
            errors.append("engine preview gate requires evidence path")
        else:
            preview_path = Path(preview.get("path"))
            if not preview_path.is_absolute():
                preview_path = run / preview_path
            if not preview_path.exists():
                errors.append(f"engine preview evidence file is missing: {preview_path}")
        if preview.get("console_errors") not in {None, 0}:
            errors.append(f"engine preview has console errors: {preview.get('console_errors')}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    parser.add_argument("--phase", choices=PHASES, default="prepared")
    parser.add_argument("--json-output", default=None)
    args = parser.parse_args()

    run = Path(args.run_dir).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not run.is_dir():
        errors.append(f"missing run directory: {run}")
        report = {"run": str(run), "phase": args.phase, "errors": errors, "warnings": warnings}
        print(json.dumps(report, indent=2))
        return 1

    for name in ("request.json", "manifest.json"):
        if not (run / name).is_file():
            errors.append(f"missing {name}")
    for name in ("prompts", "references", "generated", "processed", "final", "qa"):
        if not (run / name).is_dir():
            errors.append(f"missing directory: {name}")

    request = manifest = None
    if not errors:
        try:
            request = read_json(run / "request.json")
            manifest = read_json(run / "manifest.json")
        except ValueError as exc:
            errors.append(str(exc))

    profile = find_profile(run)
    if request and manifest:
        if request.get("asset_id") != manifest.get("asset_id"):
            errors.append("asset_id mismatch between request and manifest")
        canonical_policy = request.get("canonical_policy")
        canonical = manifest.get("canonical", {})
        if args.phase in {"generated", "final", "integrated"} and canonical_policy == "required":
            if not canonical.get("path"):
                errors.append("canonical asset required but manifest canonical.path is empty")
            if not canonical.get("approved"):
                errors.append("canonical asset required but not approved")
        if args.phase in {"generated", "final", "integrated"} and not manifest.get("generations"):
            errors.append("no generation provenance recorded")
        if args.phase in {"final", "integrated"}:
            finals = manifest.get("final_assets", [])
            if not finals:
                errors.append("no final_assets recorded")
            for item in finals:
                value = item.get("path") if isinstance(item, dict) else item
                if not value:
                    errors.append("final asset entry missing path")
                    continue
                p = Path(value)
                if not p.is_absolute():
                    p = run / value
                if not p.exists():
                    errors.append(f"final asset missing: {p}")
        if args.phase == "integrated":
            engine = manifest.get("engine", {})
            if not engine.get("adapter"):
                errors.append("engine adapter not recorded")
            if not engine.get("imports"):
                errors.append("no engine imports recorded")
            if not engine.get("readback"):
                errors.append("engine readback evidence is empty")
            validate_handoff(run, request, profile, errors, warnings)

    report = {
        "run": str(run),
        "phase": args.phase,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.json_output:
        out = Path(args.json_output).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
