"""Flag hidden-test traps that the spec does not state (data only; safe on Windows).

Why: the Gemma pilot (2026-11-20) failed 4 tasks by a single test each because the
test rejected non-ASCII digits/letters or a bool, while the spec said only "digits",
"letters" or "an int". That is a spec defect, not a fair trap: a model that follows the
spec as written is marked wrong. Self-checks cannot catch it because the reference and
the tests share the author's reading.

Heuristics (review each hit by hand; a hit is not automatically a defect):
- tests contain non-ASCII characters or \\uXXXX escapes, but the spec never says "ASCII";
- tests use True as an input tuple element, but the spec never mentions bool.
Usage: uv run python pipeline/lint_spec_traps.py [tasks/generated/...]
"""
import glob
import os
import re
import sys

BACKSLASH = chr(92)
NON_ASCII = re.compile(re.escape(BACKSLASH) + r"[uU][0-9a-fA-F]{4}|[^\x00-\x7f]")
BOOL_INPUT = re.compile(r"\(True, |\[True\]|True\)\]")


def lint(task_dir: str) -> list[str]:
    tests = open(os.path.join(task_dir, "tests.py"), encoding="utf-8").read()
    prompt = open(os.path.join(task_dir, "prompt.md"), encoding="utf-8").read().lower()
    hits = []
    if NON_ASCII.search(tests) and "ascii" not in prompt:
        hits.append("non-ASCII in tests, spec never says ASCII")
    if BOOL_INPUT.search(tests) and "bool" not in prompt:
        hits.append("True used in tests, spec never mentions bool")
    # A triple quote inside the docstring breaks any solution that copies the docstring
    # (found 2026-11-20: c0004's example '"say ""hi""";;x' gave DeepSeek and gpt-oss SyntaxErrors).
    raw = open(os.path.join(task_dir, "prompt.md"), encoding="utf-8").read()
    if raw.count('"""') >= 2:
        body = raw.split('"""', 1)[1].rsplit('"""', 1)[0]
        if '"""' in body or "'''" in body:
            hits.append("triple quote inside the docstring (copied docstrings will not parse)")
    return hits


def main() -> None:
    roots = sys.argv[1:] or ["tasks/generated"]
    dirs = sorted(d for r in roots for d in glob.glob(os.path.join(r, "**", "tests.py"), recursive=True))
    n = 0
    for t in dirs:
        hits = lint(os.path.dirname(t))
        if hits:
            n += 1
            print(os.path.basename(os.path.dirname(t)), "|", "; ".join(hits))
    print(f"{n} task(s) flagged for review out of {len(dirs)}")


if __name__ == "__main__":
    main()
