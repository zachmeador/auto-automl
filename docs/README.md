# Model-building workflow

The workflow turns a defined prediction problem and source dataset into a validated, reproducible model artifact.

1. [Problem definition](01-problem-definition.md) — specify the prediction contract.
2. [Data ingestion and validation](02-data-ingestion-and-validation.md) — create a trustworthy dataset.
3. [Data splitting](03-data-splitting.md) — reserve unbiased evaluation data.
4. [Preprocessing and features](04-preprocessing-and-features.md) — create model-ready inputs.
5. [Candidate pipelines](05-candidate-pipelines.md) — define valid model configurations.
6. [Search and tuning](06-search-and-tuning.md) — optimize configurations within a budget.
7. [Evaluation and selection](07-evaluation-and-selection.md) — choose and characterize a winner.
8. [Final training and packaging](08-final-training-and-packaging.md) — produce the inference artifact.

Each stage defines its decisions, procedure, deliverables, safeguards, and exit criteria. Later stages consume versioned outputs from earlier stages. Deployment and production monitoring begin after this workflow.
