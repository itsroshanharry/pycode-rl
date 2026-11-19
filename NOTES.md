# NOTES.md: decision log

Running log of doc ambiguities resolved, design decisions, and cost. Newest first.

---

## CURRENT STATUS (read this first in a new session), updated 2026-11-18

**Where we are:** Phase 1 done; plan step 3 done; plan step 4 (generation) in progress.
- **Environment** `pycode-env` (single-function tasks, `null` harness default, shared scoring, isolated grader): built, cheat suite 26/26, 10 hand-written tasks valid in Prime sandboxes.
- **Published:** PRIVATE as `itsroshanharry/pycode-env` 0.1.0 (ships the 10 hand-written tasks, split `train`). Hosted smoke run passed 2/2.
- **Generation:**
  - 102 seeds (`pipeline/prompts/seeds.jsonl`) and prompt `generate_v1.md`.
  - **Batch b01:** 10 Claude-written candidates, all passing assembly, local check (30/30 authored mutants killed) and `vf-validate` (10/10).
  - Test-strength check (`02b`) on b01: mutation 0.949 mean, all 17 survivors equivalent, branch coverage 100%, hard-code fake fails on all 10, 0 flagged.
  - **Batch b02** (c0011-c0020, prompt v1): all gates passed, `vf-validate` 20/20. The automatic mutants exposed 3 real test gaps (c0012, c0019), which are fixed.
  - **Grader fixed** (UnicodeDecodeError false negative). The Hub package 0.1.0 is outdated, so re-push before the next hosted run.
  - **Prompt `generate_v2.md`** (difficulty levers twist/combo/efficiency/spec-trap) is ready; **b03 onward use v2.**
- **Wallet:** about $9.98 (about $0.02 spent). The user has not set a dashboard usage limit yet.

**Agreed decisions (don't relitigate):**
- function-level tasks (no repo pivot);
- generator split: Claude writes the first ~50, then a cheap Prime model, in a separate removable `01b_generate_api.py`;
- contamination = exact n-gram + LLM-judge rephrase check (no MinHash);
- traces ON;
- hosted evals for the leaderboard;
- SWE-env reward-hack audit is out of scope (separate later project).

**Next steps, in order:**
1. ~~Review the 02b results on b01~~ done: 0 flagged.
2. ~~Re-push the Hub package~~ **done:** `itsroshanharry/pycode-env` **0.1.1** (PRIVATE, wheel sha256 `8ea95510...`). Hosted smoke run `tajnohon1b6p3cf6hhmksirk`: 2/2 reward 1.0, 0% error/truncation; the trace shows `grader: "2"`, `isolated: true`, `temperature: 0.0`. Wallet $9.98.
3. **Keep writing Claude batches b04, b05, ...** (user decision 2026-11-19: as many as possible). Each batch: 10 tasks with **generate_v2**, new seeds; hard efficiency tasks get `slow.py`; commit after every few tasks; then assemble -> 02a -> 02b (inspect survivors) -> vf-validate. **b01-b03 done: 30 candidates, all valid.** Seeds used so far: s001, s003, s005, s011, s012, s016, s019, s020, s021, s025, s026, s031, s033, s035, s040, s041, s043, s051, s052, s055, s056, s066, s071, s078, s081, s082, s088, s092, s093, s094.
4. Write `01b_generate_api.py` (cheap model not on the leaderboard, same template) for about 450 more candidates; run the same gates. Report pass rates per generator.
5. Pilot (20 tasks x 4 rollouts) to measure $/rollout and truncation.
6. Difficulty filter (-r 8, temperature 1.0, keep 1/8..7/8; 0/8 -> one stronger-model try, then manual). Ask first (> $1).
7. Contamination (`04_contamination.py`), split (`05`), audit 40 tasks (`06`), freeze the dataset hash, push, leaderboard, REPORT.md.

**How to run things:** see CLAUDE.md section 3 (Codespace workflow), section 7 (gate order) and section 9 (hosted command).

**User preferences:** plain language, technical terms explained in brackets, concise answers. Ask before spending more than $1 or doing anything outward-facing.

---

## 2026-11-18: Batch b03 (first generate_v2 batch) + grader v2 codec

- **b03** (c0021-c0030; seeds s001, s016, s020, s082, s043, s051, s056, s012, s025, s094): 1 easy / 6 medium / 3 hard. Levers recorded per task; c0026 `assign_rooms` and c0027 `rate_limit` use **efficiency** with `slow.py`.
  - Assembled 30/30; **local check 30/30**, including both `slow.py` files failing by timeout (2 timeouts each).
  - Authoring errors caught by re-derivation before any run: c0021 (2 week labels), c0022 (2 orderings). That makes 5 hand-computed expected values wrong so far out of several hundred, all caught. This argues for always pairing literal cases with an independent oracle.
- **Efficiency calibration finding:** the first measurement put c0026 at 3.18 s for its whole test file. The cost was mostly the grader codec: every int was a tagged pair `["i","123"]`, so 30k tuples were about 1.5 MB.
  - **Grader v2 codec** (`GRADER_VERSION = "2"`): None/bool/int/str travel as native JSON. Tags stay for float/bytes/list/tuple/set/frozenset/dict. Raw JSON floats and any malformed shape are rejected; exact-type checks still reject subclasses.
  - Round-trip test over all types passed; **cheat suite 27/27 as root**; local check 30/30.
- **Per-call timings** (Codespace, 2 cores; single call including the process boundary and codec):

  | Task | Reference | `slow.py` |
  |---|---|---|
  | c0026 (30k meetings) | **0.114 s** | **42.5 s** |
  | c0027 (30k requests) | **0.078 s** | **38.9 s** |

  The reference is under the 0.3 s target. `slow.py` is about 8x the 5 s limit on the faster machine, so more on the 1-vCPU sandbox. Note: the whole-file time (`reference_seconds`) includes the trusted test side's own input generation and checking, which doesn't count toward the candidate's call limit.
- **Hub package is outdated** (old grader v1, no UnicodeDecodeError fix): re-push before the next hosted run.
- **Gates on all 30 candidates:** `vf-validate` **30/30 valid** in real 1-vCPU Prime sandboxes (the 30k-element tests pass there); 0 stray sandboxes.
- **`02b` on b03:**
  - mean 0.952;
  - 1 flagged: c0022 natural_sort at 0.643 (9/14). **All 5 survivors are equivalent** (sort-tag constants 0/1 -> -1/2, and `run[-1]` vs `run[0]` on runs that are all digits or all non-digits). **Flag overridden after manual review**; the low score is an artifact of a small mutant count dominated by tag constants.
  - **2 real gaps found and closed:**
    1. c0023 `startswith('[') or endswith(']')` accepted the unclosed `"[abc"`;
    2. c0029 an invalid prefix line was ignored when the counts still matched.

    Both are now at 1.0 (31/31, 40/40).
  - Other survivors (c0024 x4, c0026 x2) are equivalent init values.
- **02b `--ids`** reruns only selected tasks and merges into the existing report (a full run on 30 tasks takes about 15 min).
- **Running total of real test gaps found by auto-mutants: 5** (b02: 3, b03: 2) that the authored mutants missed. Equivalent survivors are about 70% of all survivors.

---

## 2026-11-18: Prompt generate_v2 (difficulty levers)

- **Motivation (user):** company DSA interviews use questions that are hard to answer with AI or recall. Adopt their *principles*, not the questions: real interview questions get posted to LeetCode/GfG and are contaminated.
- **v2 levers:** twist / combo / efficiency / spec-trap (see CLAUDE.md Stage 1). Medium tasks use 1 or more, hard tasks 2 or more, recorded in `meta.levers`. If a task resembles a known problem, the twist must change the answer for tested inputs.
- **Efficiency lever closes a real gap:** b01/b02 tests check correctness mostly on small inputs, so an O(n^3) brute force would usually pass. v2 hard tasks ship `slow.py` (correct but naive). `02a` requires it to score 0 **by timing out** (`timeouts > 0`, not by being wrong) and records `reference_seconds`. `taskfiles.build_row` reads the optional `slow.py` into the row's `slow_reference` and errors if `levers` contains "efficiency" without it. Builder output for existing tasks is unchanged (candidates sha `c4408cda...`).
- **Design note:** wall-clock-based rejection is acceptable only with a large margin (reference well under 1 s vs naive above 200 s), so machine speed can't flip the result. This is consistent with the "no flaky timing assertions" rule: the test asserts outputs; the grader's time limit does the rejecting.

---

## 2026-11-18: Grader false-negative fix + batch b02

- **Grader bug found while authoring c0014 (query parsing), a false negative (correct code scored 0):**
  - The worker sends the candidate's exception as (nearest builtin class name, message), and the trusted side rebuilt it with `cls(message)`.
  - `UnicodeDecodeError` needs 5 constructor args, so the rebuild failed and it became a generic `CandidateError`.
  - A *correct* solution raising `UnicodeDecodeError` (e.g. via `bytes.decode`) would therefore fail `pytest.raises(ValueError)`.
  - **Fix:** walk the MRO to the nearest builtin ancestor constructible from a message (`UnicodeError`, still a `ValueError`).
  - **Regression test** `test_unicode_decode_error_matches_value_error` added. Grader suite now **27/27 as root**.
  - **The published Hub package (0.1.0) still has the old grader**, so re-push before the next hosted run.
- **Batch b02** (`tasks/generated/b02_claude/`, c0011-c0020; seeds s005, s026, s033, s021, s088, s078, s092, s041, s035, s052): difficulty 3 easy / 5 medium / 2 hard (labels honest rather than forced to 3/4/3; the difficulty filter measures real difficulty).
  - Skipped seeds that are famous puzzles (Roman numerals = LeetCode 13, text justification = LeetCode 68, rectangle union area = LeetCode 850).
  - Funnel: assembled 10/10; local check 10/10 (30/30 authored mutants killed). On all 20 candidates: `02b` mean mutation 0.950, 0 flagged (c0019 line coverage 0.977, branch 0.975; the uncovered line is the unreachable unknown-schema-type error); **`vf-validate` 20/20 valid**, 0 stray sandboxes.
  - **The automatic mutants found 3 real test gaps that my 3 authored mutants missed**. The other 14 b02 survivors were inspected and are equivalent (e.g. checksum `data[i-1]` instead of `data[i+1]` sums the same set of low bytes; round-robin over-long slice only beyond index n-1).
    1. c0012: deleting the "stray `$`" raise is undetected; `"$ab}"` would substitute `b`.
    2. c0012: breaking the unclosed-`${` check is undetected; `"${ab"` loops forever (tests only had a 1-char name).
    3. c0019: a list schema without `"items"` was untested; mutant `or 'items' in schema` crashes there.
  - **Fix:** tests added (`"$ab}"`, `"x$ya}z"`, `"${ab"`, `"x ${abc"`, `"${a:-x"`; list schemas without items). 02a still 20/20; 02b rerun to confirm.
  - **Process lesson for REPORT:** the authored mutants are a necessary gate, but the automatic ones are what make the "tests are strong" claim author-independent. Inspect surviving auto-mutants per task: survivors are either equivalent (fine) or a real gap (strengthen the tests).

---

## 2026-11-18: Generation pipeline + batch b01 (10 Claude-written candidates)

- `pipeline/prompts/seeds.jsonl` (written by `make_seeds.py`): **102 seeds across 11 categories** of real-world rules. No classic benchmark puzzles.
- `pipeline/prompts/generate_v1.md`: the versioned generation prompt, used verbatim by any generator.
- `pipeline/taskfiles.py`: shared task-folder -> row logic. Refactoring `00_build_handwritten.py` onto it reproduced the identical hash `ecb878e9...`.
- `01_assemble_candidates.py`: folders -> `data/candidates.jsonl`; format failures are rejected and reported, never fixed.
- `02a_local_check.py`: free grader pre-check, run in the Codespace as root.
- `taskset.dataset_path`: lets `vf-validate`/`vf-run` load a candidate file.
- **Batch b01** (`tasks/generated/b01_claude/`, generator `claude-code (claude-opus-5-5)`, prompt `generate_v1`): 10 seeds, 10 categories, difficulty 3 easy / 4 medium / 3 hard. 15-36 hidden tests each; 9/10 include a differential test against an independent oracle (for CIDR, `ipaddress.collapse_addresses`).
  - Funnel: assembled 10/10 (0 format rejects); local check 10/10 (reference passes, **30/30 mutants killed**); `vf-validate` in Prime sandboxes (gold+noop) **10/10 valid**, 0 stray sandboxes. Candidates sha256 `35b678cc0737...`.
  - Authoring note (honest): one hand-computed expected value in c0006 was wrong (13 vs 12) and was caught by re-derivation before any check ran. This is the class of error the reference-vs-literal check exists to catch.
  - **Test strength (`02b_test_strength.py`, author-independent; report `data/reports/test_strength.json`):**
    - automatic AST mutation score **mean 0.949** (range 0.829-1.0; 20-40 mutants per task);
    - **line and branch coverage 100% on all 10**;
    - the hard-coded-doctest fake **fails on all 10**;
    - **0/10 flagged.**
  - **All 17 surviving auto-mutants were inspected by hand and every one is equivalent**, so the tests kill every behaviour-changing mutant. Examples: semver internal sort tags `0/1 -> -1/2` keep the order; `>=` -> `>` on a list index still raises IndexError one step later; token-bucket `last = -1` is a no-op because the bucket starts full; CIDR `prefix > 33` still ends in ValueError via a negative shift.
  - **Lesson:** the raw mutation score understates strength by about 5 points on tasks with tag constants or redundant guards. Report it with "equivalent mutants manually verified" for a sample, not as a hard 1.0 target.

---

## 2026-11-18: Published (PRIVATE) + hosted smoke test PASSED

- **Flat layout required:** `prime env push` only detects `*.py` or `<subdir>/__init__.py` directly under the env dir (`commands/env.py:916-932`), so the `uv init --lib` **src/ layout fails** with "No environment Python file found". Moved to `environments/pycode/pycode_env/` (the prime-envs convention). Dataset hash unchanged (`ecb878e9...`). (Possible docs/CLI PR candidate.)
- Pushed `itsroshanharry/pycode-env` 0.1.0, **PRIVATE**, `--runtime v1`, wheel sha256 `f9592b92...`. Private envs can't be pip/uv-installed directly, only via `prime env pull`. `.prime/.env-metadata.json` (env id/owner/version, no secrets) is committed.
- **Hosted run 1 FAILED** (`ohm1si53...`): a TOML `taskset = {split = "train"}` becomes `env_args = {"config": {"taskset": ...}}`. The runner's prime-rl (`3bd59c1`, `src/prime_rl/entrypoints/eval.py` + `configs/orchestrator.py`) puts env_args directly into `source[0].env`, a **`vf.EnvConfig`**, which rejects `config` ("Extra inputs are not permitted").
- **Correct shape:** `-a '{"taskset": {"split": "train"}}'` on the CLI. This corrects H4: hosted runs *can* set any `vf.EnvConfig` field through `-a`, e.g. `{"agent": {...}}` and `{"taskset": {...}}`. Don't use the CLI's TOML `taskset`/`harness` sections with this runner.
- **Hosted run 2 PASSED** (`b3hl8md098kmqisdv67c7cay`), command: `prime eval run itsroshanharry/pycode-env --hosted -m deepseek/deepseek-v4.1-flash-1017 -n 2 -r 1 -c 2 -a '{"taskset": {"split": "train"}}' -S '{"reasoning_effort": "low", "max_tokens": 2048}' --timeout-minutes 120`.
  - 2/2 reward 1.0, 0% error/truncation/timeout.
  - `harness=null` (the package-default Env is honored on hosted), and the egress policy was applied.
- **Results live in Prime Traces**, not `prime eval samples` (empty for v1). `prime traces list --run-id <eval id> --output json` gives per-rollout reward, our metrics (`frac_tests_passed`, `no_code`, `load_error`, `call_timeouts`), `is_truncated`, `has_error`, `total_tokens`, `duration_ms`. About 15 KB per trace, so ingestion cost is negligible.
- **Sampling verified in the raw trace** (`prime traces get <id> --raw`): `reasoning_effort: "low"` and `max_tokens: 2048` reached the request (777 reasoning / 1142 completion tokens). **`temperature: null`**, so leaderboard and filter runs must pass `temperature` explicitly in `-S`.
- Wallet: 9.9815, so about $0.018 spent cumulatively (sandbox rows now posting).

---

## 2026-11-18: Direction decision: stay function-level (no repo pivot)

- An external review proposed pivoting to SWE-bench-style repo bug-injection. **Decision (user, 2026-11-18): keep `pycode-env` (single-function tasks) and finish it.**
- Reasons:
  - Prime already hosts about 19 SWE envs (`prime-envs/environments/swe/`), incl. `swesmith_env` (SWE-smith: 88k injected-bug tasks, about 51k Python), `r2e_gym`, `swebench_verified`/`pro`. A 50-task injected-bug set would be a small duplicate.
  - Repo rollouts cost about $0.01-0.06 each (multi-turn, no cache discount on laguna/gpt-oss, minutes of sandbox time), versus about $0.001-0.002 here.
  - The methodology (validation funnel, reward-hack hardening + control experiment, decontamination, audit, CIs) is the portfolio signal.
- Adopted from the review:
  - seed-grounded generation (`meta.seed`);
  - pass@k + **pass^k** reporting;
  - failure-mode breakdown chart;
  - 0/8 tasks get one stronger-model rollout before manual inspection;
  - the filter model may appear on the leaderboard as a disclosed baseline row;
  - the contamination judge also asks an open "is this a known LeetCode/Codeforces problem?" question.
  CLAUDE.md sections 7 and 9 are updated.
- Rejected or corrected from the review:
  - it described the v0 API (`SandboxEnv`, `load_environment`, `Rubric`, `vf-eval`);
  - it claimed "50 tasks make 10-point gaps credible" (CIs are about +/-13 points; use paired comparisons);
  - its leaderboard estimate (about $2 for 800 multi-turn rollouts) was optimistic.
- **Out of scope (separate, later project):** a reward-hack audit of Prime's existing SWE envs. Lead: `swesmith_env/taskset.py:206` notes agent edits to test files are kept as-is at scoring.

---

## 2026-11-16: Contamination plan revised (Stage 4)

- **Change:** drop MinHash-LSH and use exact all-pairs n-gram overlap (5-gram Jaccard + longest common token run) plus an **LLM-judge rephrase check** on the top-k nearest benchmark problems. CLAUDE.md Stage 4, section 3 and the layout comment are updated.
- **Why:**
  - MinHash is an *approximation* of Jaccard used for near-duplicate removal at web-corpus scale. Our scale (about 500 tasks x a few thousand benchmark problems) allows exact comparison in seconds.
  - Lab-standard benchmark decontamination is exact n-gram overlap (GPT-3: 13-gram; GPT-4: 50-char substring).
  - n-gram checks miss paraphrases. LMSYS (arXiv 2311.04850) found 8-18% rephrased HumanEval overlap in RedPajama/StarCoder-Data, and showed a model trained on rephrased test data passes n-gram decontamination. Their fix is embedding shortlist + LLM judge. Our tasks are LLM-written, so paraphrase leakage is the realistic risk.
  - We can't run embedding models locally (no heavy ML deps), so the n-gram scores provide the shortlist.
- Judge model: a cheap catalog model, ideally not one on the leaderboard. Estimate < $0.10 for about 500 tasks x top-3 candidates.
- Wallet check (2026-11-16): balance **$9.9987**. Listed billing rows total $0.0164 (sandboxes $0.0151, inference $0.0013), and only the inference amount has been deducted so far, so treat about $9.98 as available.

---

## 2026-11-16: Phase 1 built and verified (spend so far: about $0.002)

**Grader design** (`environments/pycode/pycode_env/grader/run_pytest.py`, docstring has the threat model):
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
