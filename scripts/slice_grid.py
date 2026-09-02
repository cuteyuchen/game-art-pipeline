#!/usr/bin/env python3
"""Slice an existing equal-cell sprite grid into deterministic PNG frames. Requires Pillow."""

from __future__ import annotations
import argparse, json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("sheet"); p.add_argument("output_dir")
    p.add_argument("--rows", type=int, required=True); p.add_argument("--columns", type=int, required=True)
    p.add_argument("--used", type=int, default=None); p.add_argument("--prefix", default="frame")
    a = p.parse_args()
    if a.rows < 1 or a.columns < 1: raise SystemExit("rows and columns must be positive")
    try: from PIL import Image
    except Exception as exc: raise SystemExit(f"Pillow is required: {exc}")
    sheet, out = Path(a.sheet).resolve(), Path(a.output_dir).resolve()
    if not sheet.is_file(): raise SystemExit(f"missing sheet: {sheet}")
    out.mkdir(parents=True, exist_ok=True)
    with Image.open(sheet) as src: im = src.convert("RGBA")
    if im.width % a.columns or im.height % a.rows: raise SystemExit(f"sheet size {im.size} is not divisible by {a.columns}x{a.rows}")
    cw, ch = im.width // a.columns, im.height // a.rows
    total = a.rows * a.columns; used = total if a.used is None else a.used
    if used < 1 or used > total: raise SystemExit("--used must be between 1 and rows*columns")
    frames = []
    for i in range(used):
        row, col = divmod(i, a.columns)
        crop = im.crop((col*cw, row*ch, (col+1)*cw, (row+1)*ch))
        name = f"{a.prefix}-{i:03d}.png"; crop.save(out/name, "PNG")
        frames.append({"index": i, "file": name, "rect": [col*cw, row*ch, cw, ch]})
    (out/"frames.json").write_text(json.dumps({"sheet": str(sheet), "rows": a.rows, "columns": a.columns, "cell": [cw, ch], "frames": frames}, indent=2)+"\n", encoding="utf-8")
    print(out); return 0


if __name__ == "__main__": raise SystemExit(main())
