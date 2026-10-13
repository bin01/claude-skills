---
name: raise-the-bar
description: Rewrite a task prompt to be more ambitious (altitude, depth, or range) before running it. Use on /raise-the-bar, "raise the bar on this", "make this more ambitious", or a request to upgrade a prompt.
---

# Raise the Bar: ambition rewrite

Turn the user's draft task into the version a field-leading professional would recognize as the real job. The default output is a rewritten prompt plus brief reasoning. Offer to run it here, where this conversation's files and tools are. Write it as a self-contained prompt for a fresh chat only if the user will run it elsewhere.

The goal is deeper, not bigger. More sections, slides or words is scope creep, not ambition.

## Who answers what
Claude answers what expertise can answer. The user answers what only they know.

- **Claude answers**: what a top professional would do, which methods and tools they'd use, which fields to bring in, what kinds of assumptions are worth testing, and what kind of outside check fits.
- **The user answers**:
  - what outcome they really want, who the audience is, their taste, and what a good result looks like to them
  - where their raw material lives and what checks already exist in their setup
  - what the user or their team currently believes about the problem
  - baselines for any target, and constraints Claude can't see (access, budget, deadline, off-limits options)

Before asking, check the conversation, attached files, and any connected tools. Never ask the user what a professional would do or which methods to use. Those are Claude's job.

## Step 0: Is it worth raising?
If the task is small, or the user's bar is already right, say so in one line. Offer the single lift that matters most (usually Altitude: what do you want to happen as a result?) and stop. Don't run the full process on a three-line email.

## Step 1: Pick the lens
State the task in one line, then pick one primary lens (a secondary is optional):

- **Altitude**: the work serves an outcome, such as a decision, a meeting, a recurring job, or a message meant to get someone to act. It is weaker for purely creative work.
- **Depth**: the user wants this specific thing done exceptionally well.
- **Range**: the work is creative, or the obvious single-field approach seems tapped out.

If the user named a lens, use it. If it's unclear, default to Depth and say so.

## Step 2: Interrogate the task
Work through the questions for the chosen lens and answer each one yourself in terse bullets. Questions marked (U) usually need the user. Answer those from context if you can; otherwise hold them for Step 3.

**Altitude**
1. (U) What should happen after this is done? What is the goal behind the goal?
2. (U) What decision or next step does this feed?
3. For the most urgent decisions, draft directions with arguments for and against.
4. Why does this artifact or process exist at all? Is there a better mechanism for that purpose, one that could be backtested against the user's own history and run alongside the current one for a cycle?
5. What standing responsibility could replace a stream of one-off tasks ("keep the app crash-free" instead of "fix this crash")? What environment changes would let the model own it, such as data feeds, access, or machines to verify on?

**Depth**
1. What would a top professional in this field do here that the user isn't asking for?
2. What is the rawest material they'd start from, instead of the pre-digested summary, report or template? (U) Where does that material live for this user, and can it be reached?
3. Which concrete methods and tools would they use? Name them (for example, a database plus a survival model, not "analyze the data"). Require the instruments, not the vocabulary.
4. What external check, other than the model or the user, would show the result is right? Prefer something runnable: tests, a benchmark, a holdout set, a profiler, a reproduction, an independent source. (U) Which of these already exists in the user's setup?
5. (U) What does the user or team currently believe about this? Plan to test that belief adversarially against the raw data.
6. What new knowledge could come out once deep in the material, such as a blind spot, an earlier signal, or a model that predicts on data it hasn't seen?

**Range**
1. Replace nouns with verbs. Restate what the deliverable *does*: "a deck" becomes "get busy people to believe a cause-and-effect story and decide under uncertainty in 30 minutes".
2. Assemble the crew: which fields would you staff if this had to be extraordinary? Include an adversary (red team) when the work makes claims that could be wrong. Include an unexpected field only when it brings a real technique, not for novelty.
3. For each field, name the technique it contributes: what that practitioner *does* (how a short seller researches a position), not a voice to imitate.
4. Where subagents are available, give each field its own agent.

## Step 3: Ask only what's left
If open (U) questions would materially change the result, ask the user.

- Ask at most three questions, in one round. If more are open, ask the three whose answers would change the prompt most, and mark the rest as `[assumption: ...]`.
- Use the multiple-choice question tool when it's available, with your best guesses as options (the user can always type their own). Otherwise ask in plain text.
- Show your Step 2 answers alongside the questions so the user can correct those too.
- If nothing material is missing, skip this step.
- If the user is away or doesn't answer, proceed with your best guesses marked as assumptions.

## Step 4: Set the bar
- Where the task has a measurable bar, replace "do your best" with a specific hard target well beyond the current one (5s to 200ms, not 5s to 4s), and state it as achievable. Base it on the user's baseline when you have one.
- Tell the executing model that if the target seems impossible, it should keep going and report what's blocking, rather than lowering the bar. It must report honestly where it landed.
- Cite a precedent only if you can name a real one.
- For creative or qualitative work, skip numeric targets. Set the bar through the audience and the standard of the best work in that form.

## Step 5: Write the rewritten prompt
Always include:
- The goal and why it matters
- The outputs of the chosen lens (below)
- The deliverable and what "done" means
- The outside check

Lens outputs:
- **Altitude**: the outcome; the decisions to draft, with arguments for and against; the better mechanism and how to backtest it and run it alongside the current one; any standing responsibility and the environment it needs.
- **Depth**: the raw inputs and where they live; the required instruments, with the shallow substitute banned explicitly when the task involves data ("not markdown tables"); the assumptions to falsify; the stretch target.
- **Range**: the verb restatement; each field and the technique it contributes; how to split the work across agents.

Outside check: make it runnable where possible. If none exists, name the human one (the child's reaction, the exec's decision) or say plainly that there isn't one. The model must not grade its own work.

Mark remaining guesses inline as `[assumption: ...]`. Keep the prompt tight and cut anything that is only vocabulary.

## Step 6: Flag prerequisites
Separately, list access the rewritten prompt assumes the user may not have set up: data exports, connectors, a sandbox that can install software, test environments, devices. Ambitious prompts fail more often on missing access than on missing intelligence.

## Output format
If there are questions:
- First reply: the lens and why (one line), your Step 2 answers as terse bullets, and the questions.
- After the user answers: the rewritten prompt in a fenced block, the prerequisites, and an offer to run it here.

If there are no questions, send one reply with all of it.

## Guardrails
- **Role-play trap**: never write "act as a short seller" or "write like an expert". Ask for the method that person uses.
- **Vocabulary trap**: expert words without expert tools are not depth.
- **Self-judging trap**: the model grading its own output does not count as validation.
- **No invention**: never invent data sources, judges, precedents, baselines or systems the user has. Ask, or mark it as an assumption.
