---
name: model-search
description: Propose and implement one bounded model-selection or hyperparameter-search change inside an AutoML worker session.
---

# Model Search Skill

Use this skill when the selected experiment changes model class, hyperparameters, ensembling, calibration, loss, thresholding, or training procedure.

A model-search worker session may run an inner search loop. Treat the search like a human would: define the rough search space and budget before running it, inspect results, and record the selected result in the frontier ledger.

## Hard Rules

- Search only within the declared budget.
- Use the project card's split, metric, and evaluator exactly unless the objective is to fix them.
- Do not use final holdout results for search.
- Keep preprocessing coupled to the model pipeline.
- Record enough detail to reproduce the selected candidate and any result that influences future choices.
- Define the search space, budget, and selection criterion before running the search.

## Procedure

1. Identify the current frontier baseline.
2. Choose one bounded model-search hypothesis.
3. Define the search space before running it.
4. Define the selection rule before running it.
5. Run the approved evaluation command or a minimal equivalent.
6. Record all tried configs or a search summary sufficient to reproduce the selected candidate and understand discarded alternatives.
7. Compare the selected candidate against the frontier with the project card's metric rule.

## Sensible First Search Spaces

For tabular tasks, prefer:

- regularized linear/logistic baseline
- random forest or extra trees
- gradient boosting family
- calibrated classifier when probabilities matter
- simple ensembles only after multiple strong frontier models exist

## Metric Discipline

Close wins may require repeated seeds, confidence intervals, or fold-level evidence before final recommendation. Routine frontier advancement can still use validation improvement when the evaluator is trusted and the project card has no close-call rule.

## Output

Update the frontier record or run notes with:

- model hypothesis
- explicit search space
- selected configuration
- all meaningful metric values
- selected candidate and selection criterion
- runtime and resource use
- comparison to current frontier baseline
