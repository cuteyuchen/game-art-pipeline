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
```

`request.json` describes stable intent: schema version, asset id/type, description, canonical policy, source references and roles, engine target, and notes.

`manifest.json` records actual execution state: status, canonical selection/approval, generation provenance, deterministic processing, final runtime assets, QA evidence/warnings, and engine adapter/readback.

Provenance rules:

- Copy selected generator outputs into `generated/` before downstream use.
- Hash selected source files after copying.
- Never record script-drawn pixels as generated art.
- Start a new run if identity or delivery requirements change materially.
- Do not leave final project-referenced art only in temporary generator caches.
