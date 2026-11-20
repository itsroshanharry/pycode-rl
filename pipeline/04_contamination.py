"""Stage 4: contamination check against public coding benchmarks.

Why: our tasks are LLM-written, and an LLM can reproduce a benchmark problem from memory.
A task that is a reworded HumanEval/MBPP/LiveCodeBench problem (or a well-known LeetCode
problem) measures memorization, not ability.

Steps (run in the Codespace: LiveCodeBench is about 4.5 GB, streamed and reduced to its
problem text; HumanEval/MBPP come from their authors' original JSONL releases on GitHub,
pinned by commit, so no extra packages are needed):
  fetch    -> data/external/corpus.jsonl (pinned revisions; git-ignored, not redistributed)
  lexical  -> data/reports/contamination/lexical.json
              normalized-token 5-gram Jaccard (prompt vs problem text, reference vs solution
              code) for ALL pairs, plus the longest common token run for pairs that share a
              13-gram (the GPT-3 decontamination unit).
  judge    -> data/reports/contamination/judge.json
              (a) LMSYS-style rephrase check: the task next to its 3 most similar benchmark
                  problems; "is it the same problem reworded?"
              (b) "is it a well-known LeetCode/Codeforces-style problem? which one?"
              Model: openai/gpt-oss-20b via Prime Inference, temperature 0.
  decide   -> data/decontaminated.jsonl + data/reports/contamination/decisions.json
Thresholds: drop if 5-gram Jaccard >= 0.5, a common run >= 30 tokens, or a judge "yes"
that survives manual review (--overrule lists judge flags rejected after reading them).
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "external" / "corpus.jsonl"
REPORTS = ROOT / "data" / "reports" / "contamination"
TASKS = ROOT / "data" / "filtered.jsonl"
HF = "https://huggingface.co/datasets/{repo}/resolve/{rev}/{path}"
GH = "https://raw.githubusercontent.com/{repo}/{rev}/{path}"
# HumanEval and MBPP: the authors' original releases (same data as openai/openai_humaneval and
# google-research-datasets/mbpp on Hugging Face), pinned by git commit.
SOURCES = {
    "humaneval": (GH, "openai/human-eval", "b9453e8f1865df0a0057a1383767caa400acfbcf", ["data/HumanEval.jsonl.gz"]),
    "mbpp": (GH, "google-research/google-research", "f82046ba5aabbbb427dbfd38a254d26bff08b533", ["mbpp/mbpp.jsonl"]),
    "livecodebench": (HF, "livecodebench/code_generation_lite", "0fe84c3912ea0c4d4a78037083943e8f0c4dd505",
                      ["test.jsonl"] + [f"test{i}.jsonl" for i in range(2, 7)]),
}
JUDGE_MODEL = "openai/gpt-oss-20b"
API = "https://api.pinference.ai/api/v1/chat/completions"


# ----------------------------------------------------------------------------- fetch
def _open(url: str):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "pycode-decontam"}), timeout=600)


def cmd_fetch() -> None:
    import gzip

    CORPUS.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with CORPUS.open("w", encoding="utf-8") as out:
        for source, (base, repo, rev, paths) in SOURCES.items():
            for path in paths:
                url = base.format(repo=repo, rev=rev, path=path)
                if source in ("humaneval", "mbpp"):  # small JSONL (HumanEval gzipped)
                    data = _open(url).read()
                    if path.endswith(".gz"):
                        data = gzip.decompress(data)
                    for line in data.decode("utf-8").splitlines():
                        if not line.strip():
                            continue
                        row = json.loads(line)
                        if source == "humaneval":
                            rec = {"id": row["task_id"], "text": row["prompt"], "code": row["canonical_solution"]}
                        else:
                            rec = {"id": f"mbpp/{row['task_id']}", "text": row["text"], "code": row["code"]}
                        out.write(json.dumps({"source": source, **rec}) + "\n")
                        n += 1
                else:  # LiveCodeBench: stream line by line, keep only the problem statement
                    with _open(url) as resp:
                        for raw in resp:
                            row = json.loads(raw)
                            rec = {"id": f"{row.get('platform')}/{row.get('question_id')}",
                                   "text": f"{row.get('question_title', '')}\n{row.get('question_content', '')}", "code": ""}
                            out.write(json.dumps({"source": source, **rec}) + "\n")
                            n += 1
                print(f"{source}: {path} done ({n} records so far)", flush=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "sources.json").write_text(json.dumps({k: {"url": v[0], "repo": v[1], "revision": v[2], "files": v[3]} for k, v in SOURCES.items()}, indent=1) + "\n")
    print(f"{n} benchmark records -> {CORPUS.relative_to(ROOT)}")


# ----------------------------------------------------------------------------- lexical
_TOK = re.compile(r"[a-z0-9]+")


def tokens(s: str) -> list[str]:
    return _TOK.findall(s.lower())


def grams(toks: list[str], n: int) -> set[tuple]:
    return {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def longest_run(a: list[str], b: list[str]) -> int:
    best, prev = 0, [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            if x == y:
                cur[j] = prev[j - 1] + 1
                best = max(best, cur[j])
        prev = cur
    return best


def _task_text(row: dict) -> str:
    return row["prompt"]


def cmd_lexical() -> None:
    corpus = [json.loads(l) for l in CORPUS.read_text(encoding="utf-8").splitlines() if l.strip()]
    tasks = [json.loads(l) for l in TASKS.read_text(encoding="utf-8").splitlines() if l.strip()]
    ctext = [tokens(c["text"]) for c in corpus]
    ccode = [tokens(c["code"]) for c in corpus]
    c5t, c5c = [grams(t, 5) for t in ctext], [grams(t, 5) for t in ccode]
    c3t = [grams(t, 3) for t in ctext]
    index13: dict[tuple, set[int]] = {}
    for i, (t, c) in enumerate(zip(ctext, ccode)):
        for g in grams(t, 13) | grams(c, 13):
            index13.setdefault(g, set()).add(i)
    results = []
    for row in tasks:
        tt, tc = tokens(_task_text(row)), tokens(row["reference"])
        g5t, g5c, g3t = grams(tt, 5), grams(tc, 5), grams(tt, 3)
        jt = [jaccard(g5t, s) for s in c5t]
        jc = [jaccard(g5c, s) if s else 0.0 for s in c5c]
        rank = sorted(range(len(corpus)), key=lambda i: (jaccard(g3t, c3t[i]), jt[i]), reverse=True)[:3]
        shared = set()
        for g in grams(tt, 13) | grams(tc, 13):
            shared |= index13.get(g, set())
        runs = {i: max(longest_run(tt, ctext[i]), longest_run(tc, ccode[i])) for i in shared}
        best_run = max(runs.items(), key=lambda kv: kv[1], default=(None, 0))
        results.append({
            "id": row["id"],
            "max_jaccard_prompt": round(max(jt), 4), "max_jaccard_prompt_with": corpus[max(range(len(jt)), key=jt.__getitem__)]["id"],
            "max_jaccard_code": round(max(jc), 4), "max_jaccard_code_with": corpus[max(range(len(jc)), key=jc.__getitem__)]["id"],
            "longest_common_run": best_run[1], "longest_run_with": corpus[best_run[0]]["id"] if best_run[0] is not None else None,
            "top3_for_judge": [{"id": corpus[i]["id"], "source": corpus[i]["source"], "j3": round(jaccard(g3t, c3t[i]), 4)} for i in rank],
        })
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "lexical.json").write_text(json.dumps({"corpus_size": len(corpus), "tasks": results}, indent=1) + "\n")
    print(f"{len(tasks)} tasks x {len(corpus)} benchmark problems")
    for key in ("max_jaccard_prompt", "max_jaccard_code", "longest_common_run"):
        top = sorted(results, key=lambda r: r[key], reverse=True)[:3]
        print(key, [(r["id"], r[key]) for r in top])


# ----------------------------------------------------------------------------- judge
JUDGE_PROMPT = """You check a coding benchmark for contamination.

TASK (written for our benchmark):
<<<
{task}
>>>

The {k} most similar problems from public benchmarks (HumanEval, MBPP, LiveCodeBench):
{cands}

Answer two questions.
1. Is the TASK the same problem as any candidate, possibly reworded or with renamed
   identifiers (the same required input -> output behaviour)? Sharing a topic or a technique
   is NOT enough.
2. Independently of the candidates: is the TASK essentially a well-known programming-contest
   or interview problem (LeetCode, Codeforces, AtCoder, Project Euler, a classic kata) whose
   solution a model could have memorized? Name it if so. A common real-world rule (a date
   format, a checksum, a protocol) is NOT a well-known contest problem by itself.
Reply with only a JSON object:
{{"same_as": null or "<candidate id>", "same_reason": "<one sentence>",
  "well_known": null or "<problem name and site>", "well_known_reason": "<one sentence>"}}"""


def _call(prompt: str) -> str:
    key = os.environ["PRIME_API_KEY"]  # never printed
    body = json.dumps({"model": JUDGE_MODEL, "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0, "max_tokens": 2048, "reasoning_effort": "low"}).encode()
    req = urllib.request.Request(API, data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"] or "", data.get("usage", {})


def cmd_judge() -> None:
    corpus = {(c := json.loads(l))["id"]: c for l in CORPUS.read_text(encoding="utf-8").splitlines() if l.strip()}
    lex = {r["id"]: r for r in json.loads((REPORTS / "lexical.json").read_text())["tasks"]}
    tasks = [json.loads(l) for l in TASKS.read_text(encoding="utf-8").splitlines() if l.strip()]
    out, usage = [], {"prompt_tokens": 0, "completion_tokens": 0}
    for row in tasks:
        cands = "\n".join(f"[{c['id']}]\n<<<\n{corpus[c['id']]['text'][:1800]}\n>>>" for c in lex[row["id"]]["top3_for_judge"])
        text, u = _call(JUDGE_PROMPT.format(task=_task_text(row)[:4000], k=3, cands=cands))
        for k in usage:
            usage[k] += u.get(k, 0) or 0
        m = re.search(r"\{.*\}", text, re.S)
        try:
            verdict = json.loads(m.group()) if m else {"error": "no json"}
        except json.JSONDecodeError:
            verdict = {"error": "bad json"}
        out.append({"id": row["id"], **verdict, "raw": text[-1500:]})
        print(row["id"], verdict.get("same_as"), "|", verdict.get("well_known"), flush=True)
    (REPORTS / "judge.json").write_text(json.dumps({"model": JUDGE_MODEL, "usage": usage, "tasks": out}, indent=1) + "\n")
    print("usage", usage)


# ----------------------------------------------------------------------------- decide
def cmd_decide(overrule: list[str], extra_drop: list[str]) -> None:
    extra = dict(item.split('=', 1) for item in extra_drop)  # id=reason (author review with web verification)
    lex = {r["id"]: r for r in json.loads((REPORTS / "lexical.json").read_text())["tasks"]}
    judge = {r["id"]: r for r in json.loads((REPORTS / "judge.json").read_text())["tasks"]}
    tasks = [json.loads(l) for l in TASKS.read_text(encoding="utf-8").splitlines() if l.strip()]
    kept, decisions = [], {}
    for row in tasks:
        L, J = lex[row["id"]], judge.get(row["id"], {})
        reasons = []
        if max(L["max_jaccard_prompt"], L["max_jaccard_code"]) >= 0.5:
            reasons.append(f"5-gram Jaccard >= 0.5 ({L['max_jaccard_prompt_with']}/{L['max_jaccard_code_with']})")
        if L["longest_common_run"] >= 30:
            reasons.append(f"common run {L['longest_common_run']} tokens with {L['longest_run_with']}")
        judge_flag = bool(J.get("same_as") or J.get("well_known"))
        if judge_flag and row["id"] not in overrule:
            reasons.append(f"judge: same_as={J.get('same_as')} well_known={J.get('well_known')}")
        if row["id"] in extra:
            reasons.append(f"review: {extra[row['id']]}")
        decisions[row["id"]] = {"drop": bool(reasons), "reasons": reasons, "judge_flag": judge_flag,
                                "judge_overruled": judge_flag and row["id"] in overrule,
                                "max_jaccard": max(L["max_jaccard_prompt"], L["max_jaccard_code"])}
        if not reasons:
            meta = dict(row.get("meta", {}))
            meta["contam_max_jaccard"] = decisions[row["id"]]["max_jaccard"]
            meta["contam_longest_run"] = L["longest_common_run"]
            kept.append({**row, "meta": meta})
    with (ROOT / "data" / "decontaminated.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (REPORTS / "decisions.json").write_text(json.dumps({"overruled": overrule, "kept": len(kept), "decisions": decisions}, indent=1) + "\n")
    print(f"kept {len(kept)} of {len(tasks)}; dropped:", {k: v["reasons"] for k, v in decisions.items() if v["drop"]})


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("fetch", "lexical", "judge"):
        sub.add_parser(name)
    d = sub.add_parser("decide")
    d.add_argument("--overrule", nargs="*", default=[], help="judge-flagged ids rejected after manual review")
    d.add_argument("--extra-drop", nargs="*", default=[], help="id=reason drops from the second review (DeepSeek + author web check)")
    args = ap.parse_args()
    {"fetch": cmd_fetch, "lexical": cmd_lexical, "judge": cmd_judge}.get(args.cmd, lambda: cmd_decide(args.overrule, args.extra_drop))()


if __name__ == "__main__":
    sys.exit(main())
