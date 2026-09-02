# Animated Sprites

Create an animation plan before generation. Each action should define id, purpose, frame count, timing, loop flag, direction/view when relevant, root/anchor policy, and optional mirror policy.

Generation rules:

- Establish one canonical identity reference first.
- Generate one coherent action family at a time.
- Prefer compact grids for body animation when long rows would cause drift/cropping.
- Keep identity, camera distance, silhouette scale, equipment, and material language stable across actions.
- Separate detached FX, projectiles, muzzle flashes, impact bursts, and long trails from body animation unless the runtime intentionally combines them.

After visual generation passes:

1. Extract frames deterministically.
2. Normalize alpha/background.
3. Align frames to the chosen anchor.
4. Assemble runtime sheet/atlas deterministically.
5. Write timing/frame metadata.
6. Produce contact-sheet and animated-preview QA when possible.

Do not accept geometry-valid sheets with inconsistent identity or unreadable motion.
