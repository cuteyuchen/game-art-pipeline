# game-art-pipeline

A reusable agent Skill for producing game-ready 2D art without hard-coding one game's style, camera, generator, asset paths, or engine.

The pipeline separates four concerns:

```text
project art profile
      ↓
creative image generation
      ↓
deterministic processing + QA
      ↓
engine integration + readback
```

The repository itself is a valid `game-art-pipeline` Skill. Project-specific rules live in each game's `.game-art/` directory.

## Initial scope

- Static and modular/layered sprites
- Animated sprites and sprite sheets
- Reusable UI sprites and state families
- Projectiles and VFX
- Canonical-reference consistency gates
- Provenance manifests and deterministic QA
- Engine-neutral handoff
- Cocos Creator integration guidance through whatever safe Editor/MCP workflow the target project already exposes

The Skill deliberately does **not** hard-code Cocos, one image model, one resolution, a specific camera, or a specific art style.

## Install

Place this repository directory where your agent can discover Skills, for example a global Codex Skills directory or a project's `.codex/skills/game-art-pipeline/` directory.

## Bootstrap a game project

```bash
python scripts/init_project.py /path/to/game \
  --name my-game \
  --engine cocos-creator \
  --engine-version 3.8.8 \
  --runtime-assets game/assets \
  --generator auto
```

This creates:

```text
.game-art/
  profile.json
  style.md
  README.md
  source/
  references/
  runs/
```

Edit `.game-art/style.md` and, when useful, add camera/UI/character-family contracts referenced by `profile.json`.

## Example requests

```text
Use game-art-pipeline to create a top-down healer enemy from the current project's monster-family reference, generate idle/move/hurt/death, integrate it into the existing engine, and show me the preview QA.
```

```text
Use game-art-pipeline to create primary and secondary button sprites from this project's art profile. Keep program text separate and configure stretchable UI metadata.
```

```text
Use game-art-pipeline to create one canonical modular turret, derive aligned base/body/barrel layers from it, rebuild a composition preview, then integrate the layers into the project.
```

## Design notes

The workflow is informed by production patterns seen in canonical-reference sprite pipelines such as OpenAI's `hatch-pet` and community game-sprite workflows: generate identity-bearing art from an accepted base, keep visual jobs small and coherent, perform deterministic assembly separately, and repair the smallest failing scope.

No third-party Skill code is vendored here. This repository implements its own generic contracts and helper scripts.

## Deterministic helper flow

A typical run can use `prepare_run.py` → `record_generation.py` → `approve_canonical.py` → `process_sprite.py` / `slice_grid.py` → `record_final_asset.py` → `validate_run.py`. Creative pixels still come only from the selected image generator; these helpers manage files, provenance, cleanup, frames, and QA contracts.
