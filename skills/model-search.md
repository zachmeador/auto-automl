---
name: model-search
description: Propose and implement one bounded model-selection or hyperparameter-search change inside an AutoML worker iteration.
---

# Model Search Skill

Use this skill when the selected experiment changes model class, hyperparameters, ensembling, calibration, loss, thresholding, or training procedure.

A model-search experiment may run an inner search loop. The outer worker iteration is still one experiment family if the search space, budget, split, metric, and selection rule are declared before execution.

## Hard Rules

- Search only within the declared budget.
- Use the split and metric contracts exactly.
- Do not use final holdout results for search.
- Keep preprocessing coupled to the model pipeline.
- Record every trial that can influence future choices.
- Define the search space and selection criterion before running the search.

## Procedure

1. Identify the current admitted baseline.
2. Choose one bounded model-search hypothesis.
3. Define the search space before running it.
4. Define the selection rule before running it.
5. Run the approved evaluation command or a minimal equivalent.
6. Record all tried configs or the search summary needed to reproduce them.
7. Compare the selected candidate against baseline with the metric contract.

## Sensible First Search Spaces

For tabular tasks, prefer:

- regularized linear/logistic baseline
- random forest or extra trees
- gradient boosting family
- calibrated classifier when probabilities matter
- simple ensembles only after multiple strong admitted models exist

## Metric Discipline

Close wins require repeated seeds, confidence intervals, or fold-level evidence. Treat tiny single-split wins as `WARN` unless the metric contract says otherwise.

## Output

Update run artifacts with:

- model hypothesis
- explicit search space
- selected configuration
- all meaningful metric values
- selected candidate and selection criterion
- runtime and resource use
- comparison to current admitted baseline
