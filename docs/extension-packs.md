# Extension Packs

Extension packs are optional skill bundles for specific tools, platforms, or deployment environments.

The core `auto-automl` skills must remain tooling-neutral. They define the experiment loop, leakage gates, metric review, and memory distillation without assuming a tracking system, cloud runtime, model registry, or deployment platform.

Core also does not include runner or sandbox orchestration. Those capabilities are expected from the host agent application. Extension packs may add adapters for a host or platform, but should not replace the core loop contracts.

## Activation Rule

Use an extension pack only when one of these is true:

- The user explicitly asks for that stack.
- The existing project already uses that stack.
- The task cannot be completed without choosing a tool, and the user has accepted the choice.

Do not introduce tool-specific guidance merely because it could be useful.

## Candidate Pack: Databricks + MLflow 3

A future Databricks + MLflow 3 pack could include skills for:

- experiment tracking conventions
- model registry and lineage checks
- deployment-readiness review
- batch/online inference validation
- Databricks job/notebook packaging
- platform-specific leakage and data access checks
- release-gated final holdout evaluation

This pack should not be loaded by default. It should be opt-in and should preserve the same core contracts:

- no final holdout access during model search
- fold-safe preprocessing
- reproducible manifests
- blocking leakage audit
- blocking metric review

## Pack Design Rules

- Keep each pack in its own directory or clearly named skill files.
- Make trigger conditions explicit in the pack's README or skill metadata.
- Do not duplicate core AutoML safety rules unless the pack adds platform-specific enforcement.
- Prefer adapters over replacements: extension packs should add execution and deployment details, not redefine the core loop.
- Include version-sensitive guidance only when it is verified against current official documentation.
