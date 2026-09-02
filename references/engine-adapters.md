# Engine Adapters

An engine adapter should support the following conceptual operations when tooling allows:

```text
inspect_project()
import_asset(file, target_path)
create_or_update_runtime_object(asset_contract)
create_or_update_animation(animation_contract)
validate_dependencies(target)
capture_preview(target)
read_back(target)
```

The reusable skill must not assume a particular engine. Resolve the adapter from `.game-art/profile.json` and existing project tooling.

## Cocos Creator

1. Inspect the project for an existing Cocos MCP/editor extension before installing anything new.
2. Prefer live editor/AssetDB/MCP import and mutation tools over direct manipulation of generated metadata.
3. Do not guess UUIDs or hand-write `.meta`, `.scene`, or `.prefab` internals when a safe Editor route exists.
4. After import, read back the asset/SpriteFrame/Prefab or scene node to prove references resolved.
5. Create/update SpriteFrames, AnimationClips, Prefabs, and scene nodes through the safest available project route.
6. Capture an Editor or Preview screenshot when available and retain it as engine-side QA evidence.
7. Keep pilot/test assets isolated from production scene lists until accepted.

Do not hard-code a specific Cocos MCP server name or port.

## Engine-Neutral Fallback

When no live adapter is available, deliver final image/atlas files, manifest/provenance, pivot/anchor information, animation timing/frame rectangles where applicable, UI slice metadata where applicable, and a precise handoff contract. If the user explicitly requested engine integration, mark the result `PARTIAL` until engine-side readback occurs.

If `engine.instructions_file` is configured, load it as the project-specific adapter contract instead of changing this reusable skill.
