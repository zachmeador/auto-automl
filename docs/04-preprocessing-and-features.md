# Preprocessing and features

## Goal

Define a deterministic transformation from validated raw records to model-ready features. Every learned transformation must be fit on training data and applied unchanged to validation, test, and inference data.

## Feature contract

For each input field, record its semantic type, allowed values, missing-value behavior, availability time, transformation, output feature names, and inference behavior for invalid or unseen values.

Common semantic types require different handling:

- **Numeric:** preserve, impute, scale, transform, bin, or clip.
- **Categorical:** encode with explicit unknown and missing behavior.
- **Ordinal:** encode using a documented order; do not infer order from labels.
- **Boolean:** normalize accepted representations and preserve missingness if meaningful.
- **Datetime:** normalize timezone, then derive only causally available components or durations.
- **Text:** normalize and vectorize under bounded vocabulary and memory rules.
- **Structured fields:** parse with a versioned, validated extractor.
- **Identifiers:** exclude by default; retain separately for joins, grouping, and audits.

## Procedure

### 1. Define exclusions

Remove prohibited, post-outcome, direct-target, duplicate, unsupported, constant, and operational-only fields. Record the reason for each exclusion. Exclusion based on data statistics must occur inside training folds when it can affect evaluation.

### 2. Handle missing values

Choose per-feature or per-type behavior: reject, constant fill, learned imputation, or model-native missing handling. Add missingness indicators when absence may be predictive and available at inference. Do not confuse missing, zero, empty string, “unknown,” and “not applicable.”

### 3. Encode categoricals

Define behavior for unseen categories. Bound one-hot expansion by grouping rare values, hashing, or selecting an alternative encoder. Any target-dependent encoding must be trained out-of-fold and repeated inside every outer fold; otherwise it leaks labels.

### 4. Transform numerics

Use scaling for models sensitive to feature magnitude. Consider monotonic transforms for severe skew only when valid for the domain. Treat clipping thresholds, quantile maps, and normalization statistics as learned parameters. Check that transforms produce finite values.

### 5. Derive features

Generate domain features from information available by observation time. State source columns, formula, units, and boundary behavior. For rolling or aggregate features, ensure each value uses only permitted historical records and can be reproduced in serving.

### 6. Assemble the pipeline

Combine column-specific transformations, feature selection, and the estimator into one object. This lets cross-validation refit every learned step per fold and ensures inference uses identical logic. Scikit-learn's [`ColumnTransformer` and `Pipeline`](https://scikit-learn.org/stable/modules/compose.html) support heterogeneous, searchable, leakage-safe pipelines.

### 7. Validate the result

For each candidate preprocessing path, test:

- output row count and feature count;
- deterministic feature order and unique names;
- finite numeric output;
- sparse versus dense representation and memory use;
- empty, all-missing, constant, and unseen-category cases;
- serialization and clean-process inference;
- consistency between batch and single-record transforms.

## Deliverables

- Unfitted preprocessing specifications used by candidate pipelines.
- Feature lineage from raw fields to model inputs.
- Missing, unknown, invalid, and boundary-value rules.
- Exclusion registry.
- Transformed-shape and resource estimates.
- Edge-case fixtures and validation results.

## Safeguards

- Never fit preprocessing on the full dataset before cross-validation.
- Never compute feature-selection statistics using validation or test labels.
- Do not assume training categories, ranges, or schemas will remain fixed at inference.
- Reject or explicitly route malformed records; silent coercion makes prediction behavior untraceable.
- Avoid transformations that cannot be reproduced in the serving environment.

## Exit criteria

The stage is complete when every candidate can transform each fold without leakage, feature lineage is known, inference edge cases have defined behavior, and transformed data stays within resource limits.
