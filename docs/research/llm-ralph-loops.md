# LLM Ralph Loops: Designs and AutoML Implications

Date: 2026-05-27

## Executive Summary

"Ralph loop" is not a single standardized academic architecture. In current usage it means one of two closely related things:

1. A long-running coding-agent harness that repeatedly starts a fresh agent session against a durable task/spec file until external checks pass.
2. A self-evolving discovery loop where the system retrieves prior experience, generates candidates, evaluates them with tools, and distills results back into memory.

For `auto-automl`, the useful synthesis is: keep the agent orchestration markdown-native and portable across Codex, Claude Code, Cursor, etc., but make the evaluation and leakage gates non-negotiable programmatic contracts. The LLM should propose changes, explain hypotheses, and update memory. It should not be trusted to decide that a model is valid without independent checks.

Recommended first design:

```text
task spec -> fresh agent run -> experiment implementation -> train/validation eval
          -> leakage red-team gate -> experiment registry -> distill memory -> next run
```

The loop should optimize the declared objective on validation data while preserving a sealed final holdout that the agent cannot inspect or tune against.

## What "Ralph Loop" Means

The canonical coding-agent version comes from Geoffrey Huntley's Ralph Wiggum technique: a simple external loop repeatedly feeds a prompt/spec into an agent, with fresh context each iteration and durable state in files, git, specs, task lists, and logs. Ralph CLI's docs describe this as keeping an AI coding agent running against an ordered task list with verification and retries. PraisonAI describes the same pattern as fresh context plus file-based persistence, completion markers, and loop/dead-loop controls. Thoughtworks' April 2026 Technology Radar places Ralph loop in "Assess" and emphasizes the fresh-context property as a way to avoid quality degradation from accumulated context.

The newer research/discovery usage is broader. FactorMiner, an ICLR 2026 workshop paper, describes a "Ralph Loop" as retrieve -> generate -> evaluate -> distill: retrieve memory priors, generate candidate factors, evaluate them through deterministic tools, and distill outcomes into experience memory. That is especially relevant to AutoML, because feature engineering and model selection are search problems under noisy, expensive, leakage-prone evaluation.

## Core Design Principles

Durable state over chat memory:
The loop should persist plans, experiment records, data contracts, metrics, failures, and learned heuristics in files. A fresh agent session can then rehydrate only the relevant context.

One meaningful unit per iteration:
The coding-agent Ralph literature strongly favors small iterations: pick one task or one experiment family, execute, validate, record, exit. For AutoML, one unit could be "try a CatBoost baseline with target encoding guarded by fold-only fitting" or "add lagged rolling features with timestamp availability checks."

External backpressure:
The stop condition should be based on tests, metrics, leakage checks, runtime budgets, and reproducible artifacts. The agent's "done" claim is only advisory.

Separation of generator and verifier:
The same LLM can draft ideas and critique them, but validation should be a separate role and, where possible, deterministic code. Red-team agent calls are useful for adversarial review, but they should sit on top of static/runtime checks.

Memory is distilled, not dumped:
Successful and failed trials should be compressed into reusable lessons: dataset profile, what improved the metric, what failed, leakage risks found, time cost, and when a method should be avoided.

## Existing Loop Designs

### 1. External Fresh-Session Ralph

Shape:

```text
while budget remains:
  start fresh agent with PROMPT.md + task state
  agent chooses or receives one task
  agent edits/runs/tests
  harness verifies
  state is updated
```

Strengths:
Good for long-running work, context hygiene, tool portability, and easy debugging. It maps well to a repo made of markdown skills because each skill can be an executable prompt contract.

Risks:
Token cost is high; agents may churn without progress; weak completion checks can let the loop stop too early; over-broad prompts can cause wandering.

AutoML fit:
Use this as the outer loop. Each iteration gets the current experiment board, dataset contract, metric contract, and one candidate direction.

### 2. In-Session ReAct Loop

ReAct interleaves reasoning and tool use: the model reasons, acts, observes tool output, and repeats. FAMOSE applies a ReAct-style loop to automated feature discovery, using iterative feature proposal, evaluation, and refinement.

Strengths:
Good for tight exploratory workflows where the next action depends heavily on the previous observation.

Risks:
The same context window accumulates failed ideas, logs, and incidental details. It can be useful inside one experiment, but should not become the whole long-running system.

AutoML fit:
Use inside a single iteration for local exploration: inspect schema, propose features, run quick validation, refine once or twice, then exit and summarize.

### 3. Self-Refine / Reflexion Loop

Self-Refine uses a model to generate feedback and refine its own output without additional training. Reflexion stores verbal reflections from prior attempts as memory for future attempts. These are useful for writing better experiment plans and postmortems.

Strengths:
Cheap way to improve plans, error analysis, and explanations.

Risks:
Self-critique can sound convincing while missing objective errors. For ML work, it must not replace leakage checks or held-out evaluation.

AutoML fit:
Use as a post-experiment reflection step: "what did this trial teach us, what should never be repeated, and what exact hypothesis should be tested next?"

### 4. Tree / Search Loop

Tree of Thoughts and later systems explore multiple candidate reasoning paths, score them, and backtrack. CoFEH uses a Tree-of-Thought-inspired LLM feature-engineering optimizer interleaved with Bayesian hyperparameter optimization.

Strengths:
Good when search space is large and early choices constrain downstream options.

Risks:
Expensive. Without strict evaluator isolation, it can over-optimize to a noisy validation slice.

AutoML fit:
Use when choosing among feature families, model classes, or preprocessing strategies. Keep the tree shallow and score candidates through the same validation API.

### 5. Multi-Agent Specialist Loop

AutoML-Agent decomposes full-pipeline AutoML into specialized agents for planning, data preprocessing, neural network design, code generation, and multi-stage verification. This is conceptually close to a team of markdown skills.

Strengths:
Clear role boundaries; specialists can have tighter instructions; verification can be explicit.

Risks:
More orchestration complexity, more places for stale assumptions, and more context handoff failure.

AutoML fit:
Use specialist skills, not a chatty agent swarm. For example: `data-profile`, `feature-engineer`, `model-search`, `leakage-auditor`, `metric-reviewer`, `experiment-distiller`.

### 6. Evolutionary / Programmatic Evaluator Loop

AlphaEvolve-style systems use LLMs to propose code/program variants, evaluate them automatically, and feed promising variants back into future prompts. This pattern is directly applicable to model and feature search when the evaluator is reliable.

Strengths:
The LLM becomes a creative mutation operator while metrics and tests do the selection.

Risks:
The loop will exploit evaluator flaws. In ML, that means leaderboard overfit, validation leakage, shortcut features, time leakage, or accidental training on test data.

AutoML fit:
Use for bounded candidate generation: feature transforms, model configs, ensembling recipes, and training code. Gate each candidate with leakage and reproducibility checks before admission.

## AutoML-Specific Failure Modes

The main danger is not that the LLM picks a weak model. The main danger is that the loop learns how to exploit an evaluation surface that does not represent future data.

Critical failure modes:

- Train/eval/test leakage: fitting preprocessors, imputers, scalers, encoders, selectors, or feature generators on data outside the training fold.
- Training on the test set: direct inclusion, accidental joins, cached artifacts, or repeated "final" scoring that turns the test set into a tuning set.
- Target leakage: features that encode the label, future outcome, post-event information, or proxies unavailable at prediction time.
- Temporal leakage: random splits on time-dependent data, rolling features that peek forward, or features computed with full-period aggregates.
- Entity leakage: same user/customer/device/patient/order family appearing in train and evaluation splits when deployment requires entity-level generalization.
- Multi-test leakage: repeated validation/leaderboard probing without accounting for search budget.
- Metric gaming: optimizing the wrong metric, a metric with unstable confidence intervals, or a metric that ignores calibration, class imbalance, cost, latency, or fairness constraints.
- Data contamination from generated artifacts: features, labels, or metadata derived from evaluation data during exploratory analysis.
- Irreproducible wins: random seeds, nondeterministic GPU ops, unpinned data snapshots, or incomplete experiment manifests.

Scikit-learn's common pitfalls guidance is blunt on this point: split before preprocessing, never call `fit`/`fit_transform` on test data, and use pipelines to keep transformations inside the right fold. Its nested cross-validation guidance also warns that model selection and performance estimation on the same data produces optimistic scores.

## Proposed `auto-automl` Loop Architecture

### Repository-Level Artifacts

```text
skills/
  automl-loop.md
  data-profile.md
  feature-engineer.md
  model-search.md
  leakage-auditor.md
  metric-reviewer.md
  experiment-distiller.md

experiments/
  README.md
  registry.jsonl
  runs/<run_id>/
    manifest.json
    plan.md
    metrics.json
    leakage_report.md
    notes.md

docs/
  research/
```

The skills should be plain markdown so different coding agents can run them. The experiment registry should be structured so non-LLM tools can audit it.

### Iteration Contract

Each iteration should have a strict contract:

```text
Inputs:
  dataset contract
  split contract
  metric contract
  current leaderboard
  prior distilled lessons
  one candidate hypothesis

Agent actions:
  implement one experiment
  run training/evaluation only through approved commands
  write manifest and notes

Verifier actions:
  run reproducibility check
  run leakage audit
  run metric audit
  decide admit/reject

Outputs:
  metrics.json
  leakage_report.md
  experiment summary
  distilled memory update
```

### Leakage-Auditor Skill Scope

The leakage auditor should be adversarial and specific. It should ask:

- Are split files immutable and referenced by ID/hash?
- Can any code path access sealed test labels or features?
- Does every preprocessing/feature step fit only on the training fold?
- Are target encoders, imputers, scalers, PCA/feature selectors, oversamplers, and text/vectorizers inside a pipeline or fold loop?
- For time-series tasks, does every feature have an availability timestamp and a nonnegative prediction horizon?
- For grouped data, are groups isolated across folds?
- Are duplicates or near-duplicates crossing split boundaries?
- Has the validation set been queried enough times to require budget penalties or a refreshed split?
- Are cached features keyed by split/fold to prevent cross-run contamination?
- Is the final holdout still sealed?

The auditor should produce a blocking verdict: `PASS`, `WARN`, or `FAIL`. `FAIL` prevents leaderboard admission.

### Metric-Reviewer Skill Scope

The metric reviewer should check:

- The objective matches the user-specified business/scientific goal.
- Metric direction is explicit: maximize or minimize.
- Confidence intervals or repeated-seed variance are reported for close calls.
- Baselines are present.
- Runtime, memory, and inference cost are tracked if relevant.
- The model is not selected only on a single lucky split.
- The claimed improvement clears a minimum practical effect threshold.

### Memory Distillation

Do not append full logs to the prompt forever. Distill each run into a compact record:

```json
{
  "run_id": "...",
  "dataset_hash": "...",
  "hypothesis": "...",
  "changes": ["..."],
  "metric_delta": {"validation_auc": 0.004},
  "leakage_verdict": "PASS",
  "cost": {"train_seconds": 93},
  "lesson": "Target encoding helped only when nested inside CV folds.",
  "avoid": "Do not compute category means before splitting."
}
```

Over time this becomes the loop's retrieval memory: successful patterns, forbidden patterns, and dataset-specific warnings.

## Design Recommendation

Start with a simple, portable markdown-driven Ralph loop rather than a full multi-agent runtime. The minimum viable system should have:

- A single outer fresh-session loop skill: `automl-loop.md`.
- A structured experiment registry.
- A deterministic validation command.
- A leakage-auditor skill with blocking power.
- A metric-reviewer skill with blocking power.
- A distillation step that writes compact memory.

Do not expose the sealed test set to normal loop iterations. A human or a separate release gate should trigger final test evaluation after the loop has stopped selecting models.

The key product idea is not "an LLM does AutoML." The stronger idea is "an LLM proposes and maintains an AutoML search process, while programmatic evaluators and adversarial skill calls prevent the classic ways AutoML lies to itself."

## Open Questions For This Project

- Should this repo stay agent-agnostic markdown only, or include a thin harness for Codex/Claude/Aider-style CLIs?
- What is the first target task class: tabular classification/regression, time series, NLP, vision, or arbitrary sklearn-style supervised learning?
- Should experiment execution use an existing AutoML engine such as AutoGluon/FLAML/Optuna as a tool, or should the loop initially generate plain Python experiments?
- How hard should the sealed holdout boundary be: filesystem permission boundary, separate process, separate credential, or social convention?
- What should count as "done": best validation score, exhausted budget, no significant improvement, or passing a deployment-readiness checklist?

## Source Notes

- Geoffrey Huntley, "Ralph Wiggum as a software engineer" - original fresh-context loop discussion and AGENT.md/self-improvement pattern: https://ghuntley.com/ralph/
- Ralph CLI docs, "Ralph loop" - PRD/task-list loop with verification and retries: https://ralph-cli.dev/docs/core-concepts/ralph-loop/
- Ralph Loop CLI page - task list, Docker sandboxes, multi-agent CLI support, logs, and steering file: https://ralphloop.sh/
- PraisonAI, "Ralph Loops" - fresh context, file-based state, completion promises, loop controls: https://docs.praison.ai/docs/concepts/ralph-loops
- Thoughtworks Technology Radar, Vol. 34, "Ralph loop" - fresh context each iteration, spec/plan-driven coding, token-cost caution: https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2026/04/tr_technology_radar_vol_34_en.pdf
- Wang et al., "FactorMiner: A Self-Evolving Agent with Skills and Experience Memory for Financial Alpha Discovery" - retrieve/generate/evaluate/distill Ralph loop: https://openreview.net/forum?id=TTsecyqrW3
- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" - reasoning/action/observation agent loop: https://arxiv.org/abs/2210.03629
- Madaan et al., "Self-Refine: Iterative Refinement with Self-Feedback" - generate/feedback/refine without training: https://arxiv.org/abs/2303.17651
- Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning" - reflection memory from feedback: https://arxiv.org/abs/2303.11366
- Yao et al., "Tree of Thoughts" - search over intermediate thoughts with evaluation/backtracking: https://arxiv.org/abs/2305.10601
- Yang et al., "SWE-agent" - agent-computer interfaces for coding agents: https://arxiv.org/abs/2405.15793
- Zhang et al., "AutoML-GPT" - LLM-driven automated training pipeline from data processing to HPO: https://arxiv.org/abs/2305.02499
- Trirat et al., "AutoML-Agent" - multi-agent full-pipeline AutoML with specialized agents and verification: https://arxiv.org/abs/2410.02958
- Hollmann et al., "CAAFE" - LLM-generated semantic tabular features: https://arxiv.org/abs/2305.03403
- Xu et al., "CoFEH" - LLM feature engineering interleaved with Bayesian HPO: https://arxiv.org/abs/2602.09851
- Burghardt et al., "FAMOSE" - ReAct-based automated feature discovery: https://arxiv.org/abs/2602.17641
- Google DeepMind, "AlphaEvolve" - LLM-generated code variants selected by automated evaluators: https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- scikit-learn, "Common pitfalls and recommended practices" - data leakage and preprocessing split guidance: https://scikit-learn.org/stable/common_pitfalls.html
- scikit-learn, "Nested versus non-nested cross-validation" - model selection/evaluation leakage and optimistic bias: https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html
- OWASP Top 10 for LLM Applications - prompt injection, data poisoning, excessive agency, and related LLM risks: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OWASP Agentic Skills Top 10 - skill/runtime security checklist for agent execution layers: https://owasp.org/www-project-agentic-skills-top-10/
- OWASP Top 10 for Agentic Applications 2026 - agent goal hijack, tool misuse, memory/context poisoning, cascading failures: https://genai.owasp.org/download/52117/
