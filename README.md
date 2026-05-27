# auto-automl

`auto-automl` is a portable collection of markdown agent skills for running Ralph-style AutoML loops.

The project goal is not to let an LLM freely "do machine learning." The goal is to let an agent propose and run bounded ML experiments while strict contracts protect evaluation integrity:

- immutable train/validation/test split definitions
- no normal-loop access to sealed final holdout results
- fold-safe preprocessing and feature engineering
- reproducible experiment manifests
- blocking leakage and metric review before leaderboard admission
- compact memory distillation across runs

## Current Scope

Initial target: supervised tabular classification/regression.

The first version is intentionally agent-runtime agnostic. Any coding agent that can read markdown, edit files, and run shell commands should be able to use the skills in `skills/`.

This repo intentionally does not provide an always-on shell runner, Docker sandbox orchestration, or IDE control plane. Those layers are expected to come from Codex, Claude Code, Cursor, Aider, or another host agent environment. `auto-automl` defines the portable AutoML loop contracts, skills, schemas, and artifacts that those environments execute.

Core skills are also tooling-neutral. They should not suggest Databricks, MLflow, AutoGluon, Optuna, cloud platforms, or deployment stacks unless the user asks for them or the project already contains that stack.

## Repo Layout

```text
skills/
  automl-loop.md
  data-profile.md
  feature-engineer.md
  model-search.md
  leakage-auditor.md
  metric-reviewer.md
  experiment-distiller.md

schemas/
  experiment-manifest.schema.json
  registry-record.schema.json
  leakage-report.schema.json

experiments/
  README.md
  templates/
  runs/

projects/
  README.md
  <project_id>/
    pyproject.toml
    uv.lock
    experiments/
    src/
    data/
    outputs/

docs/research/
  llm-ralph-loops.md

docs/extension-packs.md
```

## Loop Shape

```text
read contracts -> choose one hypothesis -> implement one experiment
              -> run validation -> audit leakage -> review metric
              -> admit/reject -> distill memory -> repeat with fresh context
```

The sealed final holdout is outside normal loop operation. Final test evaluation should be a separate release gate after model selection has stopped.

Agents should use `AGENTS.md` as the entry point for finding the loop instructions. It points to the project workspace, contracts, loop skill, verification gates, and memory distillation step.

One worker iteration is not the same as the whole AutoML application loop. The host agent environment may repeat worker iterations until `projects/<project_id>/experiments/metric_contract.md` says the stop policy is satisfied.

## Skill Order

1. `skills/data-profile.md` creates the dataset, split, and metric contract.
2. `skills/automl-loop.md` runs one Ralph-style iteration.
3. `skills/feature-engineer.md` proposes fold-safe feature changes.
4. `skills/model-search.md` proposes bounded model/HPO changes.
5. `skills/leakage-auditor.md` blocks invalid experiments.
6. `skills/metric-reviewer.md` blocks weak or misleading metric claims.
7. `skills/experiment-distiller.md` compresses accepted and rejected runs into memory.

Templates for contracts and run artifacts live in `experiments/templates/`.

## Project Workspaces

Generated ML project code should live under `projects/<project_id>/`, not at the repo root. The root repo is the reusable skill/control layer; child project directories are where agents create task-specific training code, notebooks, data adapters, configs, and model artifacts.

All task-specific work should stay inside the child project directory, including contracts, registries, memory, run metadata, data splits, outputs, notebooks, environment files, and local scripts. The root `experiments/` directory is for reusable templates and framework documentation only.

For Python experiments, prefer a project-local `uv` environment:

- create or reuse `projects/<project_id>/pyproject.toml`
- run commands from `projects/<project_id>/`
- use `uv --cache-dir .uv-cache run <command>` instead of bare `python`, `python3`, or `pip`
- prefer `pyproject.toml` scripts for repeatable commands
- keep `uv.lock`, `.venv/`, and `.uv-cache/` inside the child project

## Optional Extension Packs

Tool-specific guidance belongs in optional extension packs, not the core loop. For example, a future Databricks + MLflow 3 pack could add deployment, model registry, experiment tracking, and platform-specific validation skills, but it should only be used when explicitly requested or when an existing project already depends on that stack.

See `docs/extension-packs.md`.

## Non-Negotiables

- Never fit preprocessing on validation or test rows.
- Never use final holdout results for loop decisions.
- Never admit a run with a `FAIL` leakage verdict.
- Never compare runs without a shared split/metric contract.
- Never treat an LLM self-critique as a substitute for programmatic checks.
