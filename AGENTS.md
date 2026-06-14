# Agent Instructions

This repo defines portable markdown skills for Ralph-style AutoML loops.

## Concepting Phase

This repo is in concepting and design exploration. Treat the current files, loop shape, and runtime-agnostic framing as working hypotheses, not legacy architecture that must be preserved by default.

When asked to research or evaluate a new runtime, harness, or product direction, compare what it unlocks against what the current concept assumes. Do not recommend keeping the current core, pushing something into an extension pack, or preserving runtime agnosticism merely because those ideas are already present. It is acceptable to recommend replacing, collapsing, or reworking existing concepts when the evidence points that way.

## Operating Rules

- Keep skills plain markdown and runtime agnostic unless the user asks for a specific harness.
- Do not build an always-on shell runner, Docker sandbox layer, or IDE control plane into core. Assume host agent environments provide execution and isolation.
- Keep the core loop tooling-neutral. Do not recommend Databricks, MLflow, AutoGluon, Optuna, cloud services, or deployment platforms unless explicitly requested or already present in the user's project.
- Put tool-specific instructions in optional extension packs.
- Use one compact project card and one compact frontier ledger as the durable loop state.
- Preserve the sealed final holdout boundary. Normal experiment loops may optimize validation metrics only.
- Treat split/evaluator integrity as blocking. Use leakage or metric review only when the worker touches that risk boundary, sees a suspicious jump, has a close metric call, or is making a final recommendation.
- Keep all task-specific work under `projects/<project_id>/`: source code, configs, notebooks, data splits, outputs, project cards, frontier ledgers, environment files, and local scripts.
- Do not place project-specific code or artifacts at the repository root or in root-level `experiments/runs/`.
- For Python experiments, prefer project-local `uv`: create or reuse `projects/<project_id>/pyproject.toml`, run from the child project directory, and prefer `uv --cache-dir .uv-cache run <command>` over bare `python`, `python3`, `pip`, or global environments.
- Prefer an existing repeatable evaluator command. Add `pyproject.toml` scripts only when no stable command exists.
- Keep `.venv/`, `.uv-cache/`, and `uv.lock` project-local.

## How To Execute The Loop

The AutoML loop has two levels:

- **Worker session**: one fresh-context agent session makes one practical move: setup, debugging, baseline work, feature exploration, model search, evaluation cleanup, or frontier advancement.
- **Application loop**: the host agent environment repeats worker sessions until the project card's stop policy is satisfied.

A worker session may contain bounded inner algorithmic search, such as cross-validation, hyperparameter search, threshold search, feature selection, ablations, or repeated seeds, when that search stays within the project card's budget.

Shape the work like a competent human ML engineer:

1. Understand the project card: target, split, metric, evaluator command, holdout rule, stop policy, and current frontier.
2. Make the smallest useful next move.
3. Explore quickly inside the project workspace.
4. Run the trusted evaluator on approved train/validation data.
5. Advance the frontier only when the validation result improves under the declared comparison rule.
6. Append one compact frontier record and leave a next-step recommendation.

Do not create full formal artifacts for scratch attempts. Any candidate that advances the frontier, changes future search, or could be reused must be reproducible from a command, config or diff, code state, and metrics summary.

Do not treat a host application's "active goal" or the current chat request as the project stop policy. The project stop policy lives in `projects/<project_id>/experiments/project_card.md`.

When asked to run, continue, or execute the AutoML loop, follow this path:

1. Read this file, `README.md`, and `projects/README.md`.
2. Identify or create the child project workspace: `projects/<project_id>/`.
3. Read or create `projects/<project_id>/experiments/project_card.md`.
4. Read `projects/<project_id>/experiments/frontier.jsonl` if present.
5. Check the stop policy in the project card.
6. If a stop condition is already satisfied, do not start a new experiment. Report the stopping reason and current best frontier run.
7. If no stop condition is satisfied, execute one worker session using `skills/automl-loop.md`.
8. If the session touches split/evaluator/data-availability logic, uses high-risk features, produces a suspicious jump, has a close metric call, or recommends a final candidate, apply the relevant review checklist:
   - `skills/leakage-auditor.md`
   - `skills/metric-reviewer.md`
9. Re-check the project card stop policy.
10. Report the iteration result, whether the application loop should continue, and the next recommended hypothesis if continuing.

If the host environment is running an always-on Ralph loop, it may invoke a new fresh-context worker session after step 10 when the stop policy says to continue. If the current session is just one worker invocation, stop after step 10 so the host loop can decide whether to launch the next worker.

## AutoML Safety Rules

- Split before preprocessing.
- Fit transformers, encoders, imputers, scalers, feature selectors, oversamplers, and target encoders only on training folds.
- Use group-aware or time-aware splits when the prediction setting requires them.
- Do not query final test metrics during model search.
- Record enough detail to reproduce every frontier-advancing candidate and every scratch result that influences future decisions.

## File Conventions

- `skills/*.md` are reusable agent skills.
- `schemas/*.schema.json` define structured records that tools and agents should honor.
- `experiments/README.md` documents reusable templates and root-level experiment constraints.
- `projects/README.md` documents child project workspaces.
- `docs/research/` stores supporting research notes.
- `docs/extension-packs.md` defines when tool-specific packs are appropriate.
