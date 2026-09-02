#!/usr/bin/env python3
"""Validate a game-art-pipeline run contract for a requested lifecycle phase."""

from __future__ import annotations
import argparse, json
from pathlib import Path
PHASES=("prepared","generated","final","integrated")


def read_json(path:Path)->dict:
    try:return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:raise ValueError(f"invalid JSON {path}: {exc}") from exc


def main()->int:
    p=argparse.ArgumentParser();p.add_argument("run_dir");p.add_argument("--phase",choices=PHASES,default="prepared");p.add_argument("--json-output",default=None);a=p.parse_args()
    run=Path(a.run_dir).resolve();errors=[];warnings=[]
    if not run.is_dir():errors.append(f"missing run directory: {run}")
    else:
        for name in ("request.json","manifest.json"):
            if not (run/name).is_file():errors.append(f"missing {name}")
        for name in ("prompts","references","generated","processed","final","qa"):
            if not (run/name).is_dir():errors.append(f"missing directory: {name}")
    request=manifest=None
    if not errors:
        try:request=read_json(run/"request.json");manifest=read_json(run/"manifest.json")
        except ValueError as exc:errors.append(str(exc))
    if request and manifest:
        if request.get("asset_id")!=manifest.get("asset_id"):errors.append("asset_id mismatch between request and manifest")
        if a.phase in {"generated","final","integrated"} and request.get("canonical_policy")=="required":
            canonical=manifest.get("canonical",{})
            if not canonical.get("path"):errors.append("canonical asset required but manifest canonical.path is empty")
            if not canonical.get("approved"):errors.append("canonical asset required but not approved")
        if a.phase in {"generated","final","integrated"} and not manifest.get("generations"):errors.append("no generation provenance recorded")
        if a.phase in {"final","integrated"}:
            finals=manifest.get("final_assets",[])
            if not finals:errors.append("no final_assets recorded")
            for item in finals:
                value=item.get("path") if isinstance(item,dict) else item
                if not value:errors.append("final asset entry missing path");continue
                fp=Path(value);fp=fp if fp.is_absolute() else run/fp
                if not fp.exists():errors.append(f"final asset missing: {fp}")
        if a.phase=="integrated":
            engine=manifest.get("engine",{})
            if not engine.get("adapter"):errors.append("engine adapter not recorded")
            if not engine.get("imports"):errors.append("no engine imports recorded")
            if not engine.get("readback"):warnings.append("engine readback evidence is empty")
    report={"run":str(run),"phase":a.phase,"ok":not errors,"errors":errors,"warnings":warnings};text=json.dumps(report,ensure_ascii=False,indent=2);print(text)
    if a.json_output:
        out=Path(a.json_output).resolve();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text+"\n",encoding="utf-8")
    return 1 if errors else 0


if __name__=="__main__":raise SystemExit(main())
