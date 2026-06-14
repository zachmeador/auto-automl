---
name: data-profile
description: Create the minimal project card for AutoML search.
---

# Data Profile Skill

Use this skill before model search or feature engineering. Its output is one compact project card that defines what the loop can safely optimize.

## Output

Write:

- `projects/<project_id>/experiments/project_card.md`

Do not write task-specific project cards to the repository root or root-level `experiments/`.

## Project Card Fields

Record only what the loop needs to start safely:

- project id and project root
- task type and target
- one-row meaning and prediction-time meaning, if known
- train/validation split rule or artifact paths
- sealed final holdout policy
- primary validation metric and maximize/minimize direction
- evaluator command and expected metric output
- current frontier baseline, if any
- search budget or stop policy
- forbidden columns, post-outcome fields, and high-risk feature families
- group/time constraints when relevant

## Blocking Unknowns

Block model search only when one of these is unknown:

- target definition
- train/validation split or evaluator command
- primary metric and direction
- final holdout access policy

Other missing details should be marked as risks in the project card and resolved when they matter.
