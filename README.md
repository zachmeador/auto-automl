# auto-automl

`auto-automl` is a portable set of markdown skills and contracts for running Ralph-style AutoML workflows in agentic coding tools.

The goal is not to let an LLM freely "do machine learning." The goal is to let an agent propose and run machine-learning experiments while explicit contracts protect evaluation integrity:

- immutable train/validation/test split definitions
- fold-safe preprocessing and feature engineering
- no normal-loop access to sealed final holdout results
- reproducible experiment manifests
- blocking leakage and metric review before leaderboard admission
- compact memory distillation across runs

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
  experiment-distiller.md

schemas/
  experiment-manifest.schema.json
  registry-record.schema.json
  leakage-report.schema.json

experiments/
  README.md
  templates/

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
  autoresearch-pattern.md

docs/extension-packs.md
```

## How It Works

```text
contracts -> experiment search -> validation -> leakage audit
          -> metric review -> registry admission -> memory distillation
```

The sealed final holdout stays outside normal model search. Final test evaluation should be a separate release gate after model selection stops.

Generated ML projects live under `projects/<project_id>/`. The repository root contains reusable skills, schemas, templates, docs, and framework guidance.

Agent-facing instructions are rooted in `AGENTS.md`. Claude-specific entrypoint: `CLAUDE.md`.

## Included Skills

- `data-profile`: dataset, split, and metric contracts
- `automl-loop`: Ralph-style worker execution
- `feature-engineer`: fold-safe feature changes
- `model-search`: bounded model and hyperparameter search
- `leakage-auditor`: train/eval/test leakage review
- `metric-reviewer`: objective and metric validation
- `experiment-distiller`: compact memory records

Templates for contracts and run artifacts live in `experiments/templates/`.

## Optional Extension Packs

Tool-specific guidance belongs in optional extension packs, not the core loop. For example, a future Databricks + MLflow 3 pack could add deployment, model registry, experiment tracking, and platform-specific validation skills for projects that explicitly use that stack.

See `docs/extension-packs.md`.
