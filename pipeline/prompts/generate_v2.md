# generate_v2: task generation prompt

<!-- v2 (2026-11-18) adds the difficulty levers below; v1 is kept unchanged for the record. -->

<!-- Placeholders filled per candidate: {{SEED_ID}} {{CATEGORY}} {{SEED}} {{DIFFICULTY}} {{EXEMPLAR}} -->

Write one Python programming task grounded in the real-world rule below. The task will
be used to evaluate language models: they see only the specification you write, reply
with an implementation, and are scored by your hidden tests.

**Seed ({{SEED_ID}}, {{CATEGORY}}):** {{SEED}}
**Difficulty:** {{DIFFICULTY}}

Build a concrete function around the seed. Pick a specific variant, sub-problem or twist
so the task is not a textbook exercise. The task must not be a restatement of a well-known
puzzle or of any HumanEval, MBPP, LeetCode or Codeforces problem.

## Hard requirements

**Function shape** (the grader calls it from a separate process, exchanging plain data):
- One top-level function. Arguments and return values use only `int`, `float`, `str`,
  `bool`, `None`, `list`, `tuple`, `dict`, `set`, `frozenset`, `bytes`, nested.
- No classes as the entry point, no generators/iterators as return values, no checks that
  depend on mutating the arguments in place, no I/O, no randomness, no global state.
- Python 3.11 standard library only.

**Specification** (`prompt.md`): one ```python block holding the signature with type
hints and a docstring that states *every* rule the tests check. That covers:
- input constraints;
- exact output format and ordering;
- tie-breaking;
- rounding;
- which exception type to raise, and when;
- every edge-case behavior.

Never rely on the solver knowing a standard from memory; spell the rules out. Include 2-3
doctest-style examples. Keep it under about 40 lines.

**Reference** (`reference.py`): a correct, readable solution, at most about 80 lines.

**Tests** (`tests.py`), pytest, hidden from the solver:
- `from solution import <entry_point>` at the top. Call the function only inside test
  functions, never at import time.
- At least 12 checked cases in total, mostly via `@pytest.mark.parametrize`:
  - the docstring examples;
  - edge cases (empty input, boundaries, duplicates, maximum sizes, negative or unusual values);
  - inputs that do not appear in the specification.
- Each error rule tested with `pytest.raises(<ExactType>)`.
- When feasible, a differential test: an independent oracle in the test file, written
  with a *different*, simple or brute-force method (not a copy of the reference),
  compared on 100-200 inputs from `random.Random(<fixed seed>)`.
- Deterministic and fast (under about 2 s total). No files, network, stdout checks or
  timing assertions. Floats compared with `pytest.approx`.
- Only assert what the specification states. If the spec allows a list or a tuple,
  normalize before comparing.

**Mutants** (`mutants.py`): a Python list literal of exactly 3 `(description, find, replace)` tuples.
- Each patch, applied to `reference.py`, produces a plausible *single* bug of the kind a
  careful programmer might make: an off-by-one, a wrong tie-break, a missed edge case, a
  wrong boundary inclusion, a wrong rounding mode, a skipped validation.
- `find` must occur exactly once in `reference.py`.
- The result must still be valid Python.
- Your tests must make each mutant fail.

**Metadata** (`meta.json`):
```json
{"id": "<assigned id>", "entry_point": "<function name>", "topic": "<short topic>",
 "difficulty_hint": "{{DIFFICULTY}}", "seed_id": "{{SEED_ID}}",
 "generator": "<who generated it>", "prompt_version": "generate_v2",
 "levers": ["<twist|combo|efficiency|spec-trap>", "..."]}
```

## Difficulty levers (v2)

Make the task hard to solve from memory, the way strong interview questions are.
Use at least one lever for medium tasks and at least two for hard ones, and list them
in `meta.json` under "levers":
- **twist:** start from a familiar shape but change a rule so that a memorized answer
  to the familiar problem gives a *wrong* result (state the changed rule clearly).
- **combo:** the solution needs two techniques together (e.g. intervals + heap,
  DP + graph search, parsing + validation).
- **efficiency** (hard tasks): state the input limits in the docstring (e.g.
  "len(nums) <= 200_000"), include at least one test at that size, and add a sixth
  file `slow.py`: a correct but naive solution (e.g. O(n^2) where O(n log n) is
  intended). Calibrate N for a **1-vCPU sandbox** with wide margins so CPU jitter
  can't flip results:
  - the reference must finish the large call in **under 0.3 s, including argument
    transfer**;
  - `slow.py` must need **at least 10x the grader's 5 s per-call limit** (50 s or more) at that N.

  Arguments cross a process boundary as JSON (capped at 8 MB per message, and
  encoding costs time), so keep one call's arguments under about 1 MB. In practice
  that means about 20,000-50,000 scalars or small tuples. A quadratic-vs-n log n gap
  is the right size there; a constant-factor gap is not. The pipeline checks that
  `slow.py` fails *by timing out*, and `vf-validate` checks that the reference passes
  inside a real 1-vCPU Prime sandbox.
- **spec-trap:** rules that are easy to misread (tie-breaks, inclusive vs. exclusive
  bounds, ordering, empty input), each stated explicitly and each covered by a test.

If the task resembles a well-known problem, the twist must change the answer for
some tested inputs. A reworded copy of a known problem is not acceptable; the
contamination check will reject it.

## Difficulty guide
- **easy:** one main rule plus a few edge cases; reference about 10-25 lines.
- **medium:** several interacting rules or a non-obvious edge case; reference about 25-50 lines.
- **hard:** needs an algorithmic idea (DP, graph, sweep, search) or many interacting rules;
  reference about 40-80 lines.

## Example of the expected format and quality

{{EXEMPLAR}}

## Output

Return the five files `meta.json`, `prompt.md`, `reference.py`, `tests.py`, `mutants.py`, plus `slow.py` when the efficiency lever is used.
