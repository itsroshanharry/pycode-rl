# generate_v3: task generation prompt

<!-- v3 (2026-11-20). Why: in the 20-task pilot at max_tokens 8192, DeepSeek V4.1 Flash solved
17/20 v1/v2 tasks 4/4 (mean 0.90), so the [1/8, 7/8] difficulty filter would drop about 85%
of them, and a leaderboard would have little headroom. Gemma 4 31B (mean 0.65) exposed 4
spec defects: traps that the tests checked but the spec never stated. v3 makes tasks harder
by construction and makes every trap explicit. v1 and v2 are kept unchanged for the record. -->

<!-- Placeholders filled per candidate: {{SEED_ID}} {{CATEGORY}} {{SEED}} {{DIFFICULTY}} {{EXEMPLAR}} -->

Write one Python programming task grounded in the real-world rule below. The task will
be used to evaluate language models: they see only the specification you write, reply
with an implementation in one turn (no tools, no feedback), and are scored by your hidden
tests. A strong reasoning model should NOT be able to solve a hard task reliably.

**Seed ({{SEED_ID}}, {{CATEGORY}}):** {{SEED}}
**Difficulty:** {{DIFFICULTY}}

Build a concrete function around the seed. Pick a specific variant, sub-problem or twist
so the task is not a textbook exercise. The task must not be a restatement of a well-known
puzzle or of any HumanEval, MBPP, LeetCode or Codeforces problem.

## Hard requirements (unchanged from v2 unless marked NEW)

**Function shape** (the grader calls it from a separate process, exchanging plain data):
- One top-level function. Arguments and return values use only `int`, `float`, `str`,
  `bool`, `None`, `list`, `tuple`, `dict`, `set`, `frozenset`, `bytes`, nested.
- No classes as the entry point, no generators/iterators as return values, no checks that
  depend on mutating the arguments in place, no I/O, no randomness, no global state.
- Python 3.11 standard library only.

**Specification** (`prompt.md`): one ```python block holding the signature with type
hints and a docstring that states *every* rule the tests check: input constraints, exact
output format and ordering, tie-breaking, rounding, which exception type to raise and when,
and every edge-case behavior. Include 2-3 doctest-style examples. Up to about 60 lines.

- **NEW: every trap must be stated.** If any test rejects or treats specially a class of
  input, the spec must name that class explicitly. The most common omissions:
  - "digits"/"letters" when only ASCII is accepted: write "ASCII digits 0-9";
  - "an int" when bool must be rejected: write "bool is not accepted (it is a subclass
    of int)";
  - "whitespace" vs "space" vs "tab";
  - empty input;
  - "-0" or negative zero;
  - leading zeros;
  - case sensitivity.

  A trap the spec does not state is a defect, not difficulty: a model that follows the spec
  as written is marked wrong. `pipeline/lint_spec_traps.py` checks the common cases.

**Reference** (`reference.py`): a correct, readable solution. NEW: up to about 120 lines
for hard tasks (about 50 for medium, 25 for easy).

**Tests** (`tests.py`), pytest, hidden from the solver:
- `from solution import <entry_point>` at the top; call the function only inside test functions.
- NEW: at least 20 checked cases (12 for easy), mostly via `@pytest.mark.parametrize`:
  the docstring examples, edge cases, and inputs that do not appear in the specification.
- NEW **one test per rule:** for every rule in the spec, at least one test that fails
  if that single rule is ignored or applied the "obvious" wrong way, with nothing else
  changed.
- NEW **make every step visible in the data:**
  - choose thresholds, bracket limits, rates and sizes so that each rule changes some
    output, avoiding round values that hide steps (lessons: rate tables with limits on
    500 g steps hid a "round up to 500 g" step, and a 20% rate hid a rounding bug);
  - use rates of 100%, odd prices, and boundaries that are not multiples of the step size.
- Each error rule tested with `pytest.raises(<ExactType>)`.
- A differential test against an independent oracle in the test file (a *different*,
  simple or brute-force method), on 100-500 inputs from `random.Random(<fixed seed>)`.
  For hard tasks this is required.
- NEW **no hand-computed expected values for anything non-trivial:** compute them with
  the oracle or a brute-force script and paste the result. Hand arithmetic was wrong
  more than 10 times in batches b04-b08.
- Deterministic, under about 2 s total (excluding the efficiency test's single large call).
  No files, network, stdout checks or timing assertions. Floats compared with `pytest.approx`.
- Only assert what the specification states.

**Mutants** (`mutants.py`): exactly 3 `(description, find, replace)` tuples. Each is a
plausible *single* bug a careful programmer might make; `find` occurs exactly once;
the result is valid Python; the tests kill each one. NEW: at least one mutant should
encode the most tempting wrong reading of the spec (the "obvious" misinterpretation).

**Metadata** (`meta.json`):
```json
{"id": "<assigned id>", "entry_point": "<function name>", "topic": "<short topic>",
 "difficulty_hint": "{{DIFFICULTY}}", "seed_id": "{{SEED_ID}}",
 "generator": "<who generated it>", "prompt_version": "generate_v3",
 "levers": ["<lever>", "..."]}
```

## Difficulty levers (v3)

NEW counts: **medium at least 2 levers, hard at least 3**, listed in `meta.json`.
v2 levers (unchanged):
- **twist:** a familiar shape with a changed rule so that a memorized answer is wrong.
- **combo:** two techniques together (e.g. intervals + heap, DP + graph search).
- **efficiency:** stated input limits, a large-input test, and `slow.py` (a correct naive
  solution) that must time out. Calibrate for a 1-vCPU sandbox: the reference finishes the
  large call in under 0.3-0.5 s including argument transfer; `slow.py` needs at least 50 s
  (10x the 5 s per-call limit). Keep one call's arguments under about 1 MB. **Required for
  every hard task in v3** unless the seed truly has no scalable input; say why in meta.json
  ("no_efficiency_reason").
- **spec-trap:** rules that are easy to misread, each stated explicitly and each tested.

NEW levers:
- **layered-rules:** five or more interacting rules with an explicit precedence order
  ("first ..., then ..., if both apply ..."). At least two tests where two rules conflict
  and only the stated precedence gives the right answer.
- **state-machine:** the input must be processed with three or more modes or states
  (e.g. quoting + escapes + nesting, or a protocol with phases). At least one test per
  transition, including the invalid ones.
- **exactness:** the correct answer depends on exact integer or rational arithmetic, very
  large values, or many digits, so that float or default-precision Decimal gives a wrong
  result on some tested input (lesson: a 35-digit value caught a model using floats).
- **composition:** two or more stages where one stage's output feeds the next (e.g. parse
  -> validate -> aggregate -> format), each with its own rules, so an error early on
  changes the final output.

If the task resembles a well-known problem, the twist must change the answer for some
tested inputs; a reworded copy is rejected by the contamination check.

## Difficulty guide (v3)
- **easy:** one main rule plus a few stated edge cases; still at least 1 lever.
- **medium:** several interacting rules or a non-obvious stated edge case; at least 2 levers.
- **hard:** an algorithmic idea (DP, graph, sweep, search, data structure) AND many
  interacting rules; at least 3 levers including efficiency. A strong reasoning model
  writing in one shot, without running code, should be expected to miss something.

## Example of the expected format and quality

{{EXEMPLAR}}

## Output

Return the files `meta.json`, `prompt.md`, `reference.py`, `tests.py`, `mutants.py`, and
`slow.py` when the efficiency lever is used.
