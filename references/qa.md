# QA Rules

## Deterministic QA

Check at minimum:

- selected source file exists;
- final file exists and is readable;
- width/height are positive and within project limits;
- PNG alpha/background policy matches the contract;
- SHA-256 is recorded;
- expected frame count/crop count matches metadata;
- unused atlas cells are transparent when required;
- run manifest paths resolve;
- engine references/dependencies resolve after integration when tooling supports it;
- every required imported animation frame has an engine-side runtime subasset reference (for example a Cocos SpriteFrame);
- engine handoff contains no unresolved import failures before integration is declared complete.

Use `scripts/validate_image.py`, `scripts/engine_handoff.py validate`, and `scripts/validate_run.py` where applicable.

## Visual QA

Inspect the smallest useful review artifact:

- one canonical image for identity approval;
- contact sheet for variants/frames;
- animated preview for motion;
- composed-layer preview for modular assets;
- engine screenshot for final in-context verification.

Evaluate:

- style and camera compliance;
- identity consistency;
- silhouette readability at runtime size;
- stable scale and pivot/anchor;
- no unexpected text, UI, backgrounds, shadows, scenery, or detached artifacts;
- no clipping or neighboring-cell contamination;
- correct state/action semantics;
- correct module composition;
- runtime readability against the actual game background when engine preview exists.

## Engine Preview QA

When the project requires engine preview:

- verify the actual imported assets, not temporary source files;
- exercise every required animation/state at least once;
- inspect runtime scale and anchor stability;
- inspect console/diagnostics for new errors;
- for small repeatable units, use a multi-instance/crowd preview sized to the project's expected concurrency;
- preserve screenshot/readback evidence in the run and record it in `engine-handoff.json`.

A mutation timeout is not a QA failure until readback shows the mutation did not complete.

## Repair Scope

Repair the smallest failing scope. Regenerate one action, direction, state, module, or component family rather than discarding an entire accepted run.

For engine failures, repair or resume the engine handoff before considering art regeneration.

Never "fix" a failed visual by relaxing a hard geometry, alpha, anchor, or identity contract without explicit project/user approval.
