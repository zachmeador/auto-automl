---
name: automl-loop
description: Run one Ralph-style AutoML worker session that mutates a bounded surface, evaluates on validation, updates the frontier ledger, and reports whether the application loop should continue.
---

# AutoML Worker Session Skill

Use this skill for one worker session inside a larger AutoML application loop. A worker session is a practical unit of progress, not necessarily one model fit and not the whole project unless the project card's stop policy says the project is done.

## Core Loop

```text
read project card + frontier
-> choose one bounded change
-> run the trusted validation evaluator
-> compare against current frontier
-> keep or discard the change
-> append one compact frontier record
-> recommend the next move
```

## Inputs

Required:

- Project card: target, split rule/artifacts, primary validation metric, direction, evaluator command, sealed holdout rule, budget/stop policy, and known leakage risks.
- Frontier ledger: current best validation result and meaningful prior attempts, typically `projects/<project_id>/experiments/frontier.jsonl`.
- Current project code/config under `projects/<project_id>/`.

Optional:

- One user-provided hypothesis.
- Approved model/tool list.

## Hard Rules

- Do not access sealed final holdout labels or metrics during normal search.
- Optimize validation only.
- Use the same split and metric comparison rule as the project card unless the session objective is explicitly to fix the evaluator or split.
- Keep all task-specific work under `projects/<project_id>/`.
- Keep the session focused on one practical objective or one tightly related experiment family.
- You may run bounded inner search, such as CV, HPO, threshold search, ablations, repeated seeds, or feature variants, when the search budget and selection rule are clear.
- Record enough detail to reproduce frontier-advancing candidates and any scratch result that changes future choices.

## Python Runtime Rules

For Python experiments:

- Prefer an existing stable evaluator command.
- If loop-created Python code needs project scaffolding, create or reuse `projects/<project_id>/pyproject.toml`.
- Run commands from `projects/<project_id>/`.
- Prefer `uv --cache-dir .uv-cache run <command>` over bare `python`, `python3`, `pip`, or global environments.
- Keep `uv.lock`, `.venv/`, and `.uv-cache/` inside `projects/<project_id>/`.
- Record the exact command and working directory in the frontier record.

## Procedure

1. Rehydrate only relevant context.
   - Read `project_card.md` and `frontier.jsonl`.
   - Check whether the stop policy is already satisfied before starting a new experiment.
   - Identify the current frontier: best valid validation result under the declared comparison rule.

2. Choose the session objective.
   - Examples: establish a baseline, debug evaluator failure, try one model family, search one feature family, calibrate a threshold, or verify a promising candidate.
   - Keep the objective small enough that the result can be interpreted.

3. Explore or implement.
   - Keep preprocessing inside train-fold-only pipelines.
   - Use the approved evaluator command when present.
   - If no command exists, create the smallest task-local command needed under `projects/<project_id>/`.
   - Keep scratch outputs under the child project.

4. Run validation and compare.
   - Evaluate only on approved train/validation data.
   - Compare with the current frontier using the metric direction, tie-breakers, and minimum improvement rule from the project card when specified.
   - Treat missing minimum practical delta as "any real metric improvement advances" unless the project card says otherwise.

5. Decide keep/discard.
   - Advance the frontier when the candidate improves or establishes the first valid baseline.
   - Keep non-improving changes only when they fix infrastructure, reduce risk, or encode a durable lesson.
   - Discard or revert ordinary losing changes when the host environment supports that frontier style.

6. Append a compact frontier record.
   - Write one JSONL row to `projects/<project_id>/experiments/frontier.jsonl`.
   - Include run id, timestamp, hypothesis/change summary, command, code ref or diff path, metric value, comparison baseline, status, risk flags, and next hint.
   - Store full logs separately only when they are needed for debugging or reproducibility.

7. Run review checklists only when needed.
   - Use `skills/leakage-auditor.md` when the session changes split/evaluator/data availability logic, introduces high-risk features, produces a suspicious metric jump, or prepares a final recommendation.
   - Use `skills/metric-reviewer.md` when the evaluator or metric changed, the improvement is close or statistically uncertain, constraints matter, or the candidate is final/recommended.
   - Put review verdicts or notes in the frontier record or a short project-local note.

8. Check project-level stop policy.
   - Read the stop policy from `project_card.md`.
   - Report whether a stop condition is satisfied.
   - If no stop condition is satisfied, report that the application loop should continue and include the next recommended hypothesis.
   - If a stop condition is satisfied, report the stopping reason and current frontier run.

## Worker Report

The worker session reports:

- session objective
- run id
- metric value and delta versus frontier, if measured
- frontier status: `advanced`, `kept`, `discarded`, `blocked`, or `not_run`
- review verdicts only if review checklists were used
- project stop condition status
- application loop status: `continue` or `stop`
- next recommended hypothesis

Do not claim "AutoML complete" unless the project-level stop policy is satisfied.
