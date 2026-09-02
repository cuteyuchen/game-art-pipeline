# UI Sprite Production

Treat reusable UI art as components, not full-page screenshots, unless the deliverable is explicitly a static mockup.

Examples: buttons, panels, modal frames, title bars, resource/HP bars, cards, toggles, icons, and decorative separators.

Rules:

- Establish one canonical geometry per component family.
- Derive hover/pressed/disabled/selected states from the same geometry.
- Keep text out of sprites by default so the engine can render localized program text.
- Preserve clean stretchable center regions on buttons and panels.
- Record 9-slice/stretch zones in metadata when the target engine uses them.
- For multiple components, generate coherent groups, validate the group/atlas, slice mechanically from verified bounds/maps, then export transparent PNGs plus metadata.
- Do not treat a presentation-style UI master board as exact runtime slicing truth unless it was intentionally created with a verified crop/layout contract.
