#!/usr/bin/env python3
"""Copy a runtime-ready file into run/final and register it in manifest.json."""

from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path


def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("run_dir"); p.add_argument("--source", required=True); p.add_argument("--kind", default="image"); p.add_argument("--name", default=None); p.add_argument("--force", action="store_true"); a=p.parse_args()
    run, source = Path(a.run_dir).resolve(), Path(a.source).resolve()
    if not source.is_file(): raise SystemExit(f"missing source: {source}")
    target = run/"final"/(a.name or source.name); target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.resolve()!=source and not a.force: raise SystemExit(f"final target already exists: {target}")
    if target.resolve()!=source: shutil.copy2(source,target)
    mp=run/"manifest.json"; manifest=json.loads(mp.read_text(encoding="utf-8"))
    record={"kind":a.kind,"path":str(target.relative_to(run)),"sha256":digest(target)}
    existing=manifest.setdefault("final_assets",[]); existing[:]=[x for x in existing if not(isinstance(x,dict) and x.get("path")==record["path"])]; existing.append(record)
    manifest["status"]="qa"; mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(target); return 0


if __name__=="__main__": raise SystemExit(main())
