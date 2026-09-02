# Effects and Projectiles

Use this path for projectiles, muzzle flashes, impacts, explosions, elemental effects, charge effects, aura overlays, trails, and similar non-character VFX.

Rules:

- Define the effect origin/anchor explicitly: center, muzzle, impact point, ground contact, or another project socket.
- Keep effect scale readable relative to the consuming gameplay object.
- Generate loops/sequences as one coherent family.
- Avoid baked scenery, floors, UI, labels, or unrelated shadows.
- Keep body animation and detached FX separate when runtime layering improves scale, reuse, or timing.
- For looping effects, inspect the first/last-frame transition as well as static contact sheets.
- Store timing, blend intent, loop flag, and anchor metadata with final output.

FX normally does not require an identity canonical gate unless it belongs to a named effect family whose style must persist across many variants.
