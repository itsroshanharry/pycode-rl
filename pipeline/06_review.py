"""Stage 6 (model-assisted): independent review of every final task.

Why: the author (Claude Code) wrote the spec, reference, tests and checker, so the author's
own checks share its blind spots ("don't self-grade"). A different model reads each task and
answers: well-known/contaminated? ambiguous rule? tests checking something the spec does not
state? suspicious reference? Every flag is then reviewed by hand (data/reports/review/decisions.json).

Lessons from the first run (2026-11-20, DeepSeek: 44/76 calls used the whole 12k budget on
thinking and returned nothing, ~$0.37 lost): probe one call first, save every result as soon
as it finishes, and stop on an estimated-cost cap without losing what was already paid for.

  # Codespace (needs PRIME_API_KEY):
  .venv/bin/python pipeline/06_review.py run --model openai/gpt-oss-120b --probe 1      # one call
  .venv/bin/python pipeline/06_review.py run --model openai/gpt-oss-120b --cap 0.30     # the rest
  # anywhere:
  uv run python pipeline/06_review.py summarize
"""
import argparse
import json
import os
import re
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "data" / "dataset.jsonl"
OUT = ROOT / "data" / "reports" / "review"
API = "https://api.pinference.ai/api/v1/chat/completions"
PRICES = {  # $/M tokens (input, output), from `prime inference models` on 2026-11-20
    "deepseek/deepseek-v4.1-flash-1017": (0.04368, 0.70),
    "openai/gpt-oss-120b": (0.35, 0.75),
    "openai/gpt-oss-20b": (0.20, 0.30),
}

PROMPT = """You are auditing one task of a Python coding benchmark. Models see only the SPEC and
must write the function; they are graded by the hidden TESTS. The REFERENCE is the author's
solution. Be strict but fair: report only real problems, not style preferences.

SPEC (shown to models):
<<<
{spec}
>>>

HIDDEN TESTS:
<<<
{tests}
>>>

REFERENCE SOLUTION:
<<<
{reference}
>>>

Questions:
1. Is the task essentially a well-known contest/interview problem (LeetCode, Codeforces,
   AtCoder, Project Euler, a classic kata) whose solution a model could have memorized? A
   common real-world rule (a date format, a checksum, a protocol) is NOT that by itself.
2. AMBIGUITY: is there a rule a careful reader could reasonably implement in two different
   ways, where the tests accept only one of them? Quote the spec phrase.
3. UNSTATED CHECK: does any test assert behaviour that the spec does not state or clearly
   imply (input class, error type, ordering, rounding, edge case)? Name the test input.
4. REFERENCE: does the reference look wrong for any input the spec allows (beyond the tests)?
Reply with only a JSON object:
{{"well_known": null or "<problem and site>", "well_known_reason": "<one sentence>",
  "ambiguities": [{{"spec_phrase": "...", "why": "..."}}],
  "unstated_checks": [{{"test_input": "...", "why": "..."}}],
  "reference_concerns": [{{"input": "...", "why": "..."}}],
  "verdict": "ok" or "minor" or "major"}}
("major" = a correct reading of the spec can fail the tests; "minor" = wording could be clearer.)"""


def _out_file(model: str) -> Path:
    return OUT / f"review_{model.split('/')[-1]}.jsonl"


def _call(model: str, prompt: str, max_tokens: int) -> tuple[str, dict]:
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0,
                       "max_tokens": max_tokens, "reasoning_effort": "low"}).encode()
    req = urllib.request.Request(API, data=body, headers={"Authorization": f"Bearer {os.environ['PRIME_API_KEY']}",
                                                         "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        data = json.load(resp)
    choice = data["choices"][0]
    return (choice["message"].get("content") or ""), {**data.get("usage", {}), "finish": choice.get("finish_reason")}


def _parse(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    try:
        return json.loads(m.group()) if m else {"error": "no json"}
    except json.JSONDecodeError:
        return {"error": "bad json"}


def _done_ids() -> set[str]:
    """Tasks that already have a usable review from any model."""
    done = set()
    old = OUT / "deepseek_review.json"
    if old.exists():
        done |= {t["id"] for t in json.loads(old.read_text())["tasks"] if t.get("verdict")}
    for f in OUT.glob("review_*.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("verdict"):
                    done.add(r["id"])
    return done


def cmd_run(model: str, probe: int, cap: float, max_tokens: int, workers: int) -> None:
    rows = [json.loads(l) for l in DATASET.read_text(encoding="utf-8").splitlines() if l.strip()]
    todo = sorted((r for r in rows if r["id"] not in _done_ids()), key=lambda r: r["id"])
    if probe:
        todo = todo[:probe]
    p_in, p_out = PRICES[model]
    OUT.mkdir(parents=True, exist_ok=True)
    lock, spent, stop = threading.Lock(), [0.0], [False]
    print(f"{len(todo)} task(s) to review with {model}; cap ${cap}", flush=True)

    def work(row: dict) -> None:
        if stop[0]:
            return
        text, usage = _call(model, PROMPT.format(spec=row["prompt"], tests=row["tests"][:14000],
                                                  reference=row["reference"][:8000]), max_tokens)
        cost = ((usage.get("prompt_tokens") or 0) * p_in + (usage.get("completion_tokens") or 0) * p_out) / 1e6
        result = {"id": row["id"], "split": row["split"], "model": model, **_parse(text), "usage": usage,
                  "est_cost": round(cost, 5), "raw": text[-3000:]}
        with lock:
            with _out_file(model).open("a", encoding="utf-8") as f:  # saved immediately
                f.write(json.dumps(result) + "\n")
            spent[0] += cost
            if spent[0] >= cap:
                stop[0] = True
            print(f"{row['id']} {result.get('verdict', result.get('error'))} out={usage.get('completion_tokens')} "
                  f"finish={usage.get('finish')} spent~${spent[0]:.3f}", flush=True)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(work, todo))
    print(f"done; estimated spend ${spent[0]:.3f}{' (stopped at cap)' if stop[0] else ''}")


def _all_reviews() -> dict[str, dict]:
    reviews = {}
    old = OUT / "deepseek_review.json"
    if old.exists():
        for t in json.loads(old.read_text())["tasks"]:
            if t.get("verdict"):
                reviews[t["id"]] = {**t, "model": "deepseek/deepseek-v4.1-flash-1017"}
    for f in sorted(OUT.glob("review_*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip() and (r := json.loads(line)).get("verdict"):
                reviews.setdefault(r["id"], r)
    return reviews


def cmd_summarize() -> None:
    ids = {json.loads(l)["id"] for l in DATASET.read_text(encoding="utf-8").splitlines() if l.strip()}
    reviews = {k: v for k, v in _all_reviews().items() if k in ids}
    verdicts: dict[str, list] = {}
    for tid, r in sorted(reviews.items()):
        verdicts.setdefault(r["verdict"], []).append(tid)
    summary = {
        "dataset_tasks": len(ids), "reviewed": len(reviews), "missing": sorted(ids - set(reviews)),
        "by_model": {m: sum(r["model"] == m for r in reviews.values()) for m in sorted({r["model"] for r in reviews.values()})},
        "verdicts": {k: len(v) for k, v in verdicts.items()},
        "flagged": {k: v for k, v in verdicts.items() if k != "ok"},
        "well_known": {tid: r["well_known"] for tid, r in reviews.items() if r.get("well_known")},
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "summarize"])
    ap.add_argument("--model", default="openai/gpt-oss-120b")
    ap.add_argument("--probe", type=int, default=0, help="review only the first N pending tasks")
    ap.add_argument("--cap", type=float, default=0.30, help="stop starting new calls once estimated spend reaches this")
    ap.add_argument("--max-tokens", type=int, default=12000)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    if args.cmd == "run":
        cmd_run(args.model, args.probe, args.cap, args.max_tokens, args.workers)
    else:
        cmd_summarize()


if __name__ == "__main__":
    main()
