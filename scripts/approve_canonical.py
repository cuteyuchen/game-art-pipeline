#!/usr/bin/env python3
"""Approve an existing run image as the canonical reference."""

from __future__ import annotations
import argparse, json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("run_dir")
    p.add_argument("--image", required=True)
    p.add_argument("--note", default="approved canonical reference")
    a = p.parse_args()
    run = Path(a.run_dir).resolve()
    image = Path(a.image)
    if not image.is_absolute(): image = (run / image).resolve()
    if not image.is_file(): raise SystemExit(f"missing canonical image: {image}")
    mp = run / "manifest.json"
    manifest = json.loads(mp.read_text(encoding="utf-8"))
    try: stored = str(image.relative_to(run))
    except ValueError: stored = str(image)
    manifest["canonical"] = {"path": stored, "approved": True, "approval_note": a.note}
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(stored)
    return 0


if __name__ == "__main__": raise SystemExit(main())
