# Cocos Creator Adapter

## Contents

1. Purpose
2. Capability discovery
3. Resumable handoff contract
4. AssetDB import strategy
5. SpriteFrame discovery
6. Animation integration tiers
7. Prefab and scene integration
8. Preview and crowd QA
9. Recovery after timeouts
10. Completion criteria

## Purpose

Use this adapter when `.game-art/profile.json` declares `engine.type: "cocos-creator"`. Keep it independent of a specific MCP server, port, package name, or Creator project layout. Prefer whatever live Editor/MCP integration the project already has before installing new tooling.

The adapter must be resumable. A transient AssetDB or MCP timeout must not force art regeneration or a new asset run.

## Capability discovery

Before mutating the project, inspect the current Cocos tooling and classify the available integration tier.

### Tier A — dedicated engine tools

Use dedicated asset, SpriteFrame, AnimationClip, Prefab, scene, preview, and readback tools when all required operations are exposed and reliable.

### Tier B — Editor/scene script bridge

If dedicated tools are incomplete but the existing MCP/editor extension can execute trusted JavaScript in Creator's editor or scene context, use that bridge for missing operations. Prefer official Creator APIs and AssetDB messages. Do not bypass the editor by hand-authoring `.meta`, `.prefab`, `.scene`, or AnimationClip serialization.

### Tier C — runtime sprite-sequence fallback

If AnimationClip authoring/keyframe tools are unavailable, but assets can be imported and SpriteFrame references can be resolved/assigned, use the reusable fallback component in `assets/cocos-creator/GameArtSpriteSequenceAnimator.ts`.

Copy the component into a project-owned script path, wire actual SpriteFrame assets into its serialized clip arrays through the Editor/MCP/script bridge, and save the test/runtime Prefab through Creator. Do not embed guessed UUIDs into source code.

Tier C is a fallback for animation authoring only. It does not waive asset import, SpriteFrame readback, Prefab readback, or preview QA.

If none of these tiers can produce engine-side readback, finish the art run engine-neutrally and report `PARTIAL`.

## Resumable handoff contract

Before engine mutations, initialize or reuse:

```text
<run>/engine-handoff.json
```

Use:

```bash
python scripts/engine_handoff.py init <run> \
  --engine-type cocos-creator \
  --adapter auto \
  --from-final-assets \
  --target-root <project asset target>
```

The handoff file is the integration journal. It records each source/target pair, import attempts, asset UUID, SpriteFrame UUID, animation strategy, runtime object, preview evidence, and retry policy.

Never restart generation because engine integration timed out. Resume from the first incomplete handoff item.

Recommended Cocos defaults unless the project profile overrides them:

```text
import batch size: 2-4 images
per-batch readback timeout: 30 seconds
max retries per failed batch: 2
animation strategy: auto
runtime sequence fallback: allowed
crowd preview: 30 instances for small enemies, adjusted to project scale
```

Project-specific overrides may live under `engine.options` in `.game-art/profile.json`:

```json
{
  "engine": {
    "type": "cocos-creator",
    "adapter": "auto",
    "options": {
      "assetdb_batch_size": 4,
      "assetdb_timeout_seconds": 30,
      "assetdb_max_retries": 2,
      "animation_strategy": "auto",
      "allow_runtime_sequence_fallback": true,
      "crowd_preview_instances": 30
    }
  }
}
```

Treat these as tuning knobs, not hard requirements.

## AssetDB import strategy

Do not block on one giant import call for a large frame set.

1. Copy only accepted `final/` files into the project runtime asset target.
2. Ask the existing Editor/AssetDB integration to refresh/import the smallest useful directory or a batch of 2-4 files.
3. Poll asset readback after the import request instead of waiting on a single long tool call.
4. Record each file immediately after successful readback:

```bash
python scripts/engine_handoff.py record-import <run> \
  --source final/move-000.png \
  --target assets/art/enemy/normal/move-000.png \
  --status imported \
  --asset-uuid <texture-or-image-uuid> \
  --spriteframe-uuid <spriteframe-uuid>
```

5. Continue with the next batch only after the current batch has read back successfully.
6. On timeout, verify MCP/editor health, re-query the target path, and retry only unresolved files. Do not duplicate copies or clear AssetDB state.

A tool timeout does not prove import failure. Always query the target path again before retrying.

For many files, prefer one directory refresh plus per-file readback when that is more reliable than repeated import calls.

## SpriteFrame discovery

A normal Cocos image import commonly creates an image/texture asset and a SpriteFrame subasset. Do not conclude that SpriteFrame integration is impossible merely because the MCP lacks a tool named `create_spriteframe`.

After image import:

1. Inspect/query the imported image asset.
2. Inspect its subassets, dependencies, or asset info through the available tool/API.
3. Resolve the generated SpriteFrame UUID/path.
4. Read the SpriteFrame back before recording the import as complete.
5. Store both the parent asset UUID and SpriteFrame UUID in `engine-handoff.json`.

If the current importer settings do not produce a SpriteFrame, use the Editor/AssetDB path to configure/reimport the texture. Do not hand-write the `.meta` file.

For animated sprites, integration is incomplete until every expected frame has a resolved SpriteFrame reference.

## Animation integration tiers

First build an engine-neutral sequence manifest from the accepted frames:

```bash
python scripts/build_animation_manifest.py <animation-plan.json> \
  --frames-root <run>/final \
  --output <run>/animations.json
```

This file is the authoritative frame order, timing, and loop contract regardless of the Cocos implementation strategy.

### Tier A — native AnimationClip authoring

Use native/dedicated tools if they can create or edit an AnimationClip and keyframe the target `Sprite.spriteFrame` property.

For each animation:

- use exact frame order from `animations.json`;
- derive key times from cumulative `durations_ms`;
- set loop/wrap semantics from the manifest;
- save the AnimationClip through Creator;
- attach it to the target `Animation` component;
- read back clip UUID, duration, frame/key count, target property, and loop setting.

Do not accept only `add_animation_clip`/attach capability if no tool can create the actual clip asset. Fall through to Tier B or C.

### Tier B — Editor/scene script authoring

If the MCP can execute trusted Creator editor/scene scripts, use the bridge to create the same AnimationClip through Creator APIs, save it as an asset, attach it, and read it back.

Keep the script bounded to the active project and the explicit test/runtime asset paths. Do not use raw filesystem serialization for Creator asset formats.

### Tier C — `GameArtSpriteSequenceAnimator`

Use the bundled component when AnimationClip authoring is not available or is unreliable.

1. Copy `assets/cocos-creator/GameArtSpriteSequenceAnimator.ts` into a project-owned script folder, unless the project already has an equivalent sprite-sequence component.
2. Let Creator import/compile the script and confirm no new diagnostics.
3. Add `GameArtSpriteSequenceAnimator` to the test/runtime node or Prefab.
4. Set `target` to the node's Sprite component.
5. Create one serialized clip entry per animation id.
6. Assign real imported SpriteFrame assets in exact manifest order.
7. Copy exact `durations_ms` and `loop` values from `animations.json`.
8. Save through Creator and read back the component/Prefab.
9. Exercise `play(<id>)` for every required animation in preview.

This fallback is intentionally engine-side and deterministic; it does not alter the generated art.

If the project already has a compatible animator, prefer adapting to that project component over copying the bundled fallback.

Record each completed animation:

```bash
python scripts/engine_handoff.py record-animation <run> \
  --id move \
  --status ready \
  --strategy runtime-sequence \
  --frame-count 4
```

## Prefab and scene integration

Keep pilot integration isolated until accepted.

For a typical animated-sprite pilot:

1. Create/update a test Sprite node using the first approved frame.
2. Add the chosen animation implementation.
3. Save a test Prefab through Creator.
4. Read the Prefab back and verify there are no missing SpriteFrame/component references.
5. Create or reuse an isolated test scene that is not added to the production build list.
6. Instantiate the Prefab and play every required action.

Record the runtime object after readback:

```bash
python scripts/engine_handoff.py record-runtime <run> \
  --status ready \
  --path <prefab-path> \
  --uuid <prefab-uuid>
```

Do not replace production Prefabs until the relevant project review gate is satisfied.

## Preview and crowd QA

A Cocos animation pilot is not complete merely because the Prefab exists.

For small repeatable enemies or units, create an isolated crowd preview with enough simultaneous instances to reveal:

- wrong runtime scale;
- anchor jitter;
- frame switching errors;
- expensive per-frame allocations or obvious editor/runtime stalls;
- readability problems when many units overlap;
- missing assets or diagnostics that only appear during playback.

Use the project profile's `crowd_preview_instances` when provided. Otherwise start near 30 for small enemies and adapt to the project's normal concurrency.

Capture Editor or Preview evidence and read the console/diagnostics. Record it:

```bash
python scripts/engine_handoff.py record-preview <run> \
  --status pass \
  --path <qa-screenshot-or-preview-path> \
  --instances 30 \
  --console-errors 0 \
  --console-warnings 0
```

Warnings may be acceptable only when they are known pre-existing project warnings and are explicitly separated from new integration warnings.

## Recovery after timeouts

When AssetDB or MCP calls time out:

1. Stop issuing additional mutation calls.
2. Check editor/MCP health with a read-only operation.
3. Re-query the exact target paths; some timed-out mutations may already have completed.
4. Update `engine-handoff.json` for assets that actually exist.
5. Retry only unresolved files, using a smaller batch size if necessary.
6. If the adapter repeatedly times out, switch from dedicated mutation calls to the available Editor script bridge before considering a different MCP implementation.
7. Never regenerate accepted art to solve an engine timeout.

Do not wait for a single 300-second import call when shorter import + readback loops can isolate the failure.

## Completion criteria

For a Cocos animated-sprite integration, report `PASS` only when all requested conditions are satisfied:

- every runtime PNG is imported;
- every expected SpriteFrame is resolved and read back;
- every required animation is playable using AnimationClip or the documented runtime-sequence fallback;
- the test/runtime Prefab has no missing references;
- engine readback is recorded;
- preview evidence exists;
- the preview has no new console errors;
- any required crowd test passed;
- Owner/project review gates required by the profile are satisfied.

Validate the handoff before marking the run integrated:

```bash
python scripts/engine_handoff.py validate <run> \
  --require-spriteframes \
  --require-animations \
  --require-runtime \
  --require-preview

python scripts/validate_run.py <run> --phase integrated
```

If any required engine evidence is missing, keep the run `PARTIAL`. Art generation may still be fully valid; do not discard accepted art.
