# Autoresearch Pattern: Unattended Metric-Driven Agent Search

Date: 2026-05-28

## Executive Summary

Karpathy's `autoresearch` is a compact example of an agentic research loop that works because it is aggressively constrained:

```text
human programs markdown instructions -> agent edits one training file
  -> fixed-time training run -> fixed validation metric
  -> keep improvement or discard change -> repeat until interrupted
```

The main lesson for `auto-automl` is not "remove the safety gates." The lesson is that autonomy improves when the loop has a clearly bounded change surface, a trusted evaluator, simple frontier advancement, and no need to ask the human between experiments.

For this repository, the useful adaptation is an explicit unattended application loop:

```text
while stop policy is not satisfied and user has not interrupted:
  launch or continue an AutoML worker session
  run one bounded experiment or search family
  evaluate only on approved validation data
  advance or discard the validation frontier
  append one compact frontier record
  escalate leakage or metric review only when risk changes
```

The `autoresearch` keep/discard frontier can be copied. General AutoML still needs split, holdout, preprocessing, and metric safeguards, but those safeguards should protect the evaluator rather than turn every routine iteration into a release review.

## What `autoresearch` Does

`autoresearch` is a small autonomous LLM-training experiment repository. Its README describes the core loop as: an agent modifies code, trains for five minutes, checks whether the result improved, keeps or discards the change, and repeats. The repo intentionally centers on three files:

- `prepare.py`: fixed data preparation, tokenizer, dataloader, and evaluation utilities.
- `train.py`: the single mutable file the agent edits.
- `program.md`: the markdown instruction file that defines the agent's behavior.

The default task is single-GPU nanochat-style pretraining. Each experiment runs under a fixed five-minute wall-clock training budget, excluding startup and compilation. The metric is validation bits per byte, `val_bpb`, where lower is better.

The default `program.md` turns the loop into a branch-frontier search:

1. Create a dedicated `autoresearch/<tag>` branch.
2. Establish a baseline.
3. Edit `train.py`.
4. Commit the experimental change.
5. Run `uv run train.py > run.log 2>&1`.
6. Extract `val_bpb` and peak VRAM from the log.
7. Record the result in `results.tsv`.
8. If `val_bpb` improved, keep the commit and advance the branch.
9. If `val_bpb` is equal or worse, reset to the previous frontier.
10. Continue indefinitely until the human interrupts.

That is a hill-climbing/evolutionary agent loop with git as the frontier store and a TSV as the experiment ledger.

## Why The Pattern Works

The strongest design choices are simple:

Clear change boundary:
The agent edits the candidate generator while the evaluator remains fixed. In `autoresearch`, that boundary is expressed as "edit `train.py`, do not edit `prepare.py`." The same boundary can be cleaner as a set of modules, as long as data loading, split definitions, metric computation, budget, and result accounting are not casually changed by the search loop.

Fixed evaluator:
`prepare.py` owns data loading and evaluation, and `program.md` tells the agent not to modify it. This gives the loop a stable selection rule.

Fixed budget:
Every candidate gets the same training-time budget. The metric therefore compares "best model after five minutes on this machine," not "best model after arbitrary compute."

Fast cadence:
Five-minute experiments create enough selection pressure for overnight progress. The loop is optimized for many practical tries, not one perfect research plan.

Unattended continuation:
The instruction to continue until interrupted removes human confirmation from the critical path. This is essential if the product promise is "run while the human sleeps."

Git frontier:
Keeping winning commits and reverting losing commits gives the loop a concrete current best state. It avoids accumulating unrelated failed edits in the codebase.

Lightweight ledger:
`results.tsv` is small enough for the agent to reread and compare. It records enough to avoid total amnesia without turning into a long prompt log.

Human-programmed research org:
The human primarily edits `program.md`, not Python. The prompt becomes the "research org code": taste, constraints, logging rules, and continuation policy.

## Why It Is Different From A General AutoML Loop

`autoresearch` can be minimal because its problem boundary is narrow:

- one model-training script
- one training domain
- one metric
- one validation split
- one hardware target
- one dependency set
- one fixed evaluator
- no feature joins, target encoders, entity splits, or timestamp availability semantics

General AutoML has a wider failure surface. A tabular AutoML agent can accidentally fit preprocessors on validation data, leak labels through derived columns, use future information, split related entities across folds, tune against a final test set, or hide failed validation probes. In that setting, "metric went down, keep it" is necessary but not sufficient.

So the `autoresearch` pattern should influence `auto-automl` at the orchestration level, not weaken the evaluation-integrity layer.

## Mapping To `auto-automl`

Useful direct mappings:

- `program.md` maps to `AGENTS.md`, `project_card.md`, and markdown skills.
- `train.py` maps to project-local experiment code under `projects/<project_id>/`.
- `prepare.py` maps to fixed split/evaluator code and the project card.
- `val_bpb` maps to the project card's primary validation metric.
- `results.tsv` maps to `projects/<project_id>/experiments/frontier.jsonl`.
- "keep winning commit, reset loser" maps to frontier advancement and optional discard/revert.
- "never stop until interrupted" maps to an unattended application loop governed by `project_card.md`.

Important differences:

- `auto-automl` should not put task-specific files at repo root.
- `auto-automl` should not recommend or certify a run just because validation improved.
- `auto-automl` needs explicit leakage and metric review gates for setup changes, high-risk changes, surprising jumps, and final/recommended candidates.
- `auto-automl` should preserve a sealed final holdout outside normal search.
- `auto-automl` should keep the core markdown and project records runtime-agnostic; any always-on runner belongs in a host harness or optional extension pack.

## Recommended Adaptation

Add an explicit `autoresearch`-style unattended mode to the project guidance:

```text
Unattended mode:
  Continue launching AutoML worker sessions until one of these happens:
    - the project card stop policy is satisfied
    - the runtime/search budget is exhausted
    - a blocking split/evaluator/holdout issue prevents valid progress
    - the human interrupts the loop
```

The worker itself should still report one iteration cleanly. The application loop should be allowed to relaunch workers automatically.

For a host that can create fresh agent processes, prefer:

```text
host loop:
  start fresh agent with AGENTS.md + project_card.md + frontier.jsonl
  wait for worker report
  inspect stop policy
  repeat unless stopped
```

For an interactive Codex or Claude Code session where fresh relaunch is not available, allow:

```text
single-session unattended loop:
  keep iterating in the same chat
  keep context small and append frontier rows
  avoid flooding context with logs
  stop only on stop policy, blocking issue, budget, or human interrupt
```

The first version is more faithful to Ralph fresh-context principles. The second version is closer to `autoresearch` operator ergonomics and is often what users actually mean when they ask an agent to "keep going."

## Suggested Project Card Additions

The project card should include:

- `mode`: `single_worker` or `unattended`
- `max_experiments`
- `max_wall_clock_hours`
- `max_validation_probes`
- `minimum_practical_improvement`
- `stop_when_no_improvement_after`
- `final_holdout_release_gate`
- `evaluator_command`
- `frontier_ledger`

The worker report should include:

- current frontier run
- whether the latest candidate advanced the frontier
- stop policy status
- validation probe count
- next hypothesis
- whether unattended continuation is allowed

The frontier ledger should distinguish:

- `advanced`: candidate became the current frontier
- `kept`: candidate did not advance but is useful to preserve
- `discarded`: candidate was worse and not useful
- `blocked`: candidate could not be evaluated or violated a guard

## Practical Guidance For This Repo

Adopt from `autoresearch`:

- unattended continuation when explicitly requested
- clear mutable/evaluation boundaries per project
- a fixed evaluator per project
- fixed per-experiment budget
- append-only compact result ledger
- frontier advancement semantics
- markdown as the place where humans program the research behavior

Do not adopt directly:

- root-level task artifacts
- unrestricted repeated validation probing
- reset-based discard as the only record of failed attempts
- no separate leakage audit for risky or final candidates
- no sealed final holdout
- one universal always-on runner in core

The best product direction is:

```text
portable project cards + markdown skills
  + optional unattended host loop
  + autoresearch-style frontier advancement
  + AutoML-specific leakage and metric escalation gates
```

## Source Notes

- Karpathy, `autoresearch` README: https://github.com/karpathy/autoresearch/blob/master/README.md
- Karpathy, `autoresearch` program instructions: https://github.com/karpathy/autoresearch/blob/master/program.md
- Karpathy, `autoresearch` fixed data/evaluation code: https://github.com/karpathy/autoresearch/blob/master/prepare.py
- Karpathy, `autoresearch` mutable training script: https://github.com/karpathy/autoresearch/blob/master/train.py
