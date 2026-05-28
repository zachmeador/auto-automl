---
name: automl-loop
description: Run one fresh-context AutoML worker session that explores, evaluates, optionally promotes a candidate, and reports whether the application loop should continue.
---

# AutoML Worker Session Skill

Use this skill for one worker session inside the larger AutoML application loop. A worker session is a human-sized unit of progress, not necessarily one model fit and not the whole project unless the metric contract's stop policy says the project is done.

## Terminology

`Worker session` means one fresh-context Ralph worker invocation. It can include setup, debugging, baseline work, exploratory search, a model/feature experiment, or promotion of a candidate.

Allowed inner loops include cross-validation, hyperparameter search, threshold search, feature selection, ablations, repeated seeds, and model-family searches when they are part of the declared experiment hypothesis.

Inner loops should:

- stay within the metric contract's runtime/cost/search budget
- use only approved train/validation data
- keep the final holdout sealed
- record promoted trials or a reproducible search summary
- report the selected candidate and selection criterion

## Human-Shaped Workflow

Work like a practical ML engineer:

1. Orient on contracts, code, current best result, and recent lessons.
2. Pick the smallest useful next move.
3. Explore quickly inside `projects/<project_id>/`.
4. Keep scratch work lightweight.
5. Promote a candidate only when it is useful, reproducible, and worth comparing.
6. Run leakage audit and metric review only for promoted registry candidates.
7. Distill the useful lesson and next move.

Scratch work can be informal, but it cannot violate split, holdout, or project-local rules. If scratch results influence the next session, summarize them in notes or memory.

## Inputs

Required:

- Dataset contract: source, target, prediction time, allowed features, unavailable features, entity/time semantics.
- Split contract: train/validation/test definitions, group/time constraints, split artifact hashes if available.
- Metric contract: objective metric, direction, project goal, stop policy, tie-breakers, minimum practical improvement, runtime budget.
- Current registry or leaderboard.
- Prior distilled memory, if available.

Optional:

- One user-provided hypothesis.
- Existing baseline code.
- Approved model/tool list.

## Hard Rules

- Do not access sealed final holdout labels or metrics.
- Optimize validation only.
- Keep all task-specific work under `projects/<project_id>/`.
- Do not write project-specific code, contracts, data, outputs, run records, registries, or memory files at the repository root or under root-level `experiments/runs/`.
- Keep the session focused on one practical objective or one tightly related experiment family.
- You may run a bounded inner search inside that objective when the search budget and selection rule are clear.
- Record enough detail to reproduce promoted candidates and scratch results that influence future choices.
- A candidate is not admitted to the registry until leakage audit and metric review pass.

## Python Runtime Rules

For Python experiments:

- Create or reuse `projects/<project_id>/pyproject.toml`.
- Run commands from `projects/<project_id>/`.
- Use `uv --cache-dir .uv-cache run <command>` instead of bare `python`, `python3`, `pip`, or a global environment.
- Prefer `[project.scripts]` entries in `pyproject.toml` for repeatable prepare/train/evaluate/audit commands.
- Keep `uv.lock`, `.venv/`, and `.uv-cache/` inside `projects/<project_id>/`.
- Record each command and repo-relative project working directory, for example `projects/<project_id>`, in the manifest.

## Procedure

1. Rehydrate only relevant context.
   - Read contracts, registry, and compact memory.
   - Check whether the project stop policy is already satisfied before starting a new experiment.
   - Identify the current best admitted baseline.
   - Select one next hypothesis.

2. Resolve the project workspace.
   - If a project workspace does not exist, create `projects/<project_id>/`.
   - Keep task-specific source code, configs, notebooks, data, outputs, contracts, registries, memory, and local scripts inside that child directory.
   - Keep run metadata under `projects/<project_id>/experiments/runs/<run_id>/`.
   - For Python projects, set up or reuse the project-local `uv` environment before running project code.

3. Choose the session objective.
   - Examples: establish baseline, debug split integrity, try one model family, search one feature family, calibrate thresholds, or promote a promising candidate.
   - Write a brief note before starting if the objective is non-obvious or risky.

4. Explore or implement.
   - Keep preprocessing inside train-fold-only pipelines.
   - Use existing evaluation commands when present.
   - If no command exists, create the smallest task-local command needed under `projects/<project_id>/`.
   - Keep scratch outputs under the child project and summarize only what matters.

5. Decide whether to promote a candidate.
   - Promote when the result improves, establishes a baseline, fixes evaluation, reveals a durable lesson, or should influence future search.
   - Do not promote throwaway debugging or obviously failed scratch attempts unless they teach an important avoidance lesson.

6. For promoted candidates, write durable artifacts.
   - Use `projects/<project_id>/experiments/runs/<run_id>/`.
   - Capture metrics, runtime, random seeds, data hashes, code version, command lines, and a reproducible search summary.
   - Write `metrics.json` and `manifest.json`.
   - Write `plan.md` when the candidate involves nontrivial search, risk, or a new feature/model family. A short notes section is enough for simple baselines.

7. For promoted registry candidates, run the gates.
   - Apply `skills/leakage-auditor.md`.
   - Apply `skills/metric-reviewer.md`.
   - Do not admit the candidate if either gate fails.

8. Update registry when appropriate.
   - Append one structured registry record with `admitted: true` only if both gates pass.
   - Write the registry under `projects/<project_id>/experiments/registry.jsonl`.
   - Rejected promoted candidates may get registry records when they influenced future decisions.

9. Distill memory.
   - Apply `skills/experiment-distiller.md`.
   - Keep memory compact. Do not paste long logs.

10. Check project-level stop policy.
   - Read `projects/<project_id>/experiments/metric_contract.md`.
   - Report whether a stop condition is satisfied.
   - If no stop condition is satisfied, report that the application loop should continue and include the next recommended hypothesis.
   - If a stop condition is satisfied, report the stopping reason and current best admitted run.

## Worker Report

The worker session reports:

- session objective
- promoted run id, if any
- metric delta versus baseline, if measured
- leakage verdict, if audited
- metric review verdict, if reviewed
- admitted/rejected/not promoted status
- project stop condition status
- application loop status: `continue` or `stop`
- next recommended hypothesis

Do not claim "AutoML complete" unless the project-level stop policy is satisfied.
