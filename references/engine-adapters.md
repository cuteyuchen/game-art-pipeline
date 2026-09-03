# Engine Adapters

An engine adapter should support the following conceptual operations when tooling allows:

```text
inspect_project()
import_asset(file, target_path)
read_back_asset(target_path)
resolve_runtime_subassets(asset)
create_or_update_runtime_object(asset_contract)
create_or_update_animation(animation_contract)
validate_dependencies(target)
capture_preview(target)
read_back(target)
```

The reusable skill must not assume a particular engine. Resolve the adapter from `.game-art/profile.json` and existing project tooling.

## Integration journal

Before live engine mutation, create or resume `<run>/engine-handoff.json` with `scripts/engine_handoff.py`. Treat it as the durable integration journal rather than relying on one long tool session.

Rules:

- Make integration idempotent: re-running a completed step must not duplicate assets, nodes, Prefabs, or clips.
- Treat timeouts as unknown outcome until readback proves success or failure.
- Retry only incomplete work.
- Record imported asset ids/UUIDs, runtime subasset ids, animation strategy, runtime object, and preview evidence.
- Do not regenerate accepted art to fix an engine-side timeout.

## Cocos Creator

When the engine type is `cocos-creator`, load `references/cocos-creator.md` and follow it in addition to these rules.

High-level requirements:

1. Inspect the project for an existing Cocos MCP/editor extension before installing anything new.
2. Prefer live editor/AssetDB/MCP import and mutation tools over direct manipulation of generated metadata.
3. Do not guess UUIDs or hand-write `.meta`, `.scene`, `.prefab`, or AnimationClip internals when a safe Editor route exists.
4. Import large frame sets in bounded batches or one directory refresh followed by per-file readback; avoid a single long blocking call.
5. Resolve imported SpriteFrame subassets through readback before animation wiring.
6. If dedicated AnimationClip authoring is missing, fall back to an Editor/scene script bridge; if that is still unavailable, use the bundled runtime sprite-sequence component when the project permits it.
7. Capture an Editor or Preview screenshot and retain it as engine-side QA evidence.
8. Keep pilot/test assets isolated from production scene lists until accepted.

Do not hard-code a specific Cocos MCP server name or port.

## Engine-Neutral Fallback

When no live adapter is available, deliver final image/atlas files, manifest/provenance, pivot/anchor information, animation timing/frame rectangles where applicable, UI slice metadata where applicable, and a precise handoff contract. If the user explicitly requested engine integration, mark the result `PARTIAL` until engine-side readback occurs.

If `engine.instructions_file` is configured, load it as the project-specific adapter contract instead of changing this reusable skill.
