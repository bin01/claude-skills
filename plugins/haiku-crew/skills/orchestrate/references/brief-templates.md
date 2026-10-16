# Brief templates

Per-executor versions of the brief shape in SKILL.md. Fill every field and pass it as the Agent prompt; the executor sees nothing but the brief.

## reader

```
Scope: ONLY these files (paths copied from output you have seen; relative to <repo root> or absolute):
<path/a.ts>, <path/b.ts (lines 120-340)>, <path/c.py>
File budget: <N, normally the number of files listed>.
Do not read: <tests, fixtures, other-scope dirs> (<who covers them>; cite by name).
Answer, with file:line for each fact:
1. <closed question the deliverable depends on>
2. <...>
Return: numbered answers, max <400> words, mark anything unverified as UNCONFIRMED, then a Gaps: line.
```

## web-researcher

```
Sources: start with <official URL(s)>; prefer primary sources.
Fetch budget: <N>.
1. <question with the exact quantity, version or date you need>
2. <...>
Return: numbered answers with source URLs, max <300> words, UNCONFIRMED where no source states it.
```

## runner

```
Working directory: <absolute path>.
Run:
1. `<command>` (<what to report: pass/fail, counts, first error>)
2. `<command>`
Do not: install, change config, push, delete, or attempt fixes.
Return: the standard report, max <200> words.
```

## visual-reviewer

```
Images: <absolute path 1>, <absolute path 2> (every path in full, at most 10)
Context: <what the page or screen is and who it is for, one line>.
Intended, not defects: <deliberate scrolling, empty states, dimmed elements, or "none">.
Checklist:
1. <specific, checkable item: "Every chart has a labelled y-axis">
2. <...>
Return: the standard report, max <200> words.
```

## editor

```
Files: <absolute path(s)>
Apply exactly:
1. In <file>, change <exact current text or key> to <new text>.
2. <...>
Change nothing else. Skip and report any instruction whose target is not found.
Return: the standard report, max <150> words.
```

## Worked example (reader, from the eval suite)

```
Scope: ONLY redis-py/redis/cluster.py (RedisCluster: lines 400-1000 and 1790-2270) and redis-py/redis/crc.py
Budget: 2 files. Do not read: redis/asyncio/* (not in scope), tests.
1. How is a key's slot computed, including hash tags?
2. What bounds the per-command retry loop?
3. What happens on MOVED, ASK, TryAgain and ConnectionError/TimeoutError, and when is the slot map refreshed?
4. What governs the outer retries, and what is the default?
Return: numbered answers with file:line, max 350 words, UNCONFIRMED where not verified, then a Gaps: line.
```

Result in evals: peak executor prompt about 20k, no calls over 100k, under $0.01 per job.
