# NOTES.md: decision log

Running log of doc ambiguities resolved, design decisions, and cost. Newest first.

---

## 2026-11-16: Phase 1 built and verified (spend so far: about $0.002)

**Grader design** (`environments/pycode/src/pycode_env/grader/run_pytest.py`, docstring has the threat model):
- Trusted pytest runs in the grader process. The candidate runs in a separate spawned worker behind a `solution` proxy module. Calls cross as **JSON with a tagged exact-type codec** (no pickle: a malicious worker could otherwise execute code in the grader).
- As root, the worker drops to uid 65534. Also: rlimits (AS 512 MB, FSIZE 0, NPROC 32, no core dumps), fd-level `/dev/null` stdio, per-call 5 s and total 60 s timeouts, `PYTHONHASHSEED=0`.
- Input files are deleted on read; hidden tests live only in a 0700 temp dir.
- Exit 2 (raises in the task) for broken or empty test files, so a task bug is never scored as a model failure.
- **Dataset constraint this implies:** pure functions over plain data (no class entry points, no in-place mutation checks, no generators).
- The taskset **refuses a grade with `isolated: false`**, so a scoring path that could read the tests never produces a reward.

**Cheat suite** (`tests/test_grader.py`, 19 cheats + 4 legit + 3 protocol tests): **26/26 pass as root** in the Codespace.
- Cheats covered: empty, wrong name, hard-coded examples, `sys.exit` on import, `os._exit`, `raise SystemExit` / `KeyboardInterrupt`, always-equal object, int subclass with rigged `__eq__`, printing a fake result (Python and fd level), patching `_pytest` and `AssertionError`, reading the hidden tests, killing the grader, writing `conftest.py`, infinite loop (in a call and at import), memory bomb, 100 MB return value, syntax error.
- **Control experiment (REPORT finding):** without the uid drop, `read_hidden_tests` scores **8/8 (reward 1.0)** and `kill_grader` kills the grader (exit 137). The privilege drop is what defeats both.

**Hand-written tasks** (`tasks/handwritten/`, built by `pipeline/00_build_handwritten.py`; data sha256 `ecb878e9...f2a8`):
- 10 tasks across strings, parsing, DP x2, data structures, numeric, graphs, sweep line, wrapping, and binary search. Each has 10-33 hidden tests, and most include a differential check against an independently written oracle on seeded random inputs (anti-hard-coding).
- Mutants are `(desc, find, replace)` patches over the reference. **30/30 mutants killed.**
- No prompt contains a test line or a reference-body line (checked).

**Test ladder (Prime sandboxes, from the Codespace):**
- `--only-setup` -n 1: valid, 12 s.
- `--only-gold` -n 3 and `--only-noop` -n 3: 3/3 each.
- Full gold+noop on all 10: **10/10 valid**, 0 stray sandboxes.
- `vf-run -n 1 -r 1` with `deepseek/deepseek-v4.1-flash-1017`, `--sampling.reasoning_effort low --sampling.max_tokens 2048`: **reward 1.0**. `harness=null`; the egress policy allowed only the tunnel host. The grade had 14/14 tests and `isolated: true`. Usage: 290 prompt tokens, **1294 completion (884 reasoning) at effort=low**, so 2048 is close to the cap; watch truncation in the pilot. Token cost about $0.0009 per rollout.
- **Phase 1 exit criteria met:** gold/noop pass on all 10, `vf-run` returns a score, every cheat scores 0.
- Wallet 10.0000 -> 9.9987 (sandbox rows may still be posting).

---

## 2026-11-16: Project setup + Windows blocker

- Root dev project `pyproject.toml` (Python 3.12, `package = false`) pins `verifiers` to git `20c549f` (the runner's). It resolves as **0.4.1.dev150, identical to the runner**. `pycode-env` is installed editable from `environments/pycode`. `.venv` is about 300 MB; no torch.
- `environments/pycode/pyproject.toml`: `verifiers>=0.4.1.dev150`. A higher floor (e.g. prime-envs' current `>=0.4.2.dev47`) would make the runner pull a newer verifiers from PyPI. Removed the `authors` line that `uv init` filled from this machine's git identity (a work account), plus the nested `.git`.
- **BLOCKER: verifiers v1 runtimes do not import on native Windows.** `verifiers/v1/runtimes/limiters.py` and `runtimes/native_compose.py` do `import fcntl` (Unix-only), in both the runner's commit and `main`. So `vf-validate`, `vf-run`, `vf-debug`, and anything touching `vf.Runtime` fail with `ModuleNotFoundError: fcntl`. Other Unix-only bits: `os.killpg` (subprocess/docker backends) and `prctl` (MCP server). Hosted evals are unaffected (Linux). Data-only pipeline steps (generation, contamination, stats) are unaffected.
- Options: (A) run verifiers CLIs inside a Prime sandbox; (B) GitHub Codespaces (Linux, free monthly quota, VS Code attaches, no laptop RAM); (C) a local `fcntl` shim (hack, may hit more issues); (D) WSL2/Docker (excluded by CLAUDE.md).
- **Decision: (B) GitHub Codespaces.** Rule: verifiers CLIs (`vf-validate`, `vf-run`, `vf-debug`) run in the Codespace; editing, data scripts, and `prime eval run --hosted` can run on Windows.
  - Repo: private `itsroshanharry/pycode-rl`. Commits use a repo-local identity (Roshan Kumar); the laptop's global git identity belongs to someone else, so never change it. `gh` active account is `itsroshanharry` (Nikhil's accounts are still logged in, inactive). The token has no `workflow` scope, so `gh auth refresh -s workflow` is needed before pushing `.github/workflows`.
  - `.gitattributes` forces LF (global `core.autocrlf` would otherwise convert to CRLF).
  - Codespace `pycode-rl-dev-x765vwxpjwjf4p9`: 2-core `basicLinux32gb`, `--idle-timeout 10m`. Devcontainer = `mcr.microsoft.com/devcontainers/base:1-bookworm` + sshd feature. uv manages Python 3.12. (The `devcontainers/python` image's yarn apt repo has a bad GPG key, which made the sshd feature fail and dropped us into an Alpine *recovery* container: check `/workspaces/.codespaces/.persistedshare/RECOVERY-REASON-FILE`.)
  - Verified inside: Python 3.12.16, verifiers 0.4.1.dev150, `vf-validate --help` OK, Prime CLI 0.21.0, `.venv` 355 MB.
  - `PRIME_API_KEY` is a Codespaces user secret (selected repo only). It is visible in **login shells only**, so use `gh codespace ssh -c <cs> -- 'bash -lc "..."'`. `prime whoami` inside the Codespace works (`itsroshanharry`, 16-sandbox cap).

---

## 2026-11-16: Hosted probe, `primeintellect/humaneval` (eval `ndwnprmnzutjxj4wsb69l6v3`)

Command: `prime eval run primeintellect/humaneval --hosted -m deepseek/deepseek-v4.1-flash-1017 -n 2 -r 1 -c 2 -S '{"reasoning_effort":"low","max_tokens":2048}' --timeout-minutes 120 --eval-name probe-humaneval-v1 --follow`

- **Hosted v1 confirmed.** The runner banner reads "Prime Intellect Hosted Evaluation (verifiers v1 on prime-rl)". It installs **prime-rl @ `3bd59c1`** (prime-rl 0.10.0) and builds **verifiers from prime-rl's `deps/verifiers` submodule**, then runs `uv run eval '<owner>/<env>@<version>' --model ... -n ... -r ...`. It spun up one Prime sandbox per rollout ("sandbox ... up").
- **Both rollouts errored (100% error, reward 0):** `TaskError: task HumanEvalTask scoring: AttributeError: 'Runtime' object has no attribute 'prepare_execution'`. **Root cause (verified):** the Hub copy of `primeintellect/humaneval` (0.1.0, published 2026-09-13) has `taskset.py:56 await runtime.prepare_execution(VERIFY_NETWORK_ROUTES)`, an API since removed. The GitHub version was fixed on 2026-10-19 (`scoring.network`) but **never re-pushed to the Hub**. The runner's verifiers (`20c549f`) is internally consistent: it only calls `runtime.backend.prepare_execution`. *(Corrects an earlier note that blamed runner version skew.)* This is a candidate issue/PR for Prime (stretch deliverable 6).
- Runner versions: prime-rl `3bd59c1` (2026-11-03, 82 commits behind main on 2026-11-16) bundles verifiers `20c549f` (2026-11-03, 54 behind main).
- **LESSON:** hosted runs execute our package with the runner's bundled verifiers, so develop against that commit (`20c549f`) rather than `main`. This removes one source of skew; it is not proof of compatibility. The proof is a hosted `-n 1 -r 1` smoke test after every push.
- Per-rollout results: the runner logged "Prime Traces committed episodes=2" with traces on, and the dashboard has a Traces tab.
- CLI bug on Windows: `prime eval run ... --follow` crashes printing a check mark (cp1252) *after* creating the eval. Always set `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8`. Never re-run on that crash (it would create a duplicate eval).
- Cost: wallet 10.0000 -> 9.9996. Billing rows: inference $0.0004; runner sandbox $0.0084; 2 rollout sandboxes $0.0001 each. Only the inference row has been deducted so far. Re-check whether the sandbox rows get charged ("runtime not billed separately").

---

## 2026-11-16: Toolchain + login (no spend)

- uv on PATH: **0.13.8** (`Python313\Scripts\uv.exe`). A stale standalone uv 0.10.12 sits in `~\.local\bin`; it is shadowed by PATH order, so harmless.
- Prime CLI **0.21.0** via `uv tool install prime --python 3.12`, at `~\.local\bin\prime.exe`. Its help text says to pass `--plain` for agent use.
- `prime login --max-concurrent-sandboxes 16 --max-concurrent-tunnels 16`: personal account, all scopes RW except billing/factory (read-only). The API key is capped at 16 concurrent sandboxes and 16 tunnels, a guard against the `-c 128` defaults. To change it, log in again with new caps.
- Wallet: **$10.00, 0 billing rows.** 0 sandboxes running. Client `traces_opt_out = false` (left unchanged pending the H8 decision).
- **Prime username is NOT set** ("Username: Not set"). `prime env push`, and therefore hosted evals, need it. The user has to set it in the dashboard profile.

---

## 2026-11-16: Hosted evals research (no spend)

Sources: docs `tutorials-environments/hosted-evaluations.md`, `evaluating.md`, `api-reference/hosted-evaluations/create-hosted-evaluation.md`, `traces/*` (fetched 2026-11-16); Prime CLI source `_refs/prime-cli` @ `ffe0de2` (2026-11-13), mainly `commands/evals.py`, `utils/eval_config.py`, `utils/environment_runtime.py`; public Hub endpoint `GET api.primeintellect.ai/api/v1/environmentshub/<owner>/<name>/@latest`.

**Decision: hosted evals (`prime eval run <owner>/pycode-env --hosted`) are the primary path for the leaderboard.** This changes CLAUDE.md section 9's decision order.

| # | Finding | Implication |
|---|---|---|
| H1 | `prime eval run` **without `--hosted` no longer runs anything**. It prints "prime no longer runs evaluations locally" and exits. | CLAUDE.md option 2 is hosted-only. Local runs stay `vf-run` (or prime-rl `uv run eval`). |
| H2 | **v1 support: strong evidence, no explicit doc statement.** (a) `prime env push` classifies packages as `VERIFIERS_V1` when the `verifiers` lower bound is >= 0.2.0 (or with `--runtime v1`). (b) The hosted CLI folds TOML `taskset = {...}` / `harness = {...}` into `env_args.config.{taskset,harness}`, which is the v1 shape. (c) Prime Traces "supports the verifiers v1 trace format". (d) Prime's own v1 envs are public on the Hub (`primeintellect/humaneval`, `primeintellect/livecodebench`, tags `v1`, `verifiers>=0.3.1`). (e) Hosted defaults `allow_sandbox_access=true` and `allow_tunnel_access=true` match the v1 prime-runtime design (one sandbox per rollout plus a tunnel). However, the hosted docs still say `env_args` go to `load_environment()`, and the API forwards v0 flags (`--independent-scoring`, `--state-columns`). | **Probe before building on it:** a hosted run of Prime's own v1 `primeintellect/humaneval` with `-n 2 -r 1` (pennies). It also measures billing rows and trace behavior. |
| H3 | Hosted runs **always use the `@latest` published version**; the CLI resolves `/@latest` even when the local code differs. No pinning. | Freeze the package during the leaderboard (no `prime env push`). Record the Hub `version_id` and `sha256` before and after each batch. |
| H4 | **Hosted runs expose almost no v1 agent knobs.** Only `env_args` (with `config.taskset` / `config.harness`), `sampling_args`, `max_tokens`, `temperature`, `-n`, `-r`, `-c`, `--max-retries`. There is no way to set `agent.runtime`, `agent.scoring.mode`, `max_turn_tokens`, timeouts, or `select` (no shuffle or skip). | **The package must configure itself.** Make the `null` harness the default via an exported `Env` with `vf.AgentConfig(harness={"id": "null"})` instead of relying on `config.harness` being honored. Put resources, timeouts, network, and scoring on `TaskData`. Select the split through `env_args.config.taskset.split`. |
| H5 | No shuffle: `-n N` takes the **first N tasks in `load()` order**; `-n -1` means all. | Store `dataset.jsonl` in a pre-shuffled, stratified, seeded order so `-n 20` pilots are representative. Evaluate the full test split with `-n -1`. |
| H6 | CLI defaults when flags are omitted: model `openai/gpt-4.1-mini`, `-n 5`, `-r 3`. `max_concurrent` is forwarded only if given (the server may auto-compute). Timeout defaults to 1440 min (CLI docs: min 120, max 1440; API: finite 60..5256000). | Always pass `-m`, `-n`, `-r`, `-c`, and `--timeout-minutes 120`. |
| H7 | **`reasoning_effort` handling differs by input path.** A TOML `[sampling]` or `sampling_args` table moves `reasoning_effort` / `enable_thinking` into `extra_body.chat_template_kwargs` (`_normalize_sampling_args`). The CLI `-S '<json>'` path passes JSON through unchanged. | For Prime Inference models, pass `-S '{"reasoning_effort":"low","temperature":...,"max_tokens":...}'` on the CLI, from a Python driver script (PowerShell JSON quoting is fragile). Confirm in the probe that the effort reaches the model (check token counts). |
| H8 | **Traces vs results.** Hosted runs upload to Prime Traces when the *workspace* setting is on. The client opt-out (`prime config set-traces-opt-out`, `PRIME_TRACES_OPT_OUT`) controls this machine's Prime Runs routing, and opted-out runs fell back to *legacy sample storage*, **retired 2026-11-06**. With uploads off, per-rollout hosted results may not be stored anywhere. | **Revisit CLAUDE.md's "turn traces off".** At our scale traces are cheap: about 900 leaderboard traces at roughly 30 KB each is about 27 MB, about $0.03 ingestion at $1/GiB. Recommend keeping workspace uploads **on** for hosted evals with a low usage limit, and pulling per-rollout data via `prime traces list --run-id ...` / `prime traces get <id> --raw` for the CIs. Needs the user's decision. |
| H9 | Hidden tests ride in `trace.task.data`, so they are uploaded to Prime Traces (workspace-private) and ship in the Hub package. | Already in limitations (finding #12). Use `--visibility PRIVATE` until the final push. |
| H10 | Billing. With Prime Inference (no `--api-base-url`), tokens are billed at catalog rates and "the hosted evaluation sandbox runtime is not billed separately". **Unclear whether the per-rollout Prime sandboxes the v1 runtime spawns are billed.** `GET /api/v1/billing/wallet` returns the balance plus up to 100 recent billing rows. | Measure real $/rollout from billing rows after the humaneval probe and after the pilot. |
| H11 | Hosted runs execute on Prime's Linux infra, so the **Windows `prime_tunnel`/frpc risk (finding #15) does not apply to them**. It still applies to local `vf-run` pilots. `vf-validate` needs no tunnel (no model), so Stage 2 works locally either way. | Another reason to prefer hosted for model runs from this laptop. |
| H12 | Stage 3 (difficulty filter, about 300 tasks x 8 rollouts) can also run hosted, but only on the `@latest` push. Do it with a PRIVATE push whose dataset holds the validated candidates (e.g. `split="candidates"`), then push the final dataset later. | Decide when we reach Stage 3. Older Hub versions may stay downloadable. |

**Useful commands (from CLI source):** `prime eval run <slug|config.toml> --hosted [--follow]`, `prime eval list` (Type column HOSTED/LOCAL), `prime eval get <id>`, `prime eval samples <id>`, `prime eval logs <id> -f`, `prime eval stop <id>`, `prime env push [--visibility PRIVATE] [--auto-bump] [--runtime v1]`, `prime env info <slug>`.

---

## 2026-11-16: Session 1, grounding (no spend)

**State:** workspace had only CLAUDE.md. Shallow clones (read-only) in `_refs/`:
- `verifiers` @ `672d020` (2026-11-15)
- `prime-envs` @ `b41d875` (2026-11-12; envs pin `verifiers>=0.4.2.dev47`)

**Local toolchain:** git 2.51, gh, Python 3.13.5 (system), **uv 0.10.6 (pip-installed under Python313\Scripts)**, **`prime` CLI not installed**.

### Verified against source (code wins over CLAUDE.md where they differ)

| # | Topic | Finding | Action |
|---|---|---|---|
| 1 | uv version | verifiers `pyproject.toml` sets `required-version = ">=0.11.1"`; installed 0.10.6 will refuse `uv sync`. uv came from pip, so `uv self update` won't work. | Upgrade with `python -m pip install -U uv` (or switch to the standalone installer) before setup. |
| 2 | **Default harness is `bash`, not `null`** | `default_harness_id()` returns `bash` unless the taskset package exports a `Harness`. With bash + shared scoring the agent could plant `conftest.py`/`sitecustomize.py` or tamper with the grader venv. | Ship a small `Env` with `vf.AgentConfig(harness={"id": "null"})` exported in `__all__` (docs: env.md "Role defaults"), and/or always pass `--env.agent.harness.id null`. Document that `bash` requires `--env.agent.scoring.mode isolated`. |
| 3 | `vf-run` default model | `RunnerConfig.model` defaults to `deepseek/deepseek-v4-flash` (gateway, **$0.44 in / $1.32 out**, about 10x the planned filter model). | Always pass `-m` explicitly. |
| 4 | Default concurrency | `vf-run` and `vf-validate` both default `-c 128` (up to 128 live sandboxes). | Always pass `-c 8`. |
| 5 | Reasoning defaults | `deepseek/deepseek-v4.1-flash-1017` has `default_effort: "max"`, enabled by default. All 5 leaderboard models support reasoning. Reasoning tokens count against `max_tokens`, so 2048 may truncate. | Set `sampling.reasoning_effort` explicitly (supported: none/low/high/max), record it, and measure in the pilot. Consider `skip_on_truncated`. |
| 6 | `vf-validate` sandboxes | Default mode (no `--only-*`) runs gold and noop **in separate fresh runtimes**, so 2 sandboxes per task. (`building-environments.md` says "single sandbox"; `debugging.md` and the code say separate.) | Budget 2 sandboxes per candidate for full validation. 500 candidates means about 1000 sandbox boots, likely above the $0.2-0.5 estimate. Pilot first. |
| 7 | `validate()` runs after `setup()` | `vf-validate` calls `Task.setup` before `validate`. | Drop the `await self.setup(runtime)` call inside `validate()` in the CLAUDE.md sketch (redundant). |
| 8 | Hook signatures | Base is `setup(self, trace, runtime)`, but hooks are invoked by parameter name (`utils/decorators.invoke`), so `setup(self, runtime)` is valid. | Sketch signatures OK. |
| 9 | Finalize timeout | Sketch grades in `finalize` but sets no `TaskTimeout.finalize`; `scoring=120` doesn't cover it. | Add `finalize=` to `TaskTimeout`. |
| 10 | Grader deps offline | `prepare_uv_script` in `setup` caches the interpreter on the backend; `run_uv_script` reuses it with no network. Fine for shared scoring under `allow=[]`. HumanEval/LCB instead open `scoring.network` to pypi/astral. | Keep the prepare-in-setup design. If switching to isolated, `setup` re-runs in the grading sandbox, so it still works. |
| 11 | Metrics before rewards | `Task.score` runs all `@vf.metric`, then all `@vf.reward`. A reward returning a Mapping records several *summed* rewards. | Grading once in `finalize` and reading `trace.info` in both is the right shape. |
| 12 | Hidden tests in traces | `TaskData` (incl. `tests`, `reference`, `mutants`) is serialized onto `trace.task.data` in `traces.jsonl`, and `dataset.jsonl` ships in the wheel. Hidden from the agent, but **public once pushed**. | State in README/REPORT limitations (same as HumanEval). Keep traces opt-out. |
| 13 | CLI scripts | Only `vf-run`, `vf-validate`, `vf-debug` exist. No `vf-gepa`. | n/a |
| 14 | Network policy in validate | `vf-validate` never applies the execution-time egress policy (shared mode), so the no-network property is only exercised by a real `vf-run`. | Test no-egress in the anti-hack suite through `vf-run`. |
| 15 | Prime tunnel on Windows | With the prime runtime, the laptop's interception server is exposed to the sandbox via `prime_tunnel` (frpc). Nothing in v1 handles Windows specifically. | Unverified on Windows. The first `vf-run -n 1 -r 1` is the real test. |
| 16 | Heavy deps | Lockfile pulls `transformers` + `tokenizers` (via `renderers[multimodal]`) but **no torch**. `uvloop` is correctly excluded on win32. | Acceptable; note the disk usage. |
| 17 | Sandbox lifetime | `PrimeConfig.idle_timeout = 3600`s with no hard timeout. A stray sandbox lives up to 1h idle. | Still run `prime sandbox list` after every paid step. |

### Model catalog (public `GET /api/v1/models`, 2026-11-16)
All five CLAUDE.md model IDs exist, and their prices match the table exactly:
`deepseek/deepseek-v4.1-flash-1017` (hosted, 1M ctx, max out 131K), `poolside/laguna-s-2.1` (gateway, no specs listed), `qwen/qwen3.6-35b-a3b` (fp8, 262K), `google/gemma-4-31b-it` (fp4, 262K, **max out 16K**), `openai/gpt-oss-120b` (fp4, 131K).

### Reference patterns worth copying
- `prime-envs/environments/code/humaneval`: flat package layout (`packages = ["humaneval"]`), grader read via `Path(__file__).parent`, grades inside `@vf.reward(runtime)`, runs candidate in a spawned worker that never sees tests.
- `prime-envs/environments/code/livecodebench`: last-fenced-block extraction across *all* assistant messages (`extract_code`), records `pass_rate` metric + `trace.info` report, `timeout_per_test` on a `TaskConfig` subclass. Also the loader for calibration slices (`livecodebench/code_generation_lite`, release files v1-v6, official date window 8/1/2024-5/1/2025).
- `verifiers.v1.parse_pytest_outcomes(output)`: parses `pytest -rA` summary lines into `{node_id: outcome}` for the grader.
