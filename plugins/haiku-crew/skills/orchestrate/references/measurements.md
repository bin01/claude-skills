# Measurements and how to re-check them

Claude Code 2.1.293, Haiku 5.5 executors, 7 October 2026.

## Executor starting context

First-call prompt size for an executor told to reply without using tools.

| Agent | Starting context | Tools it reported |
|---|---|---|
| reader | 4,526 | Read, Grep, Glob |
| editor | 4,716 | Read, Edit, Write, Grep |
| runner | 3,920 | Bash, Read |
| web-researcher | 3,183 | WebSearch, WebFetch |
| visual-reviewer | 2,869 | Read |

For comparison, built-in types on Haiku in a claude.ai session with many connectors: general-purpose 71,071; Explore 59,439. Built-in types grow with every connector you add. These executors allow no MCP tools, so they should not. All executors write to the 5-minute cache.

## Eval suite (evals/, run with `claude plugin eval`)

Seven cases on a pinned redis-py checkout plus generated fixtures. The planner is Opus 5.5 and there are 2 runs per case. Costs are per run, from the harness, at list price.

| Case | What it tests | v0.1 baseline | Final | Executors (final) |
|---|---|---|---|---|
| map-cluster-routing | one large subsystem (6k-line file) | $0.295 | $0.224 | $0.008 |
| compare-pools | two disjoint large files | $0.245 | $0.196 | $0.005 |
| qa-screenshots | visual QA, 6 planted defects | $0.219 | $0.184 | $0.001 |
| run-failing-tests | 2.7k-line noisy test output | $0.147 | $0.145 | done directly |
| bulk-config-edits | 30-file mechanical edit | $0.144 | $0.147 | done directly |
| tiny-lookup | one-grep question | $0.122 | $0.112 | done directly |
| architecture-overview | 4 subsystems, ~20k lines | (added later) | $0.350 | $0.011 |

All cases pass in the final version (14/14 runs). No executor call exceeded 100k tokens; the largest executor prompt was about 21k.

### What the hill climb changed

1. One job per scope: one `visual-reviewer` for all images, one `reader` per subsystem. QA went from 3 briefs to 1 (−21%).
2. Inline brief template, so the planner no longer opens the references file. Verification is limited to one combined call, and only for surprising or UNCONFIRMED claims. No separate recon turn: if the planner doesn't know the files, it gives `reader` the directory. Reading cases fell 12–15%.
3. The skill loads only for bigger jobs (3+ executors or a large codebase). The executors carry their own output format, budgets and stop rules, so 1–2 executor jobs need no skill-loading turn. Reading cases fell a further 10–14%.

The changes that were kept are the ones where quality held and cost fell on both runs.

### Comparison without the plugin (eval sandbox, 1 run each)

| Case | With plugin | Without plugin |
|---|---|---|
| map-cluster-routing | $0.224 (final) | $0.223, used built-in Explore |
| qa-screenshots | $0.184 (final) | $0.171, Opus viewed the images itself |

On small tasks in the eval sandbox, the plugin roughly matches running without it. The sandbox has no connectors, so the built-in `Explore` starts small there (peak 41k). In a real session with many connectors it starts at 59k or more, and it runs on the main model unless overridden. The plugin's gains are expected in those sessions, and on large tasks where helpers would otherwise cross Haiku's 100k price tier. The suite does not include a task that large. Use a real large task as the held-out check.

### Grader notes

- Two rubric bugs were fixed during the work. One judge criterion was less precise than a correct answer (TryAgain sleeps only once the TTL is below half). The other asked an architecture overview for low-level constants. Both runs were correct; the rubric was wrong.
- The architecture-overview answers ran 637–758 words against a 500-word limit. That is the planner's own writing, so it is not scored.

## Re-check in a new environment

```
claude -p "Spawn haiku-crew:reader with the prompt 'Do not call any tools. Reply only with a comma-separated list of the exact names of every tool you can call.' Print its reply." --model haiku
python3 <plugin>/skills/orchestrate/scripts/cost_report.py ~/.claude/projects/<project-dir>/<session-id>/subagents
```

Inside a chat session, spawning one executor with the same prompt and reading `subagent_tokens` in the result gives the same number. Expect 3–5k. A much larger number means the tool allowlist is not being applied.

To rerun the eval suite (it needs bubblewrap and socat for the Bash sandbox on Linux):

```
claude plugin eval <plugin-dir> --model opus --scaffold --allow-tools Bash Edit Write --keep-temp --json results.json
python3 <plugin-dir>/evals/eval_breakdown.py results.json
```

## List prices used by the cost script (USD per million tokens, platform.claude.com pricing, read 7 Oct 2026)

| Model | Input | Cache write 5m | Cache write 1h | Cache read | Output |
|---|---|---|---|---|---|
| Fable 5.1 / Mythos 5.1 | 10.00 | 12.50 | 20.00 | 0.25 | 50.00 |
| Opus 5.5 | 4.00 | 5.00 | 8.00 | 0.20 | 20.00 |
| Sonnet 5.5 | 2.00 | 2.50 | 4.00 | 0.10 | 10.00 |
| Haiku 5.5, prompt <= 100k | 0.10 | 0.125 | 0.20 | 0.01 | 0.50 |
| Haiku 5.5, prompt > 100k | 0.50 | 0.625 | 1.00 | 0.05 | 2.50 |

Transcript token counts match the CLI's `modelUsage` exactly. For Haiku the cost also matches the CLI's `total_cost_usd`. For Sonnet 5.5, Claude Code 2.1.293 bills cache reads at $0.20/M in its estimate, while the pricing page says $0.10/M, so the CLI figure overstates Sonnet sessions. This script follows the pricing page.
