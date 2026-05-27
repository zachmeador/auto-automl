# Agent Instructions

This repo defines portable markdown skills for Ralph-style AutoML loops.

## Operating Rules

- Keep skills plain markdown and runtime agnostic unless the user asks for a specific harness.
- Do not build an always-on shell runner, Docker sandbox layer, or IDE control plane into core. Assume host agent environments provide execution and isolation.
- Keep the core loop tooling-neutral. Do not recommend Databricks, MLflow, AutoGluon, Optuna, cloud services, or deployment platforms unless explicitly requested or already present in the user's project.
- Put tool-specific instructions in optional extension packs.
- Prefer structured contracts and deterministic checks over prose-only instructions.
- Preserve the sealed final holdout boundary. Normal experiment loops may optimize validation metrics only.
- Treat leakage audits and metric reviews as blocking gates, not advisory notes.
- Write task-specific ML project code under `projects/<project_id>/`; do not place generated project code at the repository root.
- Keep generated experiment state under `experiments/runs/<run_id>/`.
- Keep durable, compact memory in structured records rather than long logs.

## AutoML Safety Rules

- Split before preprocessing.
- Fit transformers, encoders, imputers, scalers, feature selectors, oversamplers, and target encoders only on training folds.
- Use group-aware or time-aware splits when the prediction setting requires them.
- Do not query final test metrics during model search.
- Record every trial that influences future decisions.

## File Conventions

- `skills/*.md` are reusable agent skills.
- `schemas/*.schema.json` define structured records that tools and agents should honor.
- `experiments/README.md` documents run layout and registry expectations.
- `projects/README.md` documents child project workspaces.
- `docs/research/` stores supporting research notes.
- `docs/extension-packs.md` defines when tool-specific packs are appropriate.
