"""Summarize a vf-run traces.jsonl (pilot / difficulty filter): per-task pass counts,
truncation, failure modes, tokens and estimated cost. Data only; safe on Windows.
Usage: uv run python pipeline/pilot_summary.py <traces.jsonl> [--out data/reports/pilot/<name>.json]
"""
import argparse
import collections
import json
from pathlib import Path

PRICE_IN, PRICE_CACHED, PRICE_OUT = 0.04368, 0.0024, 0.70  # $/M tokens, deepseek-v4.1-flash-1017 (2026-11-20)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("traces")
    ap.add_argument("--out")
    args = ap.parse_args()
    rows = [json.loads(line) for line in Path(args.traces).read_text(encoding="utf-8").splitlines() if line.strip()]
    per_task = collections.defaultdict(list)
    modes = collections.Counter()
    out_tok, reason_tok, in_tok, cached_tok, truncated = [], [], 0, 0, 0
    for r in rows:
        t = r["traces"][0]
        tid = t["task"]["data"]["id"]
        reward = sum(v["score"] * v["weight"] for v in t["rewards"].values())
        per_task[tid].append(reward)
        call = t["calls"][-1]
        usage = call.get("usage") or {}
        is_trunc = call.get("finish_reason") == "length"
        truncated += is_trunc
        out_tok.append(usage.get("completion_tokens", 0))
        reason_tok.append(usage.get("reasoning_tokens") or (usage.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0)
        in_tok += usage.get("prompt_tokens", 0)
        cached_tok += usage.get("cached_input_tokens", 0)
        m, g = t["metrics"], t["info"].get("grade", {})
        if not r["ok"] or r["errors"]:
            mode = "infra_error"
        elif reward == 1.0:
            mode = "pass"
        elif m.get("no_code"):
            mode = "no_code_truncated" if is_trunc else "no_code"
        elif m.get("load_error"):
            mode = "load_error"
        elif m.get("call_timeouts"):
            mode = "call_timeout"
        else:
            mode = "wrong_answer"
        modes[mode] += 1
    hist = collections.Counter(int(sum(v)) for v in per_task.values())
    cost = (in_tok * PRICE_IN + cached_tok * PRICE_CACHED + sum(out_tok) * PRICE_OUT) / 1e6
    summary = {
        "rollouts": len(rows),
        "tasks": len(per_task),
        "mean_reward": round(sum(sum(v) for v in per_task.values()) / len(rows), 3),
        "pass_count_histogram": dict(sorted(hist.items())),
        "per_task": {k: f"{int(sum(v))}/{len(v)}" for k, v in sorted(per_task.items())},
        "failure_modes": dict(modes.most_common()),
        "truncated_rate": round(truncated / len(rows), 3),
        "mean_output_tokens": round(sum(out_tok) / len(rows)),
        "mean_reasoning_tokens": round(sum(reason_tok) / len(rows)),
        "token_cost_usd_estimate": round(cost, 4),
    }
    print(json.dumps(summary, indent=1))
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
