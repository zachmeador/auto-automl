# Extension Packs

Extension packs are optional skill bundles for specific tools, platforms, or deployment environments.

The core `auto-automl` skills must remain tooling-neutral. They define the project card, frontier loop, and review checklists without assuming a tracking system, cloud runtime, or deployment platform.

Core also does not include runner or sandbox orchestration. Those capabilities are expected from the host agent application. Extension packs may add adapters for a host or platform, but should not replace the core project card and frontier loop.

## Activation Rule

Use an extension pack only when one of these is true:

- The user explicitly asks for that stack.
- The existing project already uses that stack.
- The task cannot be completed without choosing a tool, and the user has accepted the choice.

Do not introduce tool-specific guidance merely because it could be useful.

## Pack Design Rules

- Keep each pack in its own directory or clearly named skill files.
- Make trigger conditions explicit in the pack's README or skill metadata.
- Do not duplicate core AutoML safety rules unless the pack adds platform-specific enforcement.
- Prefer adapters over replacements: extension packs should add execution and deployment details, not redefine the core loop.
- Include version-sensitive guidance only when it is verified against current official documentation.
