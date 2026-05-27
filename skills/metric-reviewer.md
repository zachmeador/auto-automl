---
name: metric-reviewer
description: Review one AutoML run for objective alignment, metric correctness, statistical credibility, and leaderboard admission.
---

# Metric Reviewer Skill

Use this skill after validation metrics exist and after leakage audit has run.

Review the run under `projects/<project_id>/experiments/runs/<run_id>/`. Treat task-specific metric artifacts outside `projects/<project_id>/` as suspicious unless they are explicitly approved read-only inputs.

## Verdicts

- `PASS`: metric claim is valid enough for admission.
- `WARN`: keep the run, but do not promote without human review or more evidence.
- `FAIL`: metric claim is invalid, misleading, or not comparable.

## Review Checklist

Objective alignment:

- Does the primary metric match the declared goal?
- Is direction explicit?
- Are secondary constraints honored?

Comparability:

- Same split as baseline?
- Same target definition?
- Same sample weighting?
- Same preprocessing boundary?
- Same evaluation command or compatible metric implementation?
- Same project-local environment command pattern?

Statistical credibility:

- Is improvement larger than the minimum practical threshold?
- Are fold-level scores, repeated seeds, or confidence intervals needed?
- Is variance reported for close comparisons?
- Could a single lucky split explain the improvement?

Operational constraints:

- Runtime within budget?
- Memory within budget?
- Inference latency acceptable?
- Calibration, threshold, fairness, or class-specific constraints satisfied when relevant?

Leaderboard decision:

- `admitted: true` only if metric verdict is `PASS` and leakage verdict is `PASS`.
- `WARN` can enter memory but should not displace the current best model.
- `FAIL` must be rejected and distilled as a cautionary lesson.

## Output

Write `metric_review.md` in `projects/<project_id>/experiments/runs/<run_id>/` with:

- verdict
- baseline comparison
- metric deltas
- uncertainty or variance notes
- operational notes
- admission decision
