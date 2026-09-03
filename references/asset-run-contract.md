# Asset Run Contract

Use one isolated run per asset attempt:

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
  animations.json        # optional, animated-sprite timing/frame contract
  engine-handoff.json    # optional until live engine integration begins
```

`request.json` describes stable intent: schema version, asset id/type, description, canonical policy, source references and roles, engine target, and notes.

`manifest.json` records actual execution state: status, canonical selection/approval, generation provenance, deterministic processing, final runtime assets, QA evidence/warnings, and summarized engine adapter/readback.

`engine-handoff.json` is the resumable live-integration journal. It records exact import targets, attempts/timeouts, engine ids/UUIDs, SpriteFrame or equivalent subasset readback, animation strategy, runtime object, and preview evidence. Keep detailed retries here rather than bloating `manifest.json`.

Provenance rules:

- Copy selected generator outputs into `generated/` before downstream use.
- Hash selected source files after copying.
- Never record script-drawn pixels as generated art.
- Start a new run if identity or delivery requirements change materially.
- Do not start a new art run merely because the engine handoff timed out; resume the existing handoff.
- Do not leave final project-referenced art only in temporary generator caches.
