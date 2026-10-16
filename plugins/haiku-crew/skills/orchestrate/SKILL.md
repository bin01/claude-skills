---
name: orchestrate
description: "Orchestrates the haiku-crew agents (reader, web-researcher, runner, visual-reviewer, editor) on larger jobs: three or more executors, a large codebase or document set, fan-out research, or multi-step build-and-review work. Use when the user asks to plan-and-execute, use many cheap or Haiku helpers, or cut token cost on a big task. Not needed for a one- or two-executor job."
---

# Orchestrate Haiku executors

Orchestrating executors pays when the material they must read is large relative to the reports they send back. The planner (you) keeps judgment and the final deliverable; executors gather and check facts. Cost is driven by three things: each executor's starting context, how far its context grows, and how much of that the planner ends up re-reading.

## Executors

Use only these executors. Each runs on Haiku with a strict tool allowlist, no MCP tools, no skills, and a turn budget. Measured starting context is about 3-5k tokens, against 59k for built-in Explore and 37-71k for general-purpose.

| Agent | Tools | Use for | Turn budget (hard stop) |
|---|---|---|---|
| `haiku-crew:reader` | Read, Grep, Glob | Code, docs, data files already on disk | 8 tool turns (10) |
| `haiku-crew:web-researcher` | WebSearch, WebFetch | External facts with source URLs | 6 (8) |
| `haiku-crew:runner` | Bash, Read | Tests, builds, scripts, queries; returns a summary | 6 (8) |
| `haiku-crew:visual-reviewer` | Read | Screenshots and renders against a checklist | 2 (4) |
| `haiku-crew:editor` | Read, Edit, Write, Grep | Exact change lists on named files | 10 (12) |

Do not use `general-purpose`, `claude`, `Explore` or forks as cheap executors: they inherit every tool in the session, and a fork also carries your full context on your model. Pass `model: sonnet` on the Agent call when a job needs more reasoning than Haiku gives; the executor keeps its small tool set.

## 1. Decide whether to use executors

Use executors when the job reads more than about 15k tokens of material (roughly 1,000 lines of code) to produce a short answer, or when several such jobs can run in parallel.

Do the work yourself when:
- the answer is one or two greps away,
- each finding decides the next question (tightly coupled reasoning),
- you could not cheaply verify the executor's key claims,
- the work is the final deliverable: design, writing, the decision.

## 2. Scope the work before dispatching

Do not spend a turn on recon just to build file lists; every turn re-reads your context at your price. List files only when you have seen them in this session's output and know they hold the answers. Otherwise give the executor the directory, a file budget and the questions: Haiku searching the tree costs a fraction of a cent, while a guessed file list leaves answers in files the executor is told not to open. Split the work so that:

- **Each path is real.** Copy every path from output you have seen this session (the clone, `pwd` or a listing), never from where you expect it to be. An executor given a missing path stops and reports, and the job has to be dispatched again.
- **Each job is bounded.** Name files and line ranges when you know them; otherwise name the directory, the file budget, and what to skip.
- **Each job fits.** Keep the material a reader job reads to about 4,000 lines of code (budget about 15 tokens per line, measured). That puts the peak prompt near 65k, well below Haiku's 100k long-context tier, where every token in the call costs 5x. Split larger scopes into two jobs.
- **One job per disjoint scope, not per file or image.** Shared infrastructure goes to one executor; the others cite it by name instead of re-reading it. Every brief you write is output at your price, so one `visual-reviewer` takes all of a task's screenshots and one `reader` takes a whole subsystem. Split only when a scope would pass the 100k ceiling, or when a review has more than 10 images (split those by page region).

## 3. Write the brief

The executor sees only the brief, not your conversation, so state everything it needs. Ask closed, numbered questions the deliverable depends on, rather than "explain X". Use this shape (no need to open the references folder):

```
Scope: ONLY <exact files with line ranges, or a directory to search | image paths | sources | working dir>
Budget: <N files | N fetches | N commands>. Do not touch: <exclusions; who covers them>
1. <closed question, or exact change, or command and what to report>
2. ...
Return: numbered answers with citations (file:line, URL or image name), max <N> words, UNCONFIRMED where not verified, then a Gaps: line.
```

Write every file and image path out in full. Executors cannot fill in a range such as `shot-01 … shot-12`, and silently skip what they cannot resolve. For a review, also say what is intended and not a defect (deliberate horizontal scrolling, empty states, dimmed inactive elements), or the report fills up with it.

## 4. Dispatch

Launch independent jobs in parallel, in a single message with several Agent calls. Run executors in the foreground unless you have other work to do meanwhile.

## 5. Handle reports

- Reports come back as numbered answers with citations, a `Gaps:` line, and `UNCONFIRMED` markers. Read each once and pull out what you need; do not re-read reports in later turns.
- **Gaps:** dispatch a new, narrower job for the gap, naming the files that hold the answer. This is cheaper than resuming the old executor, whose context is already full.
- **Cut off with no report** (the result says it hit its turn limit): send it one `SendMessage` saying "Stop calling tools and report now in the required format." Then fix the scoping that caused it.

## 6. Verify proportionately

Reports carry citations, so most claims need no re-check. Verify once, after all reports are in and before you build the deliverable:

1. List the claims the deliverable depends on that are surprising, conflict between reports, or are marked UNCONFIRMED. Add any number, threshold or condition whose quoted source line does not say what the answer says: an executor can cite the right line and still misstate the rule, for example reporting one branch's limit as the general one.
2. Check the whole list in ONE call: a single Bash command combining several `grep -n` patterns and `sed -n` ranges.

If nothing qualifies, skip verification. If building the deliverable turns up facts you still need, collect them and check them together in one more call, not one call per fact. Each extra call re-reads your whole context at your price.

## 7. Keep your own context small

- Every call you make re-reads your full context, and your tokens cost 20-40x an executor's. Anything bulky you would read only to extract a few facts belongs to an executor.
- A large deliverable you write yourself stays in your context, and every later call re-reads it. Before writing it, plan the steps that follow and combine them: one command that syntax-checks, renders and saves every screenshot, then one edit pass per round of fixes. Do not Read the deliverable back.
- Do not put screenshots in your own context to review renders. Save them to files and send them to `visual-reviewer` with a checklist; fix from its defect list. Hide sticky and fixed elements before taking element screenshots, or they land on top of content and get reported as defects.
- Run one review round. Take a second only if the first reported high-severity defects, and send only the images those fixes changed.
- Do not ask executors for long reports. Raise word caps only when the deliverable needs the detail.

## 8. Measure

After the task, run the cost report on the session's transcripts:

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/orchestrate/scripts/cost_report.py ~/.claude/projects/<project>/<session-id>.jsonl ~/.claude/projects/<project>/<session-id>/
```

Pass both paths: the `.jsonl` file is your own transcript and the folder holds the executors'. It lists, per agent, the calls made, the starting and peak prompt, the calls over 100k, the cache-write TTL and the cost at list price. To leave out turns after the task, such as the request to measure it, add `--until "<opening words of that message>"` (or an ISO timestamp); calls from that point on are dropped from every transcript. Calls logged without usage are counted in the `no use` column and are not priced, so a non-zero count means the total is a lower bound. Report executor calls over 100k as a scoping problem to fix next time. To check the executors' starting context in a new environment, see `references/measurements.md`.
