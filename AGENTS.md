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
- Keep all task-specific work under `projects/<project_id>/`: source code, configs, notebooks, data splits, outputs, contracts, registries, memory, run metadata, environment files, and local scripts.
- Do not place project-specific code or artifacts at the repository root or in root-level `experiments/runs/`.
- For Python experiments, use project-local `uv`: create or reuse `projects/<project_id>/pyproject.toml`, run from the child project directory, and prefer `uv --cache-dir .uv-cache run <command>` over bare `python`, `python3`, `pip`, or global environments.
- Prefer `pyproject.toml` scripts for repeatable experiment commands.
- Keep `.venv/`, `.uv-cache/`, and `uv.lock` project-local.
- Keep durable, compact memory in structured records rather than long logs.

## How To Execute The Loop

The AutoML loop has two levels:

- **Worker iteration**: one fresh-context agent session executes one bounded experiment, audits it, records it, distills it, and reports status.
- **Application loop**: the host agent environment repeats worker iterations until the project stop policy is satisfied.

Do not treat a host application's "active goal" or the current chat request as the project stop policy. The project stop policy lives in `projects/<project_id>/experiments/metric_contract.md`.

When asked to run, continue, or execute the AutoML loop, follow this path:

1. Read this file, `README.md`, and `projects/README.md`.
2. Identify or create the child project workspace: `projects/<project_id>/`.
3. Read or create the project contracts:
   - `projects/<project_id>/experiments/dataset_contract.md`
   - `projects/<project_id>/experiments/split_contract.md`
   - `projects/<project_id>/experiments/metric_contract.md`
4. Read the project state if present:
   - `projects/<project_id>/experiments/registry.jsonl`
   - `projects/<project_id>/experiments/memory.jsonl`
5. Check the stop policy in `projects/<project_id>/experiments/metric_contract.md`.
6. If a stop condition is already satisfied, do not start a new experiment. Report the stopping reason and current best admitted run.
7. If no stop condition is satisfied, execute one worker iteration using `skills/automl-loop.md`.
8. Apply the verification gates using:
   - `skills/leakage-auditor.md`
   - `skills/metric-reviewer.md`
9. Distill the result using `skills/experiment-distiller.md`.
10. Re-check the stop policy.
11. Report the iteration result, whether the application loop should continue, and the next recommended hypothesis if continuing.

If the host environment is running an always-on Ralph loop, it may invoke a new fresh-context worker iteration after step 11 when the stop policy says to continue. If the current session is just one worker invocation, stop after step 11 so the host loop can decide whether to launch the next worker.

## AutoML Safety Rules

- Split before preprocessing.
- Fit transformers, encoders, imputers, scalers, feature selectors, oversamplers, and target encoders only on training folds.
- Use group-aware or time-aware splits when the prediction setting requires them.
- Do not query final test metrics during model search.
- Record every trial that influences future decisions.

## File Conventions

- `skills/*.md` are reusable agent skills.
- `schemas/*.schema.json` define structured records that tools and agents should honor.
- `experiments/README.md` documents reusable templates and root-level experiment constraints.
- `projects/README.md` documents child project workspaces.
- `docs/research/` stores supporting research notes.
- `docs/extension-packs.md` defines when tool-specific packs are appropriate.
