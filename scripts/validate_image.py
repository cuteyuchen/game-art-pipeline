#!/usr/bin/env python3
"""Inspect an image and emit deterministic metadata for QA."""

from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path
PNG_SIG = b"\x89PNG\r\n\x1a\n"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()


def inspect_png(path: Path) -> dict:
    with path.open("rb") as f:
        if f.read(8) != PNG_SIG: raise ValueError("not a PNG file")
        length = struct.unpack(">I", f.read(4))[0]; chunk_type = f.read(4)
        if chunk_type != b"IHDR" or length != 13: raise ValueError("invalid PNG IHDR")
        width, height, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", f.read(13))
    return {"format":"png","width":width,"height":height,"bit_depth":bit_depth,"color_type":color_type,"alpha_channel":color_type in (4,6),"interlace":interlace}


def inspect_with_pillow(path: Path):
    try: from PIL import Image
    except Exception: return None
    with Image.open(path) as im:
        result = {"format":(im.format or "unknown").lower(),"width":im.width,"height":im.height,"mode":im.mode,"alpha_channel":"A" in im.getbands() or "transparency" in im.info,"transparent_pixels_detected":None}
        if "A" in im.getbands():
            lo, hi = im.getchannel("A").getextrema(); result["transparent_pixels_detected"] = lo < 255; result["alpha_extrema"] = [lo, hi]
        return result


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("image"); p.add_argument("--json-output", default=None); p.add_argument("--require-alpha", action="store_true"); a=p.parse_args()
    path=Path(a.image).resolve()
    if not path.is_file(): raise SystemExit(f"missing image: {path}")
    info=inspect_with_pillow(path)
    if info is None:
        if path.suffix.lower() != ".png": raise SystemExit("Pillow unavailable; stdlib fallback validates PNG only")
        info=inspect_png(path); info["transparent_pixels_detected"] = None
    info.update({"path":str(path),"bytes":path.stat().st_size,"sha256":sha256(path)})
    errors=[]
    if info.get("width",0)<=0 or info.get("height",0)<=0: errors.append("non-positive dimensions")
    if a.require_alpha and not info.get("alpha_channel"): errors.append("alpha channel required but not present")
    info["errors"]=errors; text=json.dumps(info, ensure_ascii=False, indent=2); print(text)
    if a.json_output:
        out=Path(a.json_output).resolve(); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(text+"\n", encoding="utf-8")
    return 1 if errors else 0


if __name__ == "__main__": raise SystemExit(main())
