# Claude Code Dynamic Workflows And AutoML Runtime Fit

Date: 2026-05-28

## Executive Summary

Claude Code dynamic workflows look like the closest Claude-native runtime for the outer `auto-automl` application loop so far. They let Claude write a JavaScript orchestration script, run many subagents in the background, preserve intermediate results outside the main conversation, and save a successful workflow as a reusable command.

For this repository, the useful framing is:

```text
dynamic workflows may be a serious candidate runtime for the concept
the open question is whether the concept should stay runtime-agnostic,
become Claude Code-first, or support both through generated adapters
```

They are a strong fit for:

- running several independent hypothesis scouts or reviewers in parallel
- coordinating one bounded worker session from project card to frontier update
- adding adversarial leakage and metric review around a candidate
- saving a Claude-specific reusable command under `.claude/workflows/`

They are not enough by themselves for:

- a runtime-agnostic Ralph loop across Codex, Claude Code, Cursor, Aider, and future hosts
- deterministic validation, stop-policy enforcement, or holdout protection
- durable continuation after the Claude Code session exits
- safe concurrent file edits unless isolation is handled deliberately

This should be treated as concept evidence, not as a legacy-preservation problem. The current project card, frontier ledger, evaluator, and holdout boundary are useful design primitives to test against the workflow runtime, but they are not settled architecture just because they exist in the repo today.

## What The Feature Is

Dynamic workflows are a research-preview Claude Code feature announced on 2026-05-28. The announcement describes them as a way for Claude to write orchestration scripts that run tens to hundreds of parallel subagents in one session, with cross-checking before results are returned.

The documentation is more concrete:

- A workflow is a JavaScript script written by Claude.
- The workflow runtime executes the script in an isolated environment separate from the conversation.
- The script coordinates subagents; the script itself does not directly read files or run shell commands.
- Agents do the file reads, edits, shell commands, web fetches, and MCP work allowed by the user's configuration.
- Intermediate results live in script variables instead of flooding the main context.
- Runs are background tasks that can be inspected through `/workflows`.
- A workflow can be saved as a reusable slash command in `.claude/workflows/` or `~/.claude/workflows/`.

Availability is version-, plan-, and admin-sensitive. The workflow docs say Claude Code v2.1.154 or later is required and that workflows are available on paid plans and provider/API surfaces. The launch post describes CLI, Desktop, VS Code, API, Amazon Bedrock, Vertex AI, and Microsoft Foundry availability, with Enterprise admin controls. Treat this as current but volatile product behavior.

## Fit Against The `auto-automl` Concept

`auto-automl` wants this shape:

```text
project card -> bounded worker move -> fixed validation evaluator
             -> frontier ledger update -> repeat until stop policy
```

Dynamic workflows map well to the orchestration part:

| `auto-automl` need | Dynamic workflow fit |
| --- | --- |
| Fresh-ish worker contexts | Good: subagents get separate contexts. Not identical to fresh CLI sessions. |
| Durable loop state | Good if state remains in `project_card.md` and `frontier.jsonl`; weak if state lives only in workflow variables. |
| Parallel candidate search | Good for read-only hypothesis scouting; risky for concurrent edits without worktrees. |
| Validation evaluator | Good as a command agents run, but the evaluator must stay project-defined. |
| Frontier advancement | Good if exactly one coordinated agent appends/updates the ledger after evaluation. |
| Leakage and metric review | Strong fit for independent adversarial review agents. |
| Stop policy | Good if read from the project card; bad if replaced by Claude's own done judgment. |
| Runtime portability | Poor: this is Claude-specific and research-preview. |

The main distinction from a classic Ralph loop is that workflows keep orchestration inside one Claude Code session, while Ralph-style loops usually relaunch fresh agent sessions from an external harness. Dynamic workflows still improve context hygiene because subagent work and intermediate results do not accumulate in the main conversation, but they are not a full external process supervisor.

## Recommended Claude Workflow Shape

A Claude-specific AutoML workflow should be conservative:

```text
phase 1: read AGENTS.md, README.md, projects/README.md
phase 2: read project_card.md and frontier.jsonl
phase 3: stop immediately if the project card stop policy is satisfied
phase 4: spawn small read-only scouts for next hypotheses or failure diagnosis
phase 5: choose one bounded candidate move
phase 6: run one implementation/evaluation worker
phase 7: run leakage or metric reviewers only when the repo rules require escalation
phase 8: append one compact frontier record
phase 9: report whether the application loop should continue and the next hypothesis
```

This keeps the workflow aligned with the repo's worker-session contract instead of turning a single workflow run into an unbounded AutoML swarm.

For a higher-throughput mode, use parallelism only where the candidates are isolated:

```text
parallel scouts:
  read-only, no edits

parallel experiment workers:
  only if each worker gets an isolated worktree or project-local scratch directory
  each writes a separate candidate result
  one coordinator selects whether the frontier advances
```

Without that isolation, concurrent agents can overwrite each other's files, contaminate caches, or append conflicting ledger rows.

## Integration Shapes To Consider

There are at least three plausible integration shapes:

1. **Claude Code-first runtime:** Make dynamic workflows the main execution target and design the repo's markdown around generating or guiding `.claude/workflows/` scripts.
2. **Portable core plus Claude adapter:** Keep the existing markdown/project-card/frontier design as the common contract and add Claude workflows as one host implementation.
3. **Workflow-derived redesign:** Use dynamic workflows to simplify the concept, then back-port only the durable pieces that remain useful across runtimes.

A Claude-specific package could look like:

```text
extensions/claude-dynamic-workflows/
  README.md
  skills/
    claude-automl-workflow.md
  workflows/
    automl-worker-session.md
    automl-hypothesis-scouts.md
    automl-review-gate.md
```

If the project goes Claude Code-first, the same assets might instead live directly under `.claude/workflows/` with the markdown skills serving as source material or generation prompts. That is a product decision, not a backwards-compatibility constraint.

## Safety And Integrity Considerations

The feature is powerful exactly where AutoML is fragile: it makes many agents and many validation probes cheap to launch. That raises the risk of overfitting the validation split, hiding failed probes, and converging on evaluator quirks.

Guardrails that must remain non-negotiable:

- The project card owns target, split, metric, evaluator command, holdout rule, and stop policy.
- Normal workflow runs may optimize validation metrics only.
- The sealed final holdout must not be queried during model search.
- Split, evaluator, and data-availability changes require blocking review.
- Frontier records must remain append-only and compact.
- Any candidate that advances the frontier must be reproducible from code state, command/config, and metrics.

Workflow-specific risks:

- **Token and cost blowup:** dynamic workflows can spawn many agents and consume substantially more usage than normal sessions.
- **Permission surprise:** subagents run with inherited/allowed tools, and file edits may be auto-approved in some modes.
- **No mid-run user input:** only permission prompts pause a run; sign-off checkpoints should be separate workflows.
- **No direct script tools:** the JavaScript orchestration layer cannot itself inspect files or run shell commands, so all concrete work must be delegated to agents.
- **Session-bound resume:** paused workflows can resume within the same Claude Code session, but exiting Claude Code starts fresh.
- **Concurrency limit:** docs list up to 16 concurrent agents and 1,000 total agents per run, so designs should budget parallelism explicitly.

## Comparison With Other Claude Mechanisms

Dynamic workflows sit between subagents, agent teams, and an external `claude -p` or Agent SDK harness:

| Mechanism | Best use | Runtime fit |
| --- | --- | --- |
| Subagents | Focused delegated tasks that return summaries | Good inner worker primitive |
| Agent teams | Interactive collaboration between independent Claude Code sessions | Good for human-supervised exploration, heavier than needed for routine AutoML |
| Worktrees | File isolation for parallel sessions | Important when multiple candidates edit code |
| `claude -p` / Agent SDK | External script launches and monitors sessions | Better for a true portable-ish Ralph harness |
| Dynamic workflows | Scripted orchestration of many subagents inside Claude Code | Best Claude-native fit for an optional AutoML runner |

For a runtime-agnostic design, an external harness is still cleaner because it can enforce stop policy, launch fresh sessions, and remain independent of any one coding-agent product. For a Claude Code-first design, dynamic workflows are probably the most practical host and may remove the need to invent a separate runner.

## Product Direction Questions

Dynamic workflows make the runtime question sharper rather than settling it. The next useful step is to decide which product bet this repo wants to explore first.

Key questions:

- Should the first runnable version target Claude Code specifically, because workflows provide orchestration, resumability, visibility, and saved commands?
- Are project cards and frontier ledgers still the right durable state if the workflow script can hold intermediate state and coordinate agents directly?
- Should workflow scripts be checked in as first-class source, generated from markdown skills, or produced dynamically by Claude per project?
- Can parallel experiment workers be made safe enough with worktrees or per-candidate project directories?
- What deterministic checks should live outside Claude's workflow runtime so evaluation integrity does not depend on agent self-report?

Concrete prototype:

```text
Build one Claude Code dynamic workflow for a toy project:
  read project state
  spawn read-only hypothesis scouts
  choose one candidate
  run one isolated implementation/evaluation worker
  run reviewer agents only if the candidate touches evaluator/split risk
  append a frontier record or equivalent durable result
  report whether another workflow run should start
```

That prototype would answer whether Claude's workflow runtime can carry the application-loop concept directly, or whether an external harness is still needed.

The concise product answer:

```text
Yes, this might be the runtime the concept can run in.
Do not treat the current runtime-agnostic shape as a legacy obligation.
Use a prototype to decide whether Claude workflows should become the main path,
an adapter path, or the source of a redesign.
```

## Source Notes

- Claude launch post, "Introducing dynamic workflows in Claude Code": https://claude.com/blog/introducing-dynamic-workflows-in-claude-code
- Claude Code docs, "Orchestrate subagents at scale with dynamic workflows": https://code.claude.com/docs/en/workflows
- Claude Code docs, "Create custom subagents": https://code.claude.com/docs/en/sub-agents
- Claude Code docs, "Orchestrate teams of Claude Code sessions": https://code.claude.com/docs/en/agent-teams
- Claude Code docs, "Run parallel sessions with worktrees": https://code.claude.com/docs/en/worktrees
- Claude Code docs, "Run Claude Code programmatically": https://code.claude.com/docs/en/headless
- Existing repo note, "Autoresearch Pattern: Unattended Metric-Driven Agent Search": `docs/research/autoresearch-pattern.md`
- Existing repo note, "Coding Agent Goal Behavior": `docs/research/coding-agent-goal-behavior.md`
