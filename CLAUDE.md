# CLAUDE.md: PyCode-RL Environment (Prime Intellect / verifiers v1)

Project context for Claude Code. Read fully before acting. Docs were read on 2026-11-16; the verifiers v1 API is still stabilizing, so **when code and this file disagree, trust `--help` output and the live docs**, then record the finding in `NOTES.md`.

---

## 1. Mission

Build and publish a **Python coding environment + task-generation pipeline** on Prime Intellect's Environments Hub, then run a **multi-model leaderboard** on it. This is a portfolio project targeting Prime Intellect's "Research Engineer - Data and Evaluation" role (build executable environments in Verifiers, write/test verifiers, investigate reward hacks, trace failures to model vs. harness vs. scoring, build RL data pipelines, test on held-out tasks).

**Deliverables**
1. `dataset.jsonl`: ~100-150 curated, validated, decontaminated coding tasks with hidden pytest suites, train/test split.
2. A verifiers **v1** taskset package published with `prime env push`.
3. Offline pipeline code (generate -> validate -> difficulty filter -> contamination filter -> split -> export), reproducible from scripts.
4. Leaderboard: 4-5 models x held-out tasks x multiple rollouts, with confidence intervals.
5. `REPORT.md`: rejection rate at every stage, pass-rate histogram, verifier-exploit findings, manual audit results, calibration against a public benchmark, honest limitations.
6. (Stretch) one PR to Prime's repos (`verifiers`, `prime-envs`, or docs).

**Non-goals:** RL weight training, local model serving, large datasets (quality over volume).

---

## 2. CORRECTIONS to the original spec (read first)

The earlier spec was written from the **v0 / legacy** workflow. The current docs say v0 is deprecated and the Hub lists v0 environments under "Legacy". Use v1.

| Original spec | Current reality (docs, 2026-11-16) |
|---|---|
| `SandboxEnv`, `load_environment()`, `vf-eval` | **v0/legacy.** Use `import verifiers.v1 as vf`: `vf.TaskData`, `vf.Task`, `vf.Taskset`, `@vf.reward`, `@vf.metric`, `Task.validate`, `vf.Runtime`. CLI: `vf-validate`, `vf-debug`, `vf-run`, `vf-gepa`. |
| Inference endpoint `https://pinference.ai` | **`https://api.pinference.ai/api/v1`**, key from `PRIME_API_KEY` (or `prime login`). |
| Sandbox "~$0.02/vCPU-hour" | That is only the CPU part. Full rate: **$0.02/vCPU-hr + $0.0125/GiB-hr memory + $0.0002/GiB-hr disk** (e.g. 1 vCPU/2 GiB/5 GiB = $0.046/hr). Launch rates are stated valid **through Dec 22, 2026**. |
| "Run `vf-eval` across the models" | `vf-eval` runs v0 envs only. For v1: `vf-run` (small local runs), `uv run eval` (lives in the **prime-rl** repo), or `prime eval run <owner>/<env> --hosted`. See section 9. |
| `--runtime.type docker` in doc examples | **Not allowed on this laptop.** Always use `--runtime.type prime`. |

Model IDs in section 5 were supplied by the user and **not verified**. Run `prime inference models` and confirm each ID and price before first use. If one is missing, stop and ask which substitute to use.

---

## 3. Hard constraints

**Local machine:** Windows laptop, VS Code + Claude Code extension, 16 GB RAM (~4 GB free), RTX 2050 (4 GB VRAM).
- Do **not** run local LLMs (Ollama/vLLM), Docker, or WSL2 (they eat the RAM headroom).
- Do **not** install torch, vllm, sentence-transformers, or other heavy ML packages locally. Contamination checks use exact n-gram/string similarity plus a remote LLM-judge rephrase check (no local embedding models).
- **Never execute model-generated code on the laptop.** The `subprocess` runtime runs on the evaluator host, so it is forbidden for anything touching model output. All code execution happens in **Prime Sandboxes** (`--runtime.type prime`).
- Commands must work in **PowerShell**. No bash-only syntax in scripts or docs; use Python for glue, not shell scripts.
- Python **3.12** (verifiers v1 needs >=3.11). Manage everything with `uv`.

**Money:** a single **$10 prepaid wallet** (balance $10.00, spend $0.00, **auto top-up not configured, keep it that way**) covers Prime Inference, Sandboxes, and Traces.
- Run a **pilot** (20 tasks x 4 rollouts) before any scaled run; measure real $/rollout and extrapolate.
- **Ask the user before any single step whose estimate exceeds $1**, and stop if projected total spend exceeds **$7** (keep >= $3 reserve).
- Always cap output tokens (`max_tokens`, start at 2048) and concurrency (`-c 8`).
- Turn off Prime Traces upload: `prime config set-traces-opt-out true` (needs a recent Prime CLI, >= 0.9.4) and `PRIME_TRACES_OPT_OUT=true` (traces cost $1/GiB ingested). Ask the user to also disable "Upload runs to Prime Traces" in dashboard Billing -> Usage Limits (account-level), and to set a usage limit there.

**Claude Pro sprint (30 days):** be token-frugal. Do not re-fetch docs you already summarized below; read `--help` and source code first. Keep `NOTES.md` as a running decision log so context survives across sessions.

**Secrets:** never commit keys. `.env` in `.gitignore`. Read `PRIME_API_KEY` from env only; never print it.

---

## 4. Prime platform primer (condensed from docs)

**Platform:** Environments Hub (registry) + Hosted Training/Eval + Sandboxes + Prime Inference (OpenAI-compatible). Environments are portable across local eval, hosted eval, and training.

**verifiers v1 concepts**
- **Taskset**: loader of work. `load()` returns a list or a generator of `Task`s. Generic: `Taskset[TaskT, ConfigT]`. Never override `__init__`.
- **TaskData**: immutable, serializable per-task record (prompt, files, references, image, workdir, resources, timeout, network, scoring, artifacts). **Extra fields you add (e.g. `tests`) stay on the evaluator and are never shown to the agent.** Set `TaskData.id` to a stable ID; `idx` is auto-assigned from stream order.
- **Task**: behavior for one problem: `setup`, `finalize`, `stage_verifier`, `validate`, `@vf.reward`, `@vf.metric`, `@vf.stop`. Set `NEEDS_CONTAINER = True` for tasks that run code in a sandbox.
- **Harness**: the program the model runs in (`null` = minimal, no shell tools; `bash` = shell+file-edit tools, own loop; Claude Code, Codex, etc. need containers).
- **Agent** = harness x model x runtime policy. **Environment** = control flow across agents (default: single agent). **Trace** = full record of a rollout (`trace.last_reply`, `trace.info`, `trace.reward`).
- **Runtime** (`vf.Runtime`): `await runtime.run(argv, env)` -> `ProgramResult(exit_code, stdout, stderr)` (nonzero exit does NOT raise), `read(path, max_bytes)`, `write(path, bytes)`, `prepare_uv_script`/`run_uv_script` (PEP 723 inline deps), `run_background`. **Python hooks (`setup`, `finalize`, `@vf.reward`) execute on the evaluator (laptop); only `runtime.*` calls act inside the sandbox.** `Path.read_text()` reads the laptop, not the sandbox.
- Runtime types: `subprocess` (host; forbidden here), `docker` (local; forbidden here), **`prime`** (remote Prime sandbox; default; the only one enforcing hard disk limits).
- **Lifecycle:** task `setup` -> harness setup -> agent run -> task `finalize` -> scoring (metrics, then rewards, then judges). Network policies take effect **after** setup, so `setup` can still install packages.
- **Scoring modes:** `shared` (score in agent's sandbox) or `isolated` (fresh container; only declared `artifacts` are copied; private files go in via `stage_verifier`). Set on `TaskData.scoring = vf.ScoringConfig(mode=...)` or `--env.agent.scoring.mode`.
- **Reward semantics:** `trace.reward` = sum of `score x weight`. Return `0.0` for a wrong answer; **let infrastructure errors raise** (never return 0.0 for a sandbox/grader failure, as it would record an infra fault as a model failure).
- Task selection: `-n N`, `-s` (shuffle), `--select.include.idx 0:100`, `--select.skip K`; shuffle runs before skip/limit so larger `-n` extends the same sample; skip+limit carve disjoint splits.
- Taskset ID is derived from the package name with underscores -> hyphens (`pycode_env` -> `pycode-env`).

**Reference implementations to study before writing code** (clone read-only, don't copy blindly):
- `PrimeIntellect-ai/prime-envs`: `environments/code/humaneval` ("packaged Python grader" pattern: the closest model for this project), `environments/code/scicode`.
- `PrimeIntellect-ai/research-environments`: production tasksets.
- Docs pages: `verifiers/building-environments`, `verifiers/runtimes#packaged-grader-scripts`, `verifiers/debugging`.

---

## 4b. Ground yourself BEFORE writing code (cheap, do this every new session)

The v1 API is still changing. Verify names against the installed version instead of guessing. Budget: ~3k tokens total, far cheaper than debugging hallucinated syntax.

1. **CLI flags:** `uv run vf-run --help`, `uv run vf-validate --help`, `prime env push --help`, `prime eval run --help`. Taskset flags only appear when the taskset ID comes first (`uv run vf-run pycode-env --help`).
2. **Python API (v1 names only):**
   ```powershell
   uv run python -c "import verifiers.v1 as vf; print([n for n in dir(vf) if not n.startswith('_')])"
   uv run python -c "import inspect, verifiers.v1 as vf; print(inspect.signature(vf.TaskData)); print(vf.Runtime.__doc__)"
   ```
   Inspect one class at a time (`vf.Task`, `vf.TaskData`, `vf.Taskset`, `vf.Runtime`, `vf.TaskResources`, `vf.ScoringConfig`). If a name used in section 8 does not exist, fix the code and log it in `NOTES.md`.
3. **Installed source:** on Windows it is under `.venv\Lib\site-packages\verifiers\` (or the editable checkout). Read only the specific file you need.
4. **One reference env:** shallow-clone `https://github.com/PrimeIntellect-ai/prime-envs` into a git-ignored `_refs/` folder and read only `environments/code/humaneval`.
5. **Ignore v0 material:** `SandboxEnv`, `Rubric`, `vf-eval`, `vf-init`, and `load_environment()` are legacy. Do not inspect or copy them.

---

## 5. Models and inference

- Base URL: `https://api.pinference.ai/api/v1` (OpenAI-compatible). Key: `PRIME_API_KEY`. Teams only: header `X-Prime-Team-ID`.
- List live catalog: `prime inference models` or `GET /models`. Use IDs exactly as shown.

| Role | Model ID (verify) | $/M in | $/M cached in | $/M out | Notes |
|---|---|---|---|---|---|
| Filter model + high-volume rollouts | `deepseek/deepseek-v4.1-flash-1017` | 0.0437 | 0.0024 | 0.70 | 1M ctx |
| Coding specialist | `poolside/laguna-s-2.1` | 0.09 | n/a | 0.18 | |
| Open-weight all-rounder | `qwen/qwen3.6-35b-a3b` | 0.11 | 0.099 | 1.01 | 262K ctx |
| Comparison | `google/gemma-4-31b-it` | 0.20 | 0.10 | 0.335 | 262K ctx |
| Optional heavy baseline | `openai/gpt-oss-120b` | 0.35 | n/a | 0.75 | 131K ctx |

**Design cautions (document in REPORT.md):**
- **Self-preference/selection bias:** if the filter model also appears on the leaderboard, difficulty is calibrated to it. Either filter with a model excluded from the leaderboard, or flag it and report on the held-out split.
- **Task authoring model:** prefer a model family that is *not* on the leaderboard. Claude Code itself is a valid generator (no wallet cost) if used through reproducible prompts saved in `pipeline/prompts/`. Otherwise generate with the cheapest suitable catalog model and note it.
- If a model is a reasoning model, output tokens can balloon: measure in the pilot and cap `max_tokens`.

---

## 6. Repository layout

```
.
|-- CLAUDE.md
|-- NOTES.md                    # decision log, doc ambiguities resolved, cost log
|-- REPORT.md                   # written at the end
|-- .env.example                # PRIME_API_KEY=  (never commit .env)
|-- pipeline/                   # OFFLINE: runs on laptop, orchestrates remote work
|   |-- prompts/                # generation prompts, versioned
|   |-- 01_generate.py          # LLM -> candidates.jsonl (spec, reference, tests, mutants)
|   |-- 02_validate.py          # drives vf-validate; keeps ids that pass gold+mutant check
|   |-- 03_difficulty.py        # drives vf-run -r 8 w/ filter model; computes pass rates
|   |-- 04_contamination.py     # exact n-gram overlap + LLM-judge rephrase check + (optional) perturbation test
|   |-- 05_split_export.py      # stratified train/test split -> dataset.jsonl
|   |-- 06_audit_sample.py      # random 40-task sample -> audit.csv for manual review
|   `-- stats.py                # Wilson CIs, pass-rate histograms
|-- data/                       # candidates.jsonl, validated.jsonl, dataset.jsonl, reports/
|-- tests/                      # light pytest for pipeline utils (laptop-safe)
`-- environments/pycode/        # the publishable verifiers v1 package
    |-- pyproject.toml
    |-- README.md               # shown on the Hub
    `-- pycode_env/                # flat layout: `prime env push` does not detect src/ layouts
        |-- __init__.py         # re-exports PyCodeTaskset
        |-- taskset.py
        |-- grader/run_pytest.py  # PEP 723 grader script (generic; no task tests inside)
        `-- data/dataset.jsonl    # bundled; must be included in the built wheel
```

**Dataset row schema (`dataset.jsonl`):**
```json
{"id":"pc-0001","split":"train|test","prompt":"<spec incl. function signature>","entry_point":"fn_name",
 "tests":"<pytest source, hidden from agent>","reference":"<gold solution>","mutants":["<buggy variant>", "..."],
 "meta":{"topic":"...","difficulty_hint":"...","pass_rate":0.5,"filter_model":"...","contam_max_jaccard":0.12,
         "generator":"...","version":"v1"}}
```

---

## 7. Pipeline stages (all offline; outputs are static files)

**Setup first:** `uv` install (PowerShell: `irm https://astral.sh/uv/install.ps1 | iex`), `uv tool install prime`, `prime login` (wallet already funded). Clone `PrimeIntellect-ai/verifiers`, `uv sync`, smoke test `uv run vf-validate reverse-text -n 1`. Preferably put the package under that checkout's `environments/` as the docs do (also makes a later PR easy; fork it).

**Stage 0: hand-write 10 tasks** (varied topics: strings, parsing, dp, data structures, numeric edge cases). Use them as few-shot exemplars and to shake out the grader end to end.

**Stage 1: generate** ~500 candidates: `(prompt/spec with signature + docstring, reference, pytest tests, 3 mutants)`. Diversify via a topic x difficulty x constraint matrix in the prompt (avoid textbook clones). **Seed-grounded synthesis** (decided 2026-11-18): ground each candidate in a small real-world seed (a date/time format, a version-comparison rule, a CSV/config dialect, a unit-conversion or scheduling rule, a protocol field layout), recorded in `meta.seed`, instead of inventing from a blank prompt. This avoids LeetCode-cliche collapse. Never use HumanEval/MBPP/LiveCodeBench problems as seeds. Task format stays single-function (pure functions over plain data, as the grader requires).
**Generator split** (decided 2026-11-18): Claude Code writes `pipeline/prompts/seeds.jsonl`, the versioned template `pipeline/prompts/generate_v1.md`, and the first ~50 candidates (`meta.generator = "claude-code"`). The remainder is generated by a cheap Prime catalog model, preferably a family not on the leaderboard, from the *same* template. That code lives **only** in its own self-contained script `pipeline/01b_generate_api.py` (no other module imports it), so it is easy to spot and delete after generation; its outputs keep `meta.generator = "<model id>"`. Report pass rates per generator. Tests: parametrized, include edge cases, no randomness without a fixed seed, deterministic, per-test timeouts, **no network/file I/O**, no reliance on stdout.

**Stage 2: validate (hard rule: every task must pass this to enter the dataset).**
Implement the task's `validate()` so that it returns `True` only if the **reference passes 100% of pytest in a Prime sandbox AND >= 2 of 3 mutants fail** (log the mutation score; LLM mutants are sometimes equivalent code, so do not demand 3/3). Run `uv run vf-validate pycode-env --runtime.type prime ...` over the candidate set. `vf-validate` also runs the no-op check (an untouched task must score 0): any task scoring >= 1.0 with no agent action is invalid. Outputs: `results.jsonl`, `summary.json`.

**Stage 3: difficulty filter.** Run the filter model with `-r 8` at temperature 1.0 on validated tasks. Keep tasks with pass rate in **[1/8, 7/8]**. For 0/8 tasks, first try **one rollout with a stronger model** (cheap triage: solvable means "hard", kept and flagged; still 0 means suspect), then inspect manually (usually broken tests or underspecified prompts); fix or drop. Save the histogram. The filter model may also appear on the leaderboard as a disclosed "calibration baseline" row.

**Stage 4: contamination** (revised 2026-11-16, see NOTES.md). Reference corpora: HumanEval (`openai/openai_humaneval`), MBPP (`google-research-datasets/mbpp`), LiveCodeBench (`livecodebench/code_generation_lite`; all releases). Verify dataset IDs and pin revisions before use.
(a) **Exact lexical overlap, all pairs** (about 500 x a few thousand is small, so no MinHash/LSH approximation is needed): normalized-token 5-gram Jaccard **and** longest common token run, on prompt and on reference. Drop on Jaccard >= 0.5 or a long verbatim run; log near-misses. This is the standard n-gram decontamination (GPT-3: 13-gram; GPT-4: 50-char).
(b) **Rephrase check (LLM decontaminator, LMSYS 2023):** n-gram checks miss paraphrases, and our generator is an LLM, so for each task take its top-k most similar benchmark problems from (a) and ask a cheap judge model, preferably not on the leaderboard, whether it is the same problem reworded, **and** (open question, no corpus) whether it is a well-known LeetCode/Codeforces-style problem and which one. Drop on "yes", log the judge's reason. Estimated < $0.10.
(c) Optional perturbation test: rename identifiers/constants, compare pass rates original vs. perturbed (large drop => suspect). (d) Optional memorization probe: give the first half of the prompt; flag verbatim completions. Report counts per check.

**Stage 5: split + export.** Stratify by topic and pass-rate bucket. ~70% train / 30% held-out test. Never tune prompts or thresholds on the test split after seeing its scores.

**Stage 6: manual audit.** Randomly sample 40 final tasks; for each record: spec ambiguity? tests over/under-constraining? reference correctness? Record the defect rate in REPORT.md. This step is not optional.

**Target funnel (report actuals):** ~10 hand-written -> ~500 generated -> ~300 validated -> ~150-200 after difficulty -> ~100-150 after contamination.

---

## 8. The verifiers v1 environment

Design: single-turn by default: **`null` harness + shared scoring**. The model has no tools, and the hidden tests are only written into the sandbox at scoring time, after the agent finishes, so there is nothing to tamper with and only one sandbox per rollout (cheapest). An agentic `bash`-harness variant (isolated scoring + `artifacts`) is an optional stretch.

Sketch (**verify every name against the docs/`--help` and the prime-envs HumanEval env; this is the shape, not guaranteed-exact code**):

```python
# environments/pycode/pycode_env/taskset.py
import json, re
from importlib.resources import files
import verifiers.v1 as vf

GRADER = files("pycode_env").joinpath("grader/run_pytest.py").read_bytes()
FENCE = re.compile(r"```(?:python)?\n(.*?)```", re.S)

def extract_code(reply: str) -> str:
    blocks = FENCE.findall(reply or "")
    return (blocks[-1] if blocks else (reply or "")).strip()

class PyCodeData(vf.TaskData):
    entry_point: str
    tests: str                 # hidden: never injected into the prompt
    reference: str
    mutants: list[str] = []

class PyCodeTask(vf.Task[PyCodeData]):
    NEEDS_CONTAINER = True

    async def setup(self, runtime: vf.Runtime) -> None:
        await runtime.run(["mkdir", "-p", "/work"], {})
        # Install pytest deps BEFORE network policy locks down (policy applies after setup).
        await runtime.prepare_uv_script(GRADER)

    async def _grade(self, runtime: vf.Runtime, code: str) -> dict:
        await runtime.write("/work/solution.py", code.encode())
        await runtime.write("/work/test_solution.py", self.data.tests.encode())
        res = await runtime.run_uv_script(GRADER, args=["/work"])
        if res.exit_code:                      # grader crashed => infra error, let it raise
            raise RuntimeError(res.stderr)
        return json.loads(res.stdout)          # {"score": 0.0|1.0, "passed": n, "total": m}

    # Shared-scoring mode: grade ONCE in finalize (runs in the agent sandbox right after the
    # agent ends, before anything mutates the workspace), store on trace.info, and let the
    # reward + metric read it. Avoids running the grader twice per rollout.
    # (If you switch to isolated scoring, finalize runs in the SOLVER sandbox, so grade inside
    # the reward instead and use stage_verifier; see docs "Separate agent and grading sandboxes".)
    async def finalize(self, trace: vf.Trace, runtime: vf.Runtime) -> None:
        code = extract_code(trace.last_reply)
        trace.info["grade"] = (
            await self._grade(runtime, code) if code
            else {"score": 0.0, "passed": 0, "total": 1}
        )

    @vf.reward
    async def all_tests_pass(self, trace: vf.Trace) -> float:
        return float(trace.info["grade"]["score"])

    @vf.metric
    async def frac_tests_passed(self, trace: vf.Trace) -> float:
        g = trace.info["grade"]
        return g["passed"] / max(g["total"], 1)

    async def validate(self, runtime: vf.Runtime) -> bool:
        await self.setup(runtime)
        if (await self._grade(runtime, self.data.reference))["score"] != 1.0:
            return False
        killed = sum([(await self._grade(runtime, m))["score"] == 0.0 for m in self.data.mutants])
        return killed >= max(2, int(0.67 * len(self.data.mutants))) if self.data.mutants else True

class PyCodeConfig(vf.TasksetConfig):
    split: str = "test"          # "train" | "test" | "all"

class PyCodeTaskset(vf.Taskset[PyCodeTask, PyCodeConfig]):
    def load(self) -> list[PyCodeTask]:
        raw = files("pycode_env").joinpath("data/dataset.jsonl").read_text(encoding="utf-8")
        rows = [json.loads(l) for l in raw.splitlines() if l.strip()]
        return [PyCodeTask(PyCodeData(
                    id=r["id"], name=r["id"], prompt=r["prompt"],
                    entry_point=r["entry_point"], tests=r["tests"],
                    reference=r["reference"], mutants=r.get("mutants", []),
                    image="python:3.11-slim", workdir="/work",
                    resources=vf.TaskResources(cpu=1, memory=1, disk=5),
                    timeout=vf.TaskTimeout(setup=300, agent=300, scoring=120),
                    network=vf.NetworkPolicyConfig(allow=[]),   # no egress after setup
                ), self.config.task)
                for r in rows if self.config.split in ("all", r["split"])]
```

`grader/run_pytest.py` is a **generic** PEP 723 script (`# /// script\n# dependencies = ["pytest"]\n# ///`) that runs pytest on `/work` with a per-test timeout, prints `{"score","passed","total"}` as JSON on stdout, and exits 0 for wrong/crashing submissions (nonzero only if the grader itself could not run).

**Anti-hacking checklist (implement + test each; these become REPORT.md findings):**
- Tests hidden (TaskData field, written only at scoring). Prompt never leaks test code.
- Solution cannot hardcode: tests must include inputs not derivable from the prompt examples; add differential check vs. `reference` on seeded random inputs where feasible.
- Solution cannot read tests/reference: the model has no shell (null harness); with a `bash` harness, switch to **isolated** scoring and keep tests out of the solver sandbox.
- `sys.exit(0)`, `os._exit`, monkeypatching pytest, printing "passed", or overriding `assert`: write adversarial "cheat" submissions as unit tests of the verifier and confirm they score 0.
- Timeouts for infinite loops; memory/CPU limits via `TaskResources`; no network (`allow=[]`).
- Empty/placeholder code, markdown-only replies, wrong function name: all must score 0.
- Verify scoring edge: truncated outputs (consider `agent.scoring.skip_on_truncated`); set `max_tokens`.

**Packaging:** scaffold per the docs:
```powershell
uv init --lib --build-backend hatch --no-workspace --python '>=3.11' environments/pycode
uv add --project environments/pycode --editable "$PWD"     # from the verifiers checkout root
uv pip install -e environments/pycode
```
Ensure `data/dataset.jsonl` and `grader/run_pytest.py` are **included in the wheel** (hatch include config), or Hub installs will break. Re-export `PyCodeTaskset` in `__init__.py`. No `[tool.uv.sources]` for URL deps (use PEP 508 direct references).

**Test ladder (cheap -> expensive; do not skip rungs):**
```powershell
uv run vf-validate pycode-env --runtime.type prime -n 1 --only-setup
uv run vf-validate pycode-env --runtime.type prime -n 3 --only-gold
uv run vf-validate pycode-env --runtime.type prime -n 3 --only-noop
uv run vf-run pycode-env -n 1 -r 1        # first model call; check flags with: uv run vf-run pycode-env --help
```
`vf-validate`/`vf-debug` boot **paid sandboxes**. Keep `-n` small until they work. `vf-validate` does not call `stage_verifier` automatically in isolated mode; if you move to isolated scoring, exercise it via a real `vf-run` rollout.

---

## 9. Evaluation and leaderboard

Models and endpoint: Prime Inference (default when logged in). Configure model, sampling (`temperature`), `max_tokens`, `-n`, `-r`, `-c` per `--help`.

Decision order (resolve empirically; record in NOTES.md):
1. **`vf-run`** (verifiers repo): works locally, saves traces. Use for pilots and, if it supports model/endpoint flags and is stable, for the leaderboard (loop over models in a Python script).
2. **`prime eval run <owner>/pycode-env --hosted -m <model> -n <N> -r 4 --follow`**: requires the env to be pushed to the Hub. With Prime Inference the hosted sandbox runtime is not billed separately, but **confirm hosted evals accept v1 tasksets** with a tiny run (`-n 5 -r 1`); the hosted docs still mention `load_environment()`.
3. **`uv run eval`** is documented in the **prime-rl** repo; it may not install on Windows. Do not fight the install; fall back to 1 or 2.

Protocol:
- Evaluate on the **held-out test split only** (and report train separately if useful). Same tasks, same sampling params, same harness/prompt for every model. 4 rollouts per task, temperature fixed and recorded.
- Report per model: mean pass rate with **Wilson 95% CI** (task-level bootstrap if rollouts are correlated), **pass@1, pass@k and pass^k** (pass^k = solved on all k attempts, i.e. reliability), frac-tests-passed metric, truncation/error rates, mean tokens, $/task. Use **paired** comparisons between models (same tasks) when claiming one beats another; about 50 test tasks gives roughly +/-13-point CIs.
- **Failure-mode breakdown** per model (chart for README/REPORT), from the grade fields: no_code, load_error (syntax/import), call timeouts, truncated (hit max_tokens), wrong answer (ran but failed tests), infra error.
- **Calibration:** run the same models on a small LiveCodeBench slice (or HumanEval/MBPP subset) and compare to published numbers to validate the harness. Then compare model rankings on your tasks vs. the public benchmark; report where your tasks separate models better (or worse).
- Save raw outputs (`results.jsonl`) under `data/reports/`; commit summaries, not secrets.

---

## 10. Budget plan (estimates; replace with pilot actuals)

| Step | Rough cost |
|---|---|
| Generation (~500 tasks + mutants, ~1.25M out tokens) | ~$0.9 via DeepSeek flash, or $0 if Claude Code authors them |
| Gold/mutant validation (sandboxes only) | ~$0.2-0.5 |
| Difficulty filter (~300 x 8 rollouts) | ~$1.5-3 (depends on token use; check pilot) |
| Leaderboard (4-5 models x ~40-60 test tasks x 4) | ~$1-2 |
| **Planned total** | **~$4-7. Hard stop at $7.** |

Sandbox math: 1 vCPU/1 GiB/5 GiB ~ $0.034/hr (launch rates through Dec 22, 2026). Always delete stray sandboxes (`prime sandbox list`, `prime sandbox delete <id>`). Log every paid run's estimated and observed cost in `NOTES.md`.

---

## 11. Publishing and contributing

- From `environments/pycode/`: `prime env push` (use `--auto-bump` for version bumps; `--visibility PRIVATE` while testing; public at the end). Requires a username set on the Prime profile and `prime login`. Install by others: `prime env install <owner>/pycode-env`.
- README on the Hub must state: what the tasks are, how they were generated (AI-generated, with the validation funnel numbers), verifier design, known limitations.
- **PR target:** after publishing, look for a small useful contribution to `PrimeIntellect-ai/verifiers` or `prime-envs` (docs fix, bug, or a new env). Read their PR guidelines first. Open PRs only with the user's approval of the diff.

---

## 12. Phases and exit criteria (30-day sprint)

| Phase | Work | Exit criteria |
|---|---|---|
| 1 (days 1-5) | Setup, read reference envs, scaffold package, 10 hand-written tasks, verifier + anti-hack unit tests | `vf-validate` gold/noop pass on all 10; `vf-run -n 1` returns a score; cheat-submission tests all score 0 |
| 2 (days 6-12) | Generation + gold/mutant validation | >= 300 validated candidates; funnel stats logged |
| 3 (days 13-18) | Difficulty filter, contamination, audit, split | `dataset.jsonl` frozen with hash recorded; audit defect rate written down |
| 4 (days 19-24) | Publish to Hub, pilot, calibration run, leaderboard | Leaderboard table with CIs; calibration vs. public benchmark done |
| 5 (days 25-30) | REPORT.md, README polish, optional PR | Reproducible from scripts; every claim in REPORT.md backed by a file in `data/reports/` |

---

## 13. Working rules for Claude Code

1. **Plan before spending:** state estimated $ and sandbox-hours before any paid run; ask approval above $1/step.
2. **No guessing APIs:** run `--help`, read installed package source, or read the reference envs. If docs and behavior conflict, test with the smallest possible run and log it in `NOTES.md`.
3. **Determinism:** seeds everywhere; pin dataset revisions; record `dataset.jsonl` SHA-256 and the generator prompt version.
4. **Small steps, commit often**, with messages describing the funnel counts or finding.
5. **Explainability:** the user must be able to explain every verifier and pipeline decision in an interview. Add short comments on *why* (what exploit a check blocks), and summarize non-obvious design choices in `NOTES.md`.
6. **Don't self-grade:** validation, contamination, and audit steps are independent of whichever tool authored the tasks.
7. **Safety:** model-written code runs only in Prime Sandboxes. Never `exec`/`eval` model output locally. Never print or commit keys.
8. **Be honest in the report:** include rejection rates, unresolved defects, and where the environment is weak.
9. If blocked on access, billing, or a missing model ID, stop and ask. Do not substitute silently.

---

## 14. Docs index

- Platform: https://docs.primeintellect.ai/platform-overview.md
- Full index: https://docs.primeintellect.ai/llms.txt
- verifiers v1: `/verifiers/overview.md`, `/getting_started.md`, `/building-environments.md`, `/tasksets.md`, `/runtimes.md`, `/debugging.md`, `/harnesses.md`, `/agent.md`, `/env.md`
- Hub: `/tutorials-environments/create.md` (v0-flavored; `prime env push` flow still applies), `/tutorials-environments/evaluating.md`, `/tutorials-environments/hosted-evaluations.md`
- Inference: `/inference/overview.md`; Sandboxes: `/sandboxes/overview.md`; Traces pricing: `/traces/pricing-and-settings.md`; prime-rl eval: `/prime-rl/eval.md`
- Repos: github.com/PrimeIntellect-ai/verifiers, /prime-envs, /research-environments, /prime-rl
