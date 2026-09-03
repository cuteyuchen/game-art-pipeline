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
4. Assemble runtime sheet/atlas deterministically when the engine needs one.
5. Build engine-neutral timing/frame metadata with `scripts/build_animation_manifest.py`.
6. Produce contact-sheet and animated-preview QA when possible.
7. Start engine integration from the accepted final frames; do not regenerate actions because an engine adapter failed.

For engine integration, preserve one authoritative `animations.json` contract containing frame order, per-frame timing, and loop semantics. Engine-specific AnimationClips, state machines, or runtime sequence components must implement that contract rather than inventing new timing.

When Cocos Creator is the target, load `references/cocos-creator.md`. Use its capability tiers: native AnimationClip authoring first, Editor/scene script authoring second, and the bundled runtime sprite-sequence fallback third.

Do not accept geometry-valid sheets with inconsistent identity or unreadable motion.
