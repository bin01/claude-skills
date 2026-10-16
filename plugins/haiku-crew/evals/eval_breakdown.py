#!/usr/bin/env python3
"""Join `claude plugin eval --json` results with per-run transcript costs.

Usage: python3 eval_breakdown.py <aggregate.json> [--csv out.csv]

Needs the run directories kept with --keep-temp. For each run it reports the
score, planner and executor cost (from transcripts, at the list prices in
cost_report.py), the executor types spawned, whether the skill fired,
the largest executor prompt, and executor calls over 100k tokens.
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "skills" / "orchestrate" / "scripts"))
from cost_report import analyse  # noqa: E402

SKILL = "orchestrate"


def run_root(trace_path):
    p = Path(trace_path)
    for parent in p.parents:
        if parent.name.startswith("claude-eval-"):
            return parent
    return None


def main_transcript_facts(path):
    spawned, skill = [], False
    for line in path.open():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("type") != "assistant":
            continue
        for c in (r.get("message") or {}).get("content") or []:
            if c.get("type") != "tool_use":
                continue
            if c.get("name") == "Skill" and SKILL in json.dumps(c.get("input")):
                skill = True
            if c.get("name") in ("Agent", "Task"):
                spawned.append((c.get("input") or {}).get("subagent_type", "general-purpose"))
    return spawned, skill


def analyse_run(trace_path):
    root = run_root(trace_path)
    if root is None or not root.exists():
        return None
    files = sorted((root / "config" / "projects").rglob("*.jsonl"))
    out = dict(planner=0.0, executors=0.0, spawned=[], skill=False, exec_peak=0, over=0, planner_calls=0, priced=True)
    for f in files:
        a = analyse(f, 100_000)
        if a is None:
            continue
        out["priced"] &= a["priced"]
        if "subagents" in f.parts:
            out["executors"] += a["cost"]
            out["exec_peak"] = max(out["exec_peak"], a["peak"])
            out["over"] += a["over"]
        else:
            out["planner"] += a["cost"]
            out["planner_calls"] += a["calls"]
            sp, sk = main_transcript_facts(f)
            out["spawned"] += sp
            out["skill"] |= sk
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = json.load(open(sys.argv[1]))
    rows = []
    for case in d["cases"]:
        for arm, runs in (case.get("arms") or {}).items():
            for i, r in enumerate(runs):
                a = analyse_run(r.get("tracePath") or "") or {}
                spawned = collections.Counter(s.split(":")[-1] for s in a.get("spawned", []))
                rows.append(dict(
                    case=case["name"], arm=arm, run=i + 1, score=r.get("score"),
                    harness_cost=r.get("costUsd") or 0.0,
                    planner=a.get("planner", float("nan")), executors=a.get("executors", float("nan")),
                    calls=a.get("planner_calls"), skill=a.get("skill"),
                    spawned=",".join(f"{k}x{v}" for k, v in sorted(spawned.items())) or "-",
                    exec_peak=a.get("exec_peak"), over=a.get("over"), error=(r.get("error") or "")[:60]))
    hdr = f"{'case':20} {'arm':7} {'run':>3} {'score':>5} {'harness$':>8} {'planner$':>8} {'exec$':>7} {'calls':>5} {'skill':>5} {'exec peak':>9} {'>100k':>5}  spawned"
    print(hdr)
    print("-" * len(hdr))
    for x in rows:
        print(f"{x['case'][:20]:20} {x['arm']:7} {x['run']:>3} {x['score'] if x['score'] is not None else '-':>5} "
              f"{x['harness_cost']:>8.3f} {x['planner']:>8.3f} {x['executors']:>7.4f} {str(x['calls']):>5} "
              f"{str(x['skill'])[:5]:>5} {x['exec_peak'] or 0:>9,} {x['over'] or 0:>5}  {x['spawned']} {x['error']}")
    by = collections.defaultdict(list)
    for x in rows:
        by[(x["case"], x["arm"])].append(x)
    print("\nper case (mean of runs):")
    for (c, arm), xs in by.items():
        n = len(xs)
        print(f"  {c:20} {arm:7} score {sum((x['score'] or 0) for x in xs) / n:.2f}  "
              f"cost ${sum(x['harness_cost'] for x in xs) / n:.3f}  executors ${sum(x['executors'] for x in xs) / n:.4f}")
    print(f"\nrun total (harness estimate, incl. judges): ${d.get('costUsd', 0):.2f}")
    if "--csv" in sys.argv:
        import csv
        p = sys.argv[sys.argv.index("--csv") + 1]
        with open(p, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main()
