---
name: game-art-pipeline
description: "Produce, validate, package, and optionally integrate reusable 2D game art through a project-configurable pipeline. Use when Codex or ChatGPT needs to create or update game sprites, animated sprites, UI sprites, effects, modular or layered 2D assets, sprite sheets, atlases, or engine-ready art from text and visual references; when it must preserve a canonical visual identity across derived assets; or when generated art must be imported into a game engine and verified with deterministic QA. The skill is project-agnostic: read the target project .game-art/profile.json and art-direction files instead of hard-coding a game camera, palette, generator, paths, or engine."
---

# Game Art Pipeline

## Overview

Run a reusable art-production pipeline that separates creative image generation from deterministic processing, QA, packaging, and engine integration. Keep project-specific style, camera, paths, generator choice, and engine rules in the target project's `.game-art/` profile rather than in this skill.

## Core Rules

- Treat generated pixels and deterministic processing as separate stages.
- Use a real image-generation capability for requested art. Never substitute PIL, Canvas, SVG, HTML/CSS, primitives, or procedural drawing for final creative art.
- Use scripts only for deterministic work such as manifests, validation, background cleanup, alignment, slicing, contact sheets, hashing, and packaging.
- Preserve provenance: record generator/tool, model when known, prompt file, source references, selected source file, processing steps, and final files.
- Prefer a canonical reference before generating identity-sensitive derivatives.
- Generate the smallest coherent visual unit. Do not ask an image model to invent a large mixed-action atlas, a full UI system, or unrelated variants in one image when those parts require consistency.
- Reuse accepted source art for variants and edits. Do not independently redesign layers that must align in-engine.
- Respect the target project's existing dirty files and engine-generated metadata. Do not reset, clean, mass-restore, or overwrite unrelated work.
- Treat deterministic checks as necessary but not sufficient. Perform visual QA on contact sheets or engine previews before calling an asset final.

## Project Discovery

1. Inspect repository instructions, engine settings, and existing asset conventions.
2. Look for `.game-art/profile.json` at the project root.
3. If it exists, treat it as the machine-readable project contract and load referenced art-direction files.
4. If it does not exist, infer a run-local profile for one-off work or initialize one with `scripts/init_project.py` for repeat use.
5. Never bake inferred project-specific values back into this skill.

Read `references/project-profile.md` for the profile schema and inheritance rules.

## Workflow

1. Classify the asset as `static-sprite`, `animated-sprite`, `ui`, or `fx`. Treat modular/layered assets as `static-sprite` with a composition contract.
2. Resolve the project contract from `.game-art/profile.json` and referenced files.
3. Resolve generation capability using `references/generator-adapters.md`. Stop with `BLOCKED` if no real generation path exists.
4. Create an isolated asset run with `scripts/prepare_run.py`.
5. Establish or reuse a canonical reference for identity-sensitive art. Respect the project's canonical approval gate.
6. Generate coherent derivatives using the task reference: `static-sprite.md`, `animated-sprite.md`, `ui.md`, or `fx.md`.
7. Process accepted art deterministically: alpha/chroma cleanup, alignment, normalization, slicing, atlas assembly, or metadata only as needed.
8. Validate with `scripts/validate_image.py`, contact sheets when useful, `scripts/validate_run.py`, and `references/qa.md`.
9. Integrate into the target engine when requested using `references/engine-adapters.md`. Prefer live Editor/MCP/official import paths over hand-authored engine metadata.
10. Finalize the manifest and report canonical source, generated sources, runtime assets, QA evidence, engine readback, warnings, and remaining gates.

## Canonical Reference Gate

Require a canonical base whenever identity or exact alignment must persist across outputs, including characters across actions/directions, modular turrets or equipment, UI state families, and layered assets that share a pivot.

For layered assets, keep the same virtual canvas, pivot, camera, scale, and orientation across layers. Prefer edit/remove operations from the accepted canonical image over independent text-to-image generation of each layer.

## Generator Boundary

The generator adapter owns creative pixels. This skill owns orchestration and contracts. Accept an installed image-generation skill/tool, project-configured generator, or explicitly configured external service. Never store API keys in prompts, scripts, manifests, command arguments, logs, or repository files.

Record adapter/tool, model when known, prompt path, reference roles, selected source path, timestamp, and source hash.

## Engine Boundary

The pipeline must remain useful without an engine adapter. If live integration is unavailable, finish with engine-neutral PNG/WebP/atlas/manifest outputs and an exact handoff contract.

For Cocos Creator, prefer an existing project MCP/editor extension or AssetDB workflow. Do not guess UUIDs or hand-author `.meta`, `.prefab`, or `.scene` internals when a safe editor path is available.

## Run Artifacts

Default run shape:

```text
.game-art/runs/<asset-id>/<run-id>/
  request.json
  manifest.json
  prompts/
  references/
  generated/
  processed/
  final/
  qa/
```

Do not leave final project-referenced art only in a generator cache or temporary directory.

## Scripts

- `scripts/init_project.py` — initialize a reusable `.game-art/` project profile without overwriting existing files by default.
- `scripts/prepare_run.py` — create a deterministic run folder and initial contracts.
- `scripts/record_generation.py` — copy a selected real generator output into the run and record provenance.
- `scripts/approve_canonical.py` — mark an existing run image as the approved canonical reference.
- `scripts/process_sprite.py` — deterministic alpha/chroma cleanup and optional canvas normalization; requires Pillow.
- `scripts/slice_grid.py` — slice equal-cell sprite grids and write frame metadata; requires Pillow.
- `scripts/record_final_asset.py` — copy a runtime-ready asset into `final/` and register it.
- `scripts/validate_image.py` — inspect image dimensions, format, alpha information, and SHA-256.
- `scripts/build_contact_sheet.py` — assemble labeled QA contact sheets; requires Pillow.
- `scripts/validate_run.py` — validate run contracts and required files for a lifecycle phase.

## Completion States

Report `PASS`, `PARTIAL`, or `BLOCKED`. Do not label a run `PASS` merely because an image was generated. `PASS` requires requested final assets, deterministic QA, visual QA, and requested engine integration/readback when applicable.
