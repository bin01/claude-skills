#!/usr/bin/env python3
"""Per-agent token and cost report for a Claude Code session's transcripts.

Usage:
  python3 cost_report.py <session-dir-or-transcript.jsonl> [...] [--threshold 100000]
                        [--until "<opening words of a user message>" | --until <ISO timestamp>]

Point it at a session directory (the folder containing subagents/) or at
individual .jsonl transcripts. For each transcript it reports the agent type,
model, number of model calls, baseline (the first call's prompt size), peak
prompt, calls over the long-context threshold, cache-write TTL mix, and cost
at the list prices in PRICES below.

Each model call is counted once: transcripts can log several records per call
(one per content block), so records are de-duplicated by message id and the
last usage record for each id is kept. Calls logged without usage are counted
under 'no use' and not priced; when that count is non-zero the cost is a lower
bound. The model column is the model of most priced calls in the transcript.

--until drops every call from the first user message containing the text (or
from the timestamp) onward, in all transcripts, so turns after the task, such
as the request to measure it, stay out of the figures.

Prices are USD per million tokens, from platform.claude.com pricing as read
7 Oct 2026. Models without an entry show cost 'n/a' rather than a guess; add
a PRICES entry (checked against the pricing page) to price them.
"""
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# model prefix -> tiers. Each tier: (max_prompt or None, prices)
# prices: input, cache write 5m, cache write 1h, cache read, output
PRICES = {
    # longest matching model-id prefix wins; older versions are priced differently
    "claude-fable-5-1": [(None, (10.00, 12.50, 20.00, 0.25, 50.00))],
    "claude-mythos-5-1": [(None, (10.00, 12.50, 20.00, 0.25, 50.00))],
    "claude-opus-5-5": [(None, (4.00, 5.00, 8.00, 0.20, 20.00))],
    "claude-sonnet-5-5": [(None, (2.00, 2.50, 4.00, 0.10, 10.00))],
    "claude-haiku-5-5": [
        (100_000, (0.10, 0.125, 0.20, 0.01, 0.50)),
        (None, (0.50, 0.625, 1.00, 0.05, 2.50)),
    ],
}


def price_for(model, prompt):
    if not model:
        return None
    keys = [k for k in PRICES if model.startswith(k)]
    if not keys:
        return None
    for cap, p in PRICES[max(keys, key=len)]:
        if cap is None or prompt <= cap:
            return p
    return None


def parse_ts(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def records(path):
    for line in path.open():
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def user_text(r):
    content = (r.get("message") or {}).get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def find_cutoff(files, until):
    ts = parse_ts(until)
    if ts:
        return ts
    hits = [parse_ts(r.get("timestamp")) for f in files for r in records(f)
            if r.get("type") == "user" and until in user_text(r)]
    hits = [h for h in hits if h]
    if not hits:
        sys.exit(f"--until: no user message contains {until!r}")
    return min(hits)


def load_calls(path, cutoff=None):
    calls = {}
    for r in records(path):
        if r.get("type") != "assistant":
            continue
        if cutoff:
            ts = parse_ts(r.get("timestamp"))
            if ts and ts >= cutoff:
                continue
        m = r.get("message") or {}
        mid = m.get("id") or r.get("requestId") or r.get("uuid")
        if m.get("usage") or mid not in calls:
            calls[mid] = (m.get("model"), m.get("usage") or {})
    return list(calls.values())


def has_usage(u):
    return any((u.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens",
                                          "cache_read_input_tokens", "output_tokens"))


def agent_type(path):
    meta = path.with_name(path.name.replace(".jsonl", ".meta.json"))
    if meta.exists():
        try:
            return json.loads(meta.read_text()).get("agentType", "?")
        except json.JSONDecodeError:
            pass
    return "main" if "subagents" not in path.parts else "?"


def analyse(path, threshold, cutoff=None):
    calls = load_calls(path, cutoff)
    if not calls:
        return None
    used = [(m, u) for m, u in calls if has_usage(u)]
    model = Counter(m for m, _ in used).most_common(1)[0][0] if used else calls[0][0]
    out = dict(file=path.name, type=agent_type(path), model=model, calls=len(calls),
               nouse=len(calls) - len(used), baseline=0, peak=0, over=0, w5=0, w1=0,
               reads=0, output=0, cost=0.0, priced=True)
    for i, (model, u) in enumerate(used):
        inp = u.get("input_tokens", 0) or 0
        cw = u.get("cache_creation_input_tokens", 0) or 0
        cr = u.get("cache_read_input_tokens", 0) or 0
        o = u.get("output_tokens", 0) or 0
        cc = u.get("cache_creation") or {}
        w1 = cc.get("ephemeral_1h_input_tokens", 0) or 0
        w5 = cc.get("ephemeral_5m_input_tokens", cw - w1) or 0
        prompt = inp + cw + cr
        if i == 0:
            out["baseline"] = prompt
        out["peak"] = max(out["peak"], prompt)
        out["over"] += prompt > threshold
        out["w5"] += w5
        out["w1"] += w1
        out["reads"] += cr
        out["output"] += o
        p = price_for(model, prompt)
        if p is None:
            out["priced"] = False
            continue
        out["cost"] += (inp * p[0] + w5 * p[1] + w1 * p[2] + cr * p[3] + o * p[4]) / 1e6
    return out


def main():
    args = sys.argv[1:]
    threshold = 100_000
    if "--threshold" in args:
        i = args.index("--threshold")
        threshold = int(args[i + 1])
        del args[i:i + 2]
    until = None
    if "--until" in args:
        i = args.index("--until")
        until = args[i + 1]
        del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    files = []
    for a in args:
        p = Path(a).expanduser()
        if p.is_dir():
            files += sorted(p.rglob("*.jsonl"))
        else:
            files.append(p)
    cutoff = find_cutoff(files, until) if until else None
    if cutoff:
        print(f"Calls from {cutoff.isoformat()} onward are excluded.")
    rows = [r for f in files if (r := analyse(f, threshold, cutoff))]
    hdr = f"{'agent type':38} {'model':18} {'calls':>5} {'no use':>6} {'baseline':>9} {'peak':>8} {'>thr':>5} {'5m wr':>8} {'1h wr':>8} {'out':>7} {'cost $':>8}"
    print(hdr)
    print("-" * len(hdr))
    total = 0.0
    for r in rows:
        total += r["cost"]
        cost = f"{r['cost']:.4f}" if r["priced"] else "n/a"
        print(f"{r['type'][:38]:38} {str(r['model'])[:18]:18} {r['calls']:>5} {r['nouse']:>6} {r['baseline']:>9,} {r['peak']:>8,} "
              f"{r['over']:>5} {r['w5']:>8,} {r['w1']:>8,} {r['output']:>7,} {cost:>8}")
    print("-" * len(hdr))
    nouse = sum(r['nouse'] for r in rows)
    print(f"{'total':38} {'':18} {sum(r['calls'] for r in rows):>5} {nouse:>6} {'':>9} {'':>8} "
          f"{sum(r['over'] for r in rows):>5} {'':>8} {'':>8} {'':>7} {total:>8.4f}")
    print(f"\n'>thr' = calls whose prompt exceeded {threshold:,} tokens (Haiku's 5x price tier).")
    if nouse:
        print(f"'no use' = {nouse} call(s) logged without token usage; they are not priced, so the total is a lower bound.")


if __name__ == "__main__":
    main()
