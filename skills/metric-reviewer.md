---
name: metric-reviewer
description: Check evaluator changes, close comparisons, constraints, or final candidates for objective alignment, metric correctness, and statistical credibility.
---

# Metric Reviewer Skill

Use this checklist when metric validity can change the loop decision. It is not required for every routine frontier iteration.

Use it for:

- initial evaluator setup
- changes to metric code, sample weighting, thresholding, calibration, or evaluation data
- close wins where variance could explain the improvement
- final or user-recommended candidates
- projects with hard operational, class-specific, fairness, or calibration constraints

## Inputs

- Project card
- Current frontier record
- Candidate frontier record or run notes
- Evaluator command and metric output
- Fold/seed details when available

## Verdicts

- `PASS`: metric claim is valid enough for recommendation.
- `WARN`: keep the result in the frontier ledger, but do not treat it as a final recommendation without more evidence.
- `FAIL`: metric claim is invalid, misleading, or not comparable.

## Checklist

Objective alignment:

- Does the primary metric match the declared goal?
- Is direction explicit?
- Are secondary constraints honored when specified?

Comparability:

- Same split as frontier?
- Same target definition?
- Same sample weighting?
- Same preprocessing boundary?
- Same evaluator command or compatible metric implementation?

Statistical credibility:

- Is the improvement larger than any declared minimum practical threshold?
- Are fold-level scores, repeated seeds, or confidence intervals needed for a close call?
- Could a single lucky split explain the improvement?

Operational constraints:

- Runtime within budget?
- Memory within budget?
- Inference latency acceptable when specified?
- Calibration, threshold, fairness, or class-specific constraints satisfied when relevant?

Decision:

- Routine loop decisions may advance on validation improvement alone when the evaluator is trusted and no close-call rule applies.
- `WARN` can remain in the frontier ledger but should not become a final recommendation without more evidence.
- `FAIL` should be marked rejected or blocked and followed by a fix path.

## Output

Write a short verdict in the frontier record or a short project-local note:

- verdict
- frontier comparison
- metric deltas
- uncertainty or variance notes
- operational notes
- recommendation decision
