# Data ingestion and validation

## Goal

Produce a reproducible, versioned dataset with known semantics and measured quality. Validation must distinguish unusable data from unusual but valid data; silent repair hides defects.

## Inputs

- Prediction contract and target derivation.
- Source locations, extraction query or API parameters, and access rules.
- Expected schema, units, keys, and update behavior.
- Domain rules for valid records.

## Procedure

### 1. Capture provenance

Record source identifiers, extraction time, query or code version, partitions read, source snapshot or version, and row counts. Preserve raw source values until validation finishes. Assign a stable dataset fingerprint from content or immutable source references.

### 2. Establish row identity

Define the primary observation key. Check uniqueness at the prediction-unit grain. If multiple rows belong to one entity, retain the entity or group key needed for leakage-safe splitting. Classify identifiers as:

- observation keys used for joins and auditing;
- grouping keys used for splitting;
- candidate predictors with a documented justification;
- prohibited identifiers excluded from training.

### 3. Validate the schema

For each field, record:

- name, semantic role, physical type, and logical type;
- unit, timezone, category set, or valid range;
- nullability and default behavior;
- whether it exists at prediction time;
- whether it is sensitive, derived, or target-related.

Reject missing required columns, unexpected duplicate names, incompatible types, invalid targets, and ambiguous unit or timezone changes. Handle extra columns explicitly; do not automatically admit them as features.

### 4. Profile quality

Measure at minimum:

- row and unique-entity counts;
- missingness by field and important subgroup;
- duplicate rows and duplicate keys;
- numeric quantiles, infinities, impossible values, and outliers;
- categorical cardinality, rare values, and unexpected categories;
- date ranges, ordering, gaps, and future timestamps;
- target prevalence or distribution;
- constant and near-constant fields;
- trainable sample count after exclusions.

Compare these statistics across source, time, location, collection process, and relevant subgroups. A global average can conceal a broken partition.

### 5. Audit target and leakage

Recompute a sample of targets from source events. Check label delay, unresolved outcomes, censoring, and duplicated outcomes. Flag fields that directly encode the target, occur after observation time, summarize the label window, or are populated only after an outcome. Search for the same entity or event represented multiple ways.

### 6. Apply explicit rules

Apply inclusion, exclusion, deduplication, and correction rules in a deterministic order. For every rule, record the reason and counts before and after. Prefer failing validation over guessing how to repair an undocumented source change.

## Deliverables

- Immutable dataset reference and fingerprint.
- Extraction manifest and provenance.
- Field-level schema with semantic roles.
- Validation report with partition and subgroup summaries.
- Row-level rejection reasons or aggregate exclusion log.
- Leakage findings and unresolved data risks.

## Safeguards

- Never overwrite raw inputs during cleaning.
- Never coerce parse failures to missing values without reporting their count.
- Keep sensitive attributes under appropriate access control. When lawful and necessary, retain them separately for subgroup auditing even if they are not predictors.
- Do not infer representativeness from dataset size. Document how collection and selection differ from the intended population. The [NIST AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) calls for documenting data availability, representativeness, suitability, collection, and selection.

## Exit criteria

The stage is complete when the same extraction can be identified or reproduced, each field has an understood role, all blocking checks pass, every row-removal rule is counted, and unresolved quality limits are visible to later stages.
