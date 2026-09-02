# Static and Modular Sprites

Create one canonical base for identity-bearing static assets before variants. Preserve silhouette, camera, palette, material language, scale, and anchor unless the request explicitly changes them.

For modular/layered assets use a composition contract:

```text
canonical composite
  -> fixed/base layer
  -> rotating/body layer
  -> attachment layer
  -> overlay/module layer
  -> optional FX sockets
```

Rules:

- Keep one shared virtual canvas and pivot/origin.
- Keep orientation, camera, and scale identical across layers.
- Prefer edit/remove operations from the accepted canonical composite rather than independent redesigns.
- Rebuild a composition preview from final layers and compare it against the canonical composite.
- Preserve transparent empty canvas when anchor alignment requires it; do not independently trim layers unless compensating offsets are recorded.
- For state/material variants, change the smallest necessary region rather than fully redrawing geometry.
