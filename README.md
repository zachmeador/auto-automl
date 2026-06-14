# auto-automl

`auto-automl` is a portable set of markdown skills and lightweight records for running Ralph-style AutoML workflows in agentic coding tools.

The goal is to let an agent run an unattended metric search loop while a fixed evaluator and split rules protect evaluation integrity:

- compact project card with target, split, metric, evaluator command, holdout rule, and stop policy
- fixed train/validation evaluator for routine search
- frontier ledger for keep/discard decisions
- fold-safe preprocessing and feature engineering
- no normal-loop access to sealed final holdout results
- enough command/code/metric detail to reproduce frontier-advancing candidates

## Current Scope

Initial target: supervised tabular classification/regression.

The first version is intentionally agent-runtime agnostic. It is meant to be used from host environments such as Codex, Claude Code, Cursor, Aider, or similar tools that already provide execution, sandboxing, and orchestration.

## Repo Layout

```text
AGENTS.md
CLAUDE.md

skills/
  automl-loop.md
  data-profile.md
  feature-engineer.md
  model-search.md
  leakage-auditor.md
  metric-reviewer.md

schemas/
  frontier-record.schema.json

experiments/
  README.md
  templates/
    project_card.md
    frontier-record.example.json

projects/
  README.md
  <project_id>/
    pyproject.toml
    uv.lock
    experiments/
      project_card.md
      frontier.jsonl
    src/
    data/
    outputs/

docs/research/
  llm-ralph-loops.md
  autoresearch-pattern.md

docs/extension-packs.md
```

## How It Works

```text
project card -> mutate bounded code/config -> fixed validation evaluator
             -> advance or discard frontier -> compact ledger -> repeat
```

The sealed final holdout stays outside normal model search. Final test evaluation should be a separate release action after model selection stops.

Generated ML projects live under `projects/<project_id>/`. The repository root contains reusable skills, schemas, templates, docs, and framework guidance.

Agent-facing instructions are rooted in `AGENTS.md`. Claude-specific entrypoint: `CLAUDE.md`.

## Included Skills

- `data-profile`: creates the project card
- `automl-loop`: runs one Ralph-style worker session
- `feature-engineer`: proposes and implements fold-safe feature changes
- `model-search`: proposes and implements bounded model/HPO changes
- `leakage-auditor`: checklist for split, holdout, target, temporal, entity, and preprocessing leakage risk
- `metric-reviewer`: checklist for evaluator correctness and close metric calls

Templates live in `experiments/templates/`.

## Optional Extension Packs

Tool-specific guidance belongs in optional extension packs, not the core loop. See `docs/extension-packs.md`.
