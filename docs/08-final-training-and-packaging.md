# Final training and packaging

## Goal

Fit the approved pipeline on the declared final-training population and produce a versioned artifact that can be loaded, validated, and reconstructed.

## Freeze the training specification

Before fitting, record:

- dataset fingerprint and exact eligible population;
- preprocessing and feature specification;
- estimator family and all parameters, including defaults;
- feature order, class order, target transformation, threshold, and post-processing;
- random seeds and determinism settings;
- code revision and build command;
- runtime, dependency, hardware, and thread settings;
- expected input and output schemas.

No search, feature selection, threshold tuning, or evaluation-driven choice occurs during final fitting.

## Choose final-training data

State whether the final fit uses development data only or all eligible labeled data, including the former test partition. Including test data is reasonable only after evaluation is complete and the reported evaluation remains tied to the pre-refit model specification. Record the final population separately from the population used to estimate performance.

## Fit and package

1. Build a clean environment from the locked dependency specification.
2. Revalidate the dataset fingerprint, schema, row count, target distribution, and split policy.
3. Construct the frozen full pipeline.
4. Fit once on the declared final-training data.
5. Serialize preprocessing, feature logic, estimator, calibration, class mapping, and threshold together when the format supports it.
6. Generate an artifact checksum and unique model version.
7. Store the artifact in a controlled location with provenance and access rules.

Choose the serialization format from serving needs:

- a framework-native or Python object when the serving environment matches training;
- a safer inspectable format when artifacts may cross trust boundaries;
- an interchange format when independent runtimes are required and conversion fidelity can be tested.

Pickle-based formats can execute arbitrary code when loaded, and scikit-learn does not support loading persisted estimators across differing dependency versions. Review the security and compatibility tradeoffs in [scikit-learn's model-persistence guidance](https://scikit-learn.org/stable/model_persistence.html).

## Artifact validation

Reload the artifact in a clean process or target-like runtime. Verify:

- checksum and model version;
- accepted and rejected schemas;
- exact feature order and target/class mapping;
- prediction parity with the in-memory model on fixed fixtures;
- deterministic output within declared numerical tolerance;
- single-row, batch, empty-batch, and maximum supported batch behavior;
- missing values, unseen categories, boundary values, and invalid types;
- finite outputs and valid probability sums or numeric ranges;
- latency distribution, throughput, peak memory, and artifact size;
- absence of training-only source or network dependencies.

Store representative inputs and expected outputs as conformance fixtures. The serving implementation should run them before release and after environment changes.

## Model manifest

Package or link the following metadata:

- model identifier, creation time, owner, and status;
- prediction contract and intended use;
- artifact checksum and format;
- data fingerprint and provenance;
- code revision and dependency lock;
- complete parameters and seeds;
- feature and I/O schemas;
- evaluation report and acceptance decision;
- known limitations and prohibited uses;
- reconstruction and rollback instructions.

## Deliverables

- Versioned model artifact and checksum.
- Model manifest or model card.
- Locked runtime and reconstruction recipe.
- Input/output schemas.
- Conformance fixtures and clean-load test results.
- Final-training log and dataset reference.

## Safeguards

- Never load an untrusted pickle, joblib, or cloudpickle artifact.
- Keep secrets, credentials, raw sensitive data, and machine-specific paths out of the artifact.
- Do not report metrics from the final refit as independent test performance when that fit includes test labels.
- Retain enough source, data references, and environment metadata to rebuild rather than relying indefinitely on binary compatibility.
- Packaging does not authorize deployment. Release review, serving controls, observability, drift detection, and retraining policy belong to the operational lifecycle.

## Exit criteria

The stage is complete when a clean target-like environment can verify and load the artifact, reproduce expected predictions, enforce the schema, trace the artifact to code and data, and meet all declared resource constraints.
