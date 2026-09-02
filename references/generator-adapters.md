# Generator Adapters

A generator adapter turns a prompt plus optional visual references into a real image file that can be copied into an asset run.

Conceptual contract:

```text
generate(prompt, references, output_intent) -> selected_image_file
```

Selection order:

1. Use the project profile's preferred generator when available and authorized.
2. Otherwise prefer a native runtime image-generation capability.
3. Otherwise use an already-configured project generator or explicitly authorized external service.
4. If no real generation path exists, return `BLOCKED` instead of creating procedural placeholder art.

Prompt rules:

- Keep project style/camera constraints compact and task-relevant.
- State reference roles explicitly: identity, style, camera, pose, layout, edit target, or material.
- Ground derivatives on the accepted canonical reference whenever identity must persist.
- Do not ask for mixed sheets of unrelated assets merely to reduce calls.
- Keep API keys out of prompts, scripts, manifests, screenshots, and repository files.
