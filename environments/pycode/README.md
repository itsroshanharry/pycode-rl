# pycode-env

Single-turn Python function-implementation tasks. The model receives a function
specification (signature, docstring, examples) and replies with code; the code is graded
by a hidden pytest suite inside a Prime sandbox. Reward is 1.0 iff every hidden test passes.

> Status: development. This version ships 10 hand-written tasks (split `train`) used to
> validate the environment end to end. The generated, filtered and decontaminated dataset
> (with a held-out `test` split) will replace it.

## Usage

```bash
prime eval run itsroshanharry/pycode-env --hosted -m <model> -n 5 -r 1 -a '{"config": {"taskset": {"split": "train"}}}'
uv run vf-run pycode-env --env.taskset.split train -n 1 -r 1 -m <model>
```

Taskset options: `split` = `train` | `test` | `all` (default `test`).
Task options: `call_timeout` (default 5 s per call), `total_timeout` (default 60 s per solution).

## Design

- **Harness:** `null` by default (no tools). Shared scoring in the same sandbox. The sandbox has no network access once the agent starts.
- **Hidden tests:** stored as extra `TaskData` fields. They never appear in the prompt and are written into the sandbox only for grading.
- **Grader** (`grader/run_pytest.py`): trusted pytest runs in one process; the candidate runs in a separate worker that:
  - runs as an unprivileged user;
  - has rlimits, per-call and total timeouts, and fd-level silenced output;
  - talks to the test process over a JSON plain-data protocol (no pickle).

  This defeats the cheats we tested: rigged `__eq__` objects, printing fake results, patching pytest, `sys.exit`/`os._exit`, reading the hidden tests, and killing the grader. A grade from a non-isolated worker is refused.
- **Validation** (`vf-validate`): the reference must pass every test, at least 2 of 3 mutants must fail, and an untouched task must score 0.
- **Task constraint:** pure functions over plain data (no class entry points).

## Limitations

- Hidden tests are bundled in this package and recorded in traces. They are hidden from the model, but not secret.
- The current dataset is small and hand-written; see the status note above.
