"""Stage 6 (model-assisted): one independent review pass over every final task.

Why: the author (Claude Code) wrote the spec, reference, tests and checker, so the author's
own checks share its blind spots ("don't self-grade"). A different, stronger model reads each
task and answers four questions: well-known/contaminated? ambiguous rule? tests checking
something the spec does not state? suspicious reference? Every flag is then reviewed by hand
(recorded in data/reports/review/decisions.json), and the user spot-checks a sample.

  # Codespace (needs PRIME_API_KEY; about $0.2-0.35 with DeepSeek V4.1 Flash):
  .venv/bin/python pipeline/06_review.py run
  # anywhere:
  uv run python pipeline/06_review.py summarize
"""
import argparse
import json
import os
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "data" / "dataset.jsonl"
OUT = ROOT / "data" / "reports" / "review"
MODEL = "deepseek/deepseek-v4.1-flash-1017"
API = "https://api.pinference.ai/api/v1/chat/completions"

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


def _call(prompt: str) -> tuple[str, dict]:
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0,
                       "max_tokens": 12000, "reasoning_effort": "low"}).encode()
    req = urllib.request.Request(API, data=body, headers={"Authorization": f"Bearer {os.environ['PRIME_API_KEY']}",
                                                         "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        data = json.load(resp)
    choice = data["choices"][0]
    return (choice["message"].get("content") or ""), {**data.get("usage", {}), "finish": choice.get("finish_reason")}


def _review(row: dict) -> dict:
    text, usage = _call(PROMPT.format(spec=row["prompt"], tests=row["tests"][:14000], reference=row["reference"][:8000]))
    m = re.search(r"\{.*\}", text, re.S)
    try:
        verdict = json.loads(m.group()) if m else {"error": "no json"}
    except json.JSONDecodeError:
        verdict = {"error": "bad json"}
    return {"id": row["id"], "split": row["split"], **verdict, "usage": usage, "raw": text[-3000:]}


def cmd_run() -> None:
    rows = [json.loads(l) for l in DATASET.read_text(encoding="utf-8").splitlines() if l.strip()]
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(_review, rows))
    results.sort(key=lambda r: r["id"])
    usage = {k: sum((r["usage"].get(k) or 0) for r in results) for k in ("prompt_tokens", "completion_tokens")}
    (OUT / "deepseek_review.json").write_text(json.dumps({"model": MODEL, "usage": usage, "tasks": results}, indent=1) + "\n")
    for r in results:
        print(r["id"], r.get("verdict"), "| well_known:", r.get("well_known"), "| amb", len(r.get("ambiguities") or []),
              "| unstated", len(r.get("unstated_checks") or []), "| ref", len(r.get("reference_concerns") or []), r.get("error", ""))
    print("usage", usage)


def cmd_summarize() -> None:
    rev = json.loads((OUT / "deepseek_review.json").read_text())["tasks"]
    judge1 = {t["id"]: t for t in json.loads((ROOT / "data" / "reports" / "contamination" / "judge.json").read_text())["tasks"]}
    agree = both = only1 = only2 = 0
    for r in rev:
        a, b = bool(judge1.get(r["id"], {}).get("well_known")), bool(r.get("well_known"))
        agree += a == b
        both += a and b
        only1 += a and not b
        only2 += b and not a
    verdicts = {}
    for r in rev:
        verdicts.setdefault(r.get("verdict", "error"), []).append(r["id"])
    summary = {"tasks": len(rev), "verdicts": {k: len(v) for k, v in verdicts.items()},
               "well_known_agreement_with_gpt_oss_20b": {"agree": agree, "both_flag": both, "only_gpt_oss": only1, "only_deepseek": only2},
               "flagged": {k: v for k, v in verdicts.items() if k != "ok"},
               "deepseek_well_known": {r["id"]: r["well_known"] for r in rev if r.get("well_known")}}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "summarize"])
    args = ap.parse_args()
    cmd_run() if args.cmd == "run" else cmd_summarize()


if __name__ == "__main__":
    main()
