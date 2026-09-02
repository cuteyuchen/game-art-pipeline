#!/usr/bin/env python3
"""Build a labeled QA contact sheet from existing images. Requires Pillow."""

from __future__ import annotations
import argparse, math
from pathlib import Path


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("images", nargs="+"); p.add_argument("--output", required=True); p.add_argument("--columns", type=int, default=4); p.add_argument("--cell", type=int, default=256); p.add_argument("--padding", type=int, default=16); a=p.parse_args()
    if a.columns<1 or a.cell<32 or a.padding<0: raise SystemExit("invalid layout arguments")
    try: from PIL import Image, ImageDraw, ImageFont
    except Exception as exc: raise SystemExit(f"Pillow is required: {exc}")
    paths=[Path(x).resolve() for x in a.images]; missing=[str(x) for x in paths if not x.is_file()]
    if missing: raise SystemExit("missing images: "+", ".join(missing))
    label_h=28; rows=math.ceil(len(paths)/a.columns); width=a.padding+a.columns*(a.cell+a.padding); height=a.padding+rows*(a.cell+label_h+a.padding)
    sheet=Image.new("RGBA",(width,height),(32,34,38,255)); draw=ImageDraw.Draw(sheet); font=ImageFont.load_default()
    for i,path in enumerate(paths):
        col,row=i%a.columns,i//a.columns; x=a.padding+col*(a.cell+a.padding); y=a.padding+row*(a.cell+label_h+a.padding)
        with Image.open(path) as src:
            im=src.convert("RGBA"); im.thumbnail((a.cell,a.cell),Image.Resampling.LANCZOS); sheet.alpha_composite(im,(x+(a.cell-im.width)//2,y+(a.cell-im.height)//2))
        draw.rectangle((x,y+a.cell,x+a.cell,y+a.cell+label_h),fill=(245,245,245,255)); draw.text((x+6,y+a.cell+7),path.name,fill=(20,20,20,255),font=font)
    out=Path(a.output).resolve(); out.parent.mkdir(parents=True,exist_ok=True); sheet.convert("RGB").save(out,quality=92); print(out); return 0


if __name__=="__main__": raise SystemExit(main())
