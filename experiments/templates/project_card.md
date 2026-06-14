# Project Card

Status: incomplete

Project ID:
Project root: `projects/<project_id>/`

## Task

- Task type:
- Target:
- One row means:
- Prediction time / horizon:

## Data And Split

- Training data:
- Validation data:
- Split rule or generation command:
- Group/time constraints:
- Final holdout policy: sealed

## Metric And Evaluator

- Primary metric:
- Direction: maximize
- Evaluator command:
- Expected metric output:
- Tie-breakers:
- Minimum practical delta:

## Frontier

- Frontier ledger: `projects/<project_id>/experiments/frontier.jsonl`
- Current best run:
- Current best metric:

## Budget And Stop Policy

- Max experiments:
- Max wall-clock time:
- Stop after no improvement:
- Target metric:
- Human interrupt: always stop

## Safety Notes

- Forbidden columns:
- Post-outcome or future-only fields:
- High-risk feature families:
- Known leakage risks:

## Blockers

Block model search only if target, train/validation split or evaluator command, metric direction, or final holdout policy is unknown.
