#!/usr/bin/env python3
"""Deterministically clean alpha/chroma background and optionally normalize a sprite canvas. Requires Pillow."""

from __future__ import annotations
import argparse
from collections import deque
from pathlib import Path


def parse_hex(value: str):
    value = value.strip().lstrip("#")
    if len(value) != 6: raise argparse.ArgumentTypeError("color must be RRGGBB")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))


def parse_size(value: str):
    try: w, h = value.lower().split("x", 1); result = (int(w), int(h))
    except Exception as exc: raise argparse.ArgumentTypeError("canvas must be WIDTHxHEIGHT") from exc
    if min(result) < 1: raise argparse.ArgumentTypeError("canvas dimensions must be positive")
    return result


def near(rgb, key, tol): return max(abs(rgb[i] - key[i]) for i in range(3)) <= tol


def clear_border_connected(im, key, tol):
    px, (w, h), q, seen = im.load(), im.size, deque(), set()
    for x in range(w): q.extend(((x, 0), (x, h - 1)))
    for y in range(h): q.extend(((0, y), (w - 1, y)))
    while q:
        x, y = q.popleft()
        if (x, y) in seen: continue
        seen.add((x, y))
        r, g, b, a = px[x, y]
        if a == 0 or near((r, g, b), key, tol):
            px[x, y] = (0, 0, 0, 0)
            if x > 0: q.append((x - 1, y))
            if x + 1 < w: q.append((x + 1, y))
            if y > 0: q.append((x, y - 1))
            if y + 1 < h: q.append((x, y + 1))


def place_on_canvas(im, size, anchor):
    from PIL import Image
    w, h = size
    if im.width > w or im.height > h: raise SystemExit(f"sprite {im.size} does not fit canvas {size}")
    if anchor == "center": x, y = (w - im.width)//2, (h - im.height)//2
    elif anchor == "bottom-center": x, y = (w - im.width)//2, h - im.height
    else: x, y = 0, 0
    out = Image.new("RGBA", size, (0, 0, 0, 0)); out.alpha_composite(im, (x, y)); return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--bg-color", type=parse_hex, default=None)
    p.add_argument("--bg-tolerance", type=int, default=18)
    p.add_argument("--trim", action="store_true")
    p.add_argument("--canvas", type=parse_size, default=None)
    p.add_argument("--anchor", choices=("center", "bottom-center", "top-left"), default="center")
    a = p.parse_args()
    if not 0 <= a.bg_tolerance <= 255: raise SystemExit("bg tolerance must be 0..255")
    try: from PIL import Image
    except Exception as exc: raise SystemExit(f"Pillow is required: {exc}")
    src, out = Path(a.input).resolve(), Path(a.output).resolve()
    if not src.is_file(): raise SystemExit(f"missing input: {src}")
    with Image.open(src) as original: im = original.convert("RGBA")
    if a.bg_color is not None: clear_border_connected(im, a.bg_color, a.bg_tolerance)
    im = Image.alpha_composite(Image.new("RGBA", im.size, (0,0,0,0)), im)
    if a.trim:
        bbox = im.getbbox()
        if bbox: im = im.crop(bbox)
    if a.canvas: im = place_on_canvas(im, a.canvas, a.anchor)
    out.parent.mkdir(parents=True, exist_ok=True); im.save(out, "PNG"); print(out); return 0


if __name__ == "__main__": raise SystemExit(main())
