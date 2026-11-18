# generate_v1: task generation prompt

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
 "generator": "<who generated it>", "prompt_version": "generate_v1"}
```

## Difficulty guide
- **easy:** one main rule plus a few edge cases; reference about 10-25 lines.
- **medium:** several interacting rules or a non-obvious edge case; reference about 25-50 lines.
- **hard:** needs an algorithmic idea (DP, graph, sweep, search) or many interacting rules;
  reference about 40-80 lines.

## Example of the expected format and quality

{{EXEMPLAR}}

## Output

Return the five files: `meta.json`, `prompt.md`, `reference.py`, `tests.py`, `mutants.py`.
