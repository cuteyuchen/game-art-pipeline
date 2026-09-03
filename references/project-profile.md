# Project Profile

Keep project-specific art direction and integration settings outside the reusable skill. Default path: `.game-art/profile.json` relative to the target project root.

Recommended shape:

```json
{
  "schema_version": 1,
  "project": {"name": "example-game"},
  "engine": {
    "type": "cocos-creator",
    "version": "3.8.8",
    "adapter": "auto",
    "instructions_file": null,
    "options": {}
  },
  "generation": {"preferred": "auto", "fallbacks": []},
  "art_direction": {"style_file": ".game-art/style.md", "camera_file": null, "additional_files": []},
  "paths": {"runs": ".game-art/runs", "source_assets": ".game-art/source", "runtime_assets": "assets"},
  "defaults": {"format": "png", "background": "transparent"},
  "review": {"canonical_gate": true, "visual_qa": true, "engine_preview_gate": true}
}
```

Rules:

- Resolve relative paths from project root.
- `engine.adapter: auto` means inspect existing tooling and use the safest live editor/import path.
- `engine.instructions_file` may point to a project-specific adapter contract.
- `engine.options` is an engine-specific free-form object. Do not make the reusable schema depend on one engine's knobs.
- `generation.preferred: auto` means use the best available real image-generation tool.
- Load only art-direction files relevant to the current asset type.
- `review.canonical_gate` requires an accepted canonical reference before identity-sensitive derivatives.
- `review.visual_qa` requires contact-sheet, animation-preview, or equivalent visual review.
- `review.engine_preview_gate` requires engine-side verification when integration was requested and tooling supports it.

For Cocos Creator, `references/cocos-creator.md` recognizes optional `engine.options` values such as:

```json
{
  "assetdb_batch_size": 4,
  "assetdb_timeout_seconds": 30,
  "assetdb_max_retries": 2,
  "animation_strategy": "auto",
  "allow_runtime_sequence_fallback": true,
  "crowd_preview_instances": 30
}
```

These values are defaults/tuning hints only. Existing project instructions and explicit user requirements have higher priority.

Precedence: explicit user instruction → asset request → project profile → nearby project conventions → skill defaults.
