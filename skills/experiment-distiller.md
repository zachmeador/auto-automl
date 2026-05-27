---
name: experiment-distiller
description: Distill AutoML experiment outcomes into compact memory for future Ralph-loop iterations.
---

# Experiment Distiller Skill

Use this skill after an experiment has metrics, leakage audit, and metric review.

## Goal

Turn a run into compact memory that helps the next fresh-context agent avoid redundant search and repeat useful patterns.

Do not paste long logs. Extract reusable lessons.

## Distillation Fields

Produce one compact JSON-like record with:

- `run_id`
- `dataset_hash`
- `split_id`
- `hypothesis`
- `changes`
- `metric_delta`
- `leakage_verdict`
- `metric_review_verdict`
- `admitted`
- `cost`
- `lesson`
- `avoid`
- `next_hypothesis`

## Lesson Rules

Good lessons are:

- specific enough to affect a future experiment
- tied to the dataset or task type
- honest about failed attempts
- clear about leakage constraints
- short

Bad lessons:

- "model improved"
- "try better features"
- full command output
- long stack traces
- vague praise of a model family

## Memory Categories

Use these labels when useful:

- `successful_pattern`
- `failed_pattern`
- `forbidden_pattern`
- `dataset_warning`
- `metric_warning`
- `runtime_warning`
- `next_direction`

## Output

Append the distilled record to the configured memory file, or write it to the run notes if no memory file exists.

Do not mark a run as admitted unless both leakage and metric review verdicts are `PASS`.

