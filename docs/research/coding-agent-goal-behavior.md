# Coding Agent Goal Behavior

Date: 2026-05-28

## Executive Summary

`/goal` features in coding-agent apps are current-session continuation controls. They help an agent keep working toward a user-stated end condition without a new prompt after every turn. They are useful for long tasks with observable completion criteria, but they are not a full Ralph loop.

For `auto-automl`, treat app-level goals as a convenience for running one bounded worker session. Do not let a Codex or Claude Code goal replace the project stop policy in `projects/<project_id>/experiments/metric_contract.md`, the split contract, leakage gates, metric review, or durable registry/memory records.

The key distinction:

```text
app /goal: current thread keeps working until an app-level condition appears satisfied
Ralph loop: external harness starts fresh workers, checks durable contracts, records state
```

## Behavior Observed In Current Apps

### Codex

Codex documents Goal mode as a persistent objective for longer tasks. The goal text acts as both the starting prompt and the completion criteria. Codex uses the goal to decide what to do next and whether the task is complete.

In the Codex app, `/goal` is available from the composer. The app shows a progress row above the composer while a goal is active, with controls to pause, resume, edit, or clear the goal. Codex recommends using `/plan` first when the goal needs shaping before execution.

In the Codex CLI, `/goal <objective>` sets the active task goal, `/goal` views it, and `/goal pause`, `/goal resume`, and `/goal clear` manage it. Goal objectives are limited to 4,000 characters; longer instructions should live in a file that the goal references. `/goal` is an interactive slash command, not a top-level `codex goal` subcommand. On the local machine checked for this note, `codex-cli 0.125.0` reports `codex goal` as an unrecognized subcommand.

If `/goal` is not visible, Codex docs say to enable:

```toml
[features]
goals = true
```

or run:

```sh
codex features enable goals
```

### Claude Code

Claude Code documents `/goal [condition|clear]` as a session-scoped completion condition. Claude keeps working across turns until the condition is met. The docs state that `/goal` requires Claude Code `v2.1.139` or later. On the local machine checked for this note, `claude --version` reports `2.1.119`, which is below that documented requirement.

Claude Code's `/goal` differs from Codex in one important documented implementation detail: after each turn, a small fast model checks whether the condition holds. If it says no, Claude starts another turn; if yes, the goal clears. The evaluator sees the conversation so far but does not run commands or read files independently, so the worker must surface proof in the transcript.

Claude Code presents `/goal` as one of several autonomous-workflow mechanisms:

- `/goal`: next turn starts when the previous turn finishes; stops when a model confirms the condition is met.
- `/loop`: next turn starts on an interval or self-paced repeat; stops when the user stops it or Claude decides it is done.
- Stop hook: next turn starts when the previous turn finishes; stops when a configured script or prompt decides.

Claude Code also supports non-interactive use with a prompt such as:

```sh
claude -p "/goal CHANGELOG.md has an entry for every PR merged this week"
```

### Cursor And Aider

Cursor CLI's public slash-command reference lists controls such as `/model`, `/auto-run`, `/new-chat`, `/resume`, and `/help`, but does not list a `/goal` command. That means Cursor has adjacent autonomy controls, but not a documented goal-condition loop under that name.

Aider's public in-chat command list includes commands such as `/run`, `/test`, `/lint`, `/architect`, `/ask`, `/code`, and `/load`, but does not list `/goal`. Aider can automatically lint and test after edits with configured commands, which is useful verification backpressure, but it is not the same as a persistent app-level completion condition.

## Taxonomy

### Single-Turn Agent Loop

Most coding agents already run a local ReAct-style loop inside one assistant turn: inspect files, edit, run commands, observe output, and continue until the model decides it is done or the user interrupts.

This is useful for normal coding tasks, but it inherits the same context and self-assessment limitations as the active thread.

### Current-Session Goal Loop

Codex `/goal` and Claude Code `/goal` live here. They keep the same session moving across multiple turns. They are best for tasks with a compact, observable end state, such as:

- all tests in a named suite pass
- a migration compiles in strict mode
- a backlog file has no unchecked items
- a report exists and a verification command exits zero

They are weaker when success depends on hidden state, external policy, statistical validity, or evidence that was not put into the transcript.

### Scripted Stop Hook Or Deterministic Gate

Claude Code Stop hooks and repo-local verification scripts are closer to a durable control surface because a script can inspect files, run commands, and return a deterministic decision. For `auto-automl`, deterministic gates should check metric artifacts, registry schema, split hashes, leakage reports, and final-holdout access policy.

Prompt-based stop hooks still have the same transcript-evidence limitation as model-evaluated goals.

### External Ralph Loop

A Ralph loop is an external orchestration pattern:

```text
durable task/spec state -> fresh agent session -> one worker move
                         -> verification -> registry/memory update
                         -> stop-policy check -> maybe launch next worker
```

Its important property is not just "keep going." It is fresh-context repetition governed by files, metrics, tests, and explicit stop policy. That makes it a better outer loop for AutoML.

## Comparison For AutoML Use

| Mechanism | Scope | Stop Decision | Evidence Source | AutoML Fit |
| --- | --- | --- | --- | --- |
| Codex `/goal` | Active Codex thread | Codex judges the goal text and task state | Current thread context and surfaced tool results | Good for one bounded worker session |
| Claude Code `/goal` | Active Claude Code session | Small fast model evaluates the condition after each turn | Conversation transcript only | Good for one bounded worker session if proof is printed |
| Claude Code Stop hook | Configured hook scope | Script or prompt decides | Script can inspect workspace; prompt sees supplied context | Good for deterministic worker/session gates |
| Claude Code `/loop` | Active session | User stop or Claude's own done judgment | Current session context | Useful for polling or repeated maintenance, weak as an ML stop policy |
| Cursor `/auto-run` | Active Cursor CLI session | Tool-call approval behavior, not a goal condition | Current session context | Useful for reducing prompts, not a stop policy |
| Aider auto-lint/test | Active aider session | Command failures feed repair attempts | Lint/test command output | Useful inner feedback, not an outer loop |
| Ralph loop | External harness | Project contracts and verification gates | Durable files, commands, registry, memory | Best outer loop for `auto-automl` |

## Recommended `auto-automl` Usage

Use app goals to run exactly one worker session:

```text
/goal Run one AutoML worker session for project <project_id> following AGENTS.md.
Read the dataset, split, and metric contracts. If the project stop policy is already
satisfied, report the reason and stop. Otherwise make one practical unit of progress,
apply leakage and metric gates for any promoted candidate, update durable state, and
finish by reporting application_loop_status and the next recommended hypothesis.
Do not inspect or optimize against sealed final holdout metrics.
```

For Claude Code, phrase the condition so the evaluator can judge transcript evidence:

```text
/goal The transcript shows that one AutoML worker session for project <project_id>
completed: it reports the current best admitted run, whether the metric-contract stop
policy says continue or stop, any leakage/metric gate verdict for promoted candidates,
and the next recommended hypothesis if continuing.
```

For Codex, keep the objective similarly bounded and concrete, and prefer a file-backed run plan when the instructions exceed the 4,000-character goal limit.

## Failure Modes

Goal drift:
The app-level goal can become broader than the intended worker unit. Bound it with "one worker session" and require a final status report.

Evaluator optimism:
A model-evaluated goal can accept a convincing summary that is missing real evidence. Require commands, artifact paths, metric summaries, and gate verdicts in the transcript.

Transcript-only blindness:
Claude Code documents that the goal evaluator does not run tools. If the worker forgets to print a test result or path, the evaluator may not have enough evidence.

Stop-policy substitution:
The agent may treat "the goal is done" as "the AutoML project is done." In this repo, only `projects/<project_id>/experiments/metric_contract.md` defines project stop conditions.

Context accumulation:
App goals keep the same active session running. For long AutoML searches, stale context and incidental logs can bias future choices. Use Ralph-style fresh workers for the outer application loop.

Validation leakage:
Repeated app-goal iterations can overfit validation metrics if the metric contract does not limit search budget and leakage review. Every admitted candidate still needs the leakage-auditor and metric-reviewer gates.

## Design Recommendation

Keep core skills portable markdown. Do not bake Codex `/goal`, Claude Code `/goal`, hooks, or scheduled tasks into the core AutoML loop.

If tool-specific support is added later, put it in optional extension packs:

- `codex-goal-pack`: recommended `/goal` prompts, feature flag notes, and app/CLI controls.
- `claude-goal-pack`: `/goal` conditions, Stop hook examples, and transcript-proof requirements.
- `ralph-harness-pack`: external fresh-session launcher, budget controls, dead-loop detection, and durable stop-policy checks.

The repo's invariant should remain:

```text
host app goals may drive a worker
metric contracts decide project completion
leakage and metric review decide registry admission
sealed final holdout remains outside normal loops
```

## Source Notes

- OpenAI Codex prompting guide, "Goal mode": https://developers.openai.com/codex/prompting
- OpenAI Codex app commands, `/goal`: https://developers.openai.com/codex/app/commands
- OpenAI Codex CLI slash commands, `/goal`: https://developers.openai.com/codex/cli/slash-commands
- Claude Code docs, "Keep Claude working toward a goal": https://code.claude.com/docs/en/goal
- Claude Code command reference, `/goal`, `/loop`, and related commands: https://code.claude.com/docs/en/commands
- Cursor CLI slash commands: https://docs.cursor.com/en/cli/reference/slash-commands
- Aider in-chat commands: https://aider.chat/docs/usage/commands.html
- Aider linting and testing: https://aider.chat/docs/usage/lint-test.html
- Existing repo research on Ralph loops: `docs/research/llm-ralph-loops.md`
