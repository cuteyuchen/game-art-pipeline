#!/usr/bin/env python3
"""Copy one selected real generator output into a run and record provenance."""

from __future__ import annotations

import argparse, datetime as dt, hashlib, json, shutil
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("run_dir")
    p.add_argument("--source", required=True)
    p.add_argument("--adapter", required=True)
    p.add_argument("--model", default=None)
    p.add_argument("--prompt", default=None)
    p.add_argument("--reference", action="append", default=[])
    p.add_argument("--name", default=None)
    p.add_argument("--force", action="store_true")
    a = p.parse_args()

    run, source = Path(a.run_dir).resolve(), Path(a.source).resolve()
    if not source.is_file(): raise SystemExit(f"missing source: {source}")
    manifest_path = run / "manifest.json"
    if not manifest_path.is_file(): raise SystemExit(f"missing manifest: {manifest_path}")
    target = run / "generated" / (a.name or source.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not a.force: raise SystemExit(f"generated target already exists: {target}")
    shutil.copy2(source, target)

    prompt_value = None
    if a.prompt:
        pp = Path(a.prompt).resolve()
        if not pp.is_file(): raise SystemExit(f"prompt file does not exist: {pp}")
        prompt_value = str(pp)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.setdefault("generations", []).append({
        "adapter": a.adapter,
        "model": a.model,
        "prompt": prompt_value,
        "references": list(a.reference),
        "selected_source": str(source),
        "copied_path": str(target.relative_to(run)),
        "sha256": digest(target),
        "recorded_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    })
    manifest["status"] = "generating"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__": raise SystemExit(main())
