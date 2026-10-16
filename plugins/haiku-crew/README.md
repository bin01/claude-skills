# haiku-crew

Plan with a strong model, execute with cheap Haiku helpers, without the token bloat.

Built-in subagent types inherit every tool in the session, so a Haiku helper that does nothing can start at 37–71k tokens. These executors allow only the tools their job needs and start at 3–5k. That leaves room to do real work under Haiku's 100k long-context price tier.

## Install

In Claude Code:

```
/plugin marketplace add bin01/claude-skills
/plugin install haiku-crew@bin01-skills
```

Or from a shell: `claude plugin marketplace add bin01/claude-skills`, then `claude plugin install haiku-crew@bin01-skills`. The repository is private, so the machine needs git access to it (an SSH key or a credential helper for github.com).

To try a local checkout without installing, start Claude Code with `claude --plugin-dir <path-to-checkout>/plugins/haiku-crew`.

## What's inside

**Five executors** (`agents/`), all on Haiku with low effort, no MCP tools, no skills, a 5-minute cache and a turn budget:

- `reader`: answers numbered questions about local files, with file:line citations; one job per subsystem
- `web-researcher`: answers questions from web sources, with URLs
- `runner`: runs commands and returns a short summary, not raw output
- `visual-reviewer`: checks screenshots against a checklist and returns a defect list; one job for all of a task's images, up to 10
- `editor`: applies an exact change list and reports what it skipped

For a one- or two-executor job, the planner briefs them directly. Their descriptions say what a brief needs, and each executor enforces its own format, budget and stop rule.

**One skill**, `orchestrate`: how to run bigger jobs across executors (3+ executors or a large codebase). It covers job sizing against the 100k tier, disjoint scopes, the brief template, handling partial reports, one-call verification, and a transcript cost report (`scripts/cost_report.py`).

**An eval suite** (`evals/`, 7 cases on a pinned redis-py checkout plus generated fixtures) for `claude plugin eval`, plus `evals/eval_breakdown.py`, which joins scores with per-run planner and executor costs from the transcripts.

## Results

With an Opus planner, all 14 eval runs pass. Hill climbing cut planner cost on the cases that use executors by 16–24% against the first version. Executors cost about 1–3% of each run, and no executor call crossed 100k. Full numbers, including an honest comparison with running without the plugin, are in `skills/orchestrate/references/measurements.md`.

## Notes

- Agent descriptions are deliberately short, with no `<example>` blocks, because every description sits in the planner's context on every call.
- Plugin agents ignore `permissionMode`, `mcpServers` and `hooks`, so the executors take the permission mode of the main session. `runner` and `editor` will ask before running commands or editing unless that session auto-approves.
- After installing, check the starting context once in your own environment (see `measurements.md`). Expect 3–5k per executor.
