# QA Rules

## Deterministic QA

Check at minimum:

- selected source exists;
- final file exists and is readable;
- width/height are positive and within project limits;
- alpha/background policy matches the contract;
- SHA-256 is recorded;
- expected frame/crop counts match metadata;
- unused atlas cells are transparent when required;
- run-manifest paths resolve;
- engine references/dependencies resolve after integration when tooling supports it.

Use `scripts/validate_image.py` and `scripts/validate_run.py` where applicable.

## Visual QA

Inspect the smallest useful artifact: canonical image, contact sheet, animated preview, composed-layer preview, or engine screenshot.

Evaluate style/camera compliance, identity consistency, silhouette readability, stable scale/pivot, absence of unwanted text/background/scenery/artifacts, clipping/cell contamination, correct state/action semantics, correct module composition, and runtime readability.

## Repair Scope

Repair the smallest failing scope. Regenerate one action, direction, state, module, or component family rather than discarding accepted work.

Never relax a hard geometry, alpha, anchor, or identity contract merely to make validation pass without explicit approval.
