"""PyCode: implement a Python function from a spec; graded by a hidden pytest suite.

Design (see NOTES.md for the reasoning):
- Single turn, `null` harness by default (no tools), shared scoring. The model never
  sees the sandbox; its reply is the only input to grading.
- Hidden tests/reference/mutants are extra `TaskData` fields: kept on the evaluator,
  never put in the prompt, written into the sandbox only at grading time, and deleted
  by the grader as soon as it has read them.
- Grading runs `grader/run_pytest.py` (PEP 723, deps pre-installed during `setup`,
  before the no-egress network policy applies). It isolates the candidate in an
  unprivileged worker process; see that file's docstring for the threat model.
- Grade once in `finalize` and store it on `trace.info`; the reward and metrics read it.
- Infrastructure failures raise (never a silent 0.0), so they show up as errors rather
  than as model failures.
- Tool-using variant (`--env.taskset.solution file` with `--env.agent.harness.id bash`):
  `PyCodeFileTask` (a subclass; the default `PyCodeTask` is unchanged). The agent writes
  /work/solution.py and may run it. Grading uses isolated scoring: a fresh sandbox receives
  only that file, and the grade is computed in the scoring phase (network locked). A marker
  file proves the grading sandbox is not the agent's. Never combine a shell-equipped harness
  with the default `reply` mode, which grades in the agent's sandbox: `PyCodeEnv.run`
  refuses that combination.
- `taskset.ids` selects a fixed subset of tasks (hosted runs have no `--select` flag).
"""

from __future__ import annotations

import json
import re
import uuid
from collections.abc import Iterator
from importlib.resources import files

import verifiers.v1 as vf

GRADER = files("pycode_env").joinpath("grader/run_pytest.py").read_bytes()
WORKDIR = "/work"
GRADE_DIR = "/tmp/pycode-grade"
# Validation gate: the reference must pass every test and at least MIN_KILLED of the
# mutants must fail (LLM mutants are sometimes equivalent code, so not all of them).
MIN_MUTANTS = 3
MIN_KILLED = 2

INSTRUCTION = (
    "Implement the Python function specified below. Use Python 3.11 and only the "
    "standard library. Reply with the complete implementation in one ```python code block."
)
# `solution = "file"` (for tool-using harnesses such as `bash`): the agent writes the module
# itself and may run it; only the file's final bytes are graded, in a fresh sandbox.
INSTRUCTION_FILE = (
    "Implement the Python function specified below and save the complete module to "
    "/work/solution.py. Use Python 3.11 and only the standard library. You can run commands "
    "in the sandbox to test your code (there is no network access). Only the final contents "
    "of /work/solution.py are graded, by hidden tests."
)
SOLUTION_PATH = f"{WORKDIR}/solution.py"
MAX_SOLUTION_BYTES = 1_000_000
SOLVER_MARKER = "/tmp/pycode-solver-sandbox"  # written in the solver; must not exist where we grade

_FENCE = re.compile(r"```[^\n`]*\n(.*?)```", re.DOTALL)
_THINK = re.compile(r"<think>.*?</think>", re.DOTALL)


def extract_code(reply: str | None) -> str:
    """The last fenced code block (any language tag), else the whole reply.
    Reasoning wrapped in <think> tags is removed first."""
    text = _THINK.sub("", reply or "")
    blocks = _FENCE.findall(text)
    return (blocks[-1] if blocks else text).strip()


class PyCodeData(vf.TaskData):
    entry_point: str
    tests: str
    """Hidden pytest source. Never part of the prompt."""
    reference: str
    mutants: list[str] = []
    meta: dict = {}


class PyCodeTaskConfig(vf.TaskConfig):
    call_timeout: float = 5.0
    """Wall-clock limit for one call into the candidate, in seconds."""
    total_timeout: float = 60.0
    """Wall-clock limit for all calls into one candidate, in seconds."""


class PyCodeTask(vf.Task[PyCodeData, vf.State, PyCodeTaskConfig]):
    NEEDS_CONTAINER = True

    async def setup(self, runtime: vf.Runtime) -> None:
        res = await runtime.run(["mkdir", "-p", WORKDIR], {})
        if res.exit_code:
            raise RuntimeError(f"mkdir {WORKDIR} failed: {res.stderr[-500:]}")
        # Installs pytest for the grader now, while the sandbox still has network.
        await runtime.prepare_uv_script(GRADER)

    async def _grade(self, runtime: vf.Runtime, code: str) -> dict:
        base = f"{GRADE_DIR}/{uuid.uuid4().hex}"
        await runtime.write(f"{base}/solution.py", code.encode())
        await runtime.write(f"{base}/tests.py", self.data.tests.encode())
        res = await runtime.run_uv_script(
            GRADER,
            args=[
                f"{base}/solution.py",
                f"{base}/tests.py",
                "--call-timeout", str(self.config.call_timeout),
                "--total-timeout", str(self.config.total_timeout),
            ],
        )
        if res.exit_code != 0:
            raise RuntimeError(f"grader failed (exit {res.exit_code}): {res.stderr[-2000:]}")
        grade = json.loads(res.stdout.strip().splitlines()[-1])
        if grade.get("isolated") is False:
            # The candidate ran with the grader's privileges and could have read the
            # hidden tests: refuse to report a score rather than trust it.
            raise RuntimeError("grader could not drop privileges for the candidate")
        return grade

    async def finalize(self, trace: vf.Trace, runtime: vf.Runtime) -> None:
        code = extract_code(trace.last_reply)
        if not code:
            trace.info["grade"] = {"score": 0.0, "passed": 0, "total": 0, "no_code": True}
            return
        trace.info["grade"] = await self._grade(runtime, code)

    @vf.reward(weight=1.0)
    async def passed_all_tests(self, trace: vf.Trace) -> float:
        return float(trace.info["grade"]["score"])

    @vf.metric
    async def grading_details(self, trace: vf.Trace) -> dict[str, float]:
        g = trace.info["grade"]
        return {
            "frac_tests_passed": g["passed"] / g["total"] if g["total"] else 0.0,
            "no_code": float(bool(g.get("no_code"))),
            "load_error": float(bool(g.get("load_error"))),
            "call_timeouts": float(g.get("timeouts", 0)),
        }

    async def validate(self, runtime: vf.Runtime) -> bool:
        """Gold check for `vf-validate`: reference passes every test, and enough
        mutants fail. (`vf-validate` has already run `setup` on this runtime.)"""
        ref = await self._grade(runtime, self.data.reference)
        if ref["score"] != 1.0:
            return False
        mutants = self.data.mutants
        if len(mutants) < MIN_MUTANTS:
            return False
        killed = 0
        for m in mutants:
            killed += (await self._grade(runtime, m))["score"] == 0.0
        return killed >= MIN_KILLED


class PyCodeFileTask(PyCodeTask):
    """File mode, for tool-using harnesses. Only `finalize` and `grading_details` differ:
    setup, the grader call, the reward and `validate` are inherited unchanged."""

    async def finalize(self, trace: vf.Trace, runtime: vf.Runtime) -> None:
        """Runs in the SOLVER sandbox. The agent had a shell here (it could have edited pytest,
        planted sitecustomize.py or left a background process), so nothing is graded here.
        The solution is normalized to one regular file, the only artifact that crosses into
        the fresh grading sandbox."""
        await runtime.write(SOLVER_MARKER, b"1")
        res = await runtime.run(
            ["sh", "-c", 'if [ -f "$0" ] && [ ! -L "$0" ]; then stat -c %s "$0"; else echo missing; fi',
             SOLUTION_PATH], {})
        size = res.stdout.strip()
        code, source = "", "none"
        if size.isdigit() and int(size) > MAX_SOLUTION_BYTES:
            source = "oversized"  # graded as no code
        elif size.isdigit() and int(size) > 0:
            code = (await runtime.read(SOLUTION_PATH, MAX_SOLUTION_BYTES)).decode("utf-8", errors="replace")
            source = "file" if code.strip() else "none"
        if source == "none":
            # The model answered with a code block instead of writing the file: grade that block,
            # so the comparison measures the tools, not the delivery format. Recorded per attempt.
            blocks = _FENCE.findall(_THINK.sub("", trace.last_reply or ""))
            if blocks and blocks[-1].strip():
                code, source = blocks[-1].strip(), "reply_fallback"
        # a symlink, directory or oversized file is replaced by a plain file (or an empty one)
        await runtime.run(["rm", "-rf", SOLUTION_PATH], {})
        await runtime.write(SOLUTION_PATH, code.encode() if source != "oversized" else b"")
        trace.info["solution_source"] = source

    @vf.metric
    async def grading_details(self, trace: vf.Trace, runtime: vf.Runtime | None = None) -> dict[str, float]:
        """Runs in the GRADING sandbox (isolated scoring: fresh box, network locked, only
        /work/solution.py restored). This is the only metric and metrics run before rewards,
        so the grade is computed here exactly once; the inherited reward then reads it."""
        if runtime is None:
            raise RuntimeError("file mode grades in the scoring phase and needs its runtime")
        res = await runtime.run(["sh", "-c", f'test -e "{SOLVER_MARKER}" && echo shared || echo fresh'], {})
        if res.stdout.strip() != "fresh":
            # grading in the agent's own sandbox would let a shell-using agent tamper with it
            raise RuntimeError("file mode must be graded in a fresh sandbox (scoring mode 'isolated')")
        code = (await runtime.read(SOLUTION_PATH, MAX_SOLUTION_BYTES)).decode("utf-8", errors="replace")
        if not code.strip():
            trace.info["grade"] = {"score": 0.0, "passed": 0, "total": 0, "no_code": True}
        else:
            trace.info["grade"] = await self._grade(runtime, code)
        trace.info["graded_in_fresh_sandbox"] = True
        return await super().grading_details(trace)


class PyCodeConfig(vf.TasksetConfig):
    split: str = "test"
    """Which rows to load: "train", "test", or "all"."""
    dataset_path: str | None = None
    """Load rows from this JSONL file on the evaluator instead of the bundled dataset
    (used by the pipeline to validate and filter candidate tasks before release)."""
    solution: str = "reply"
    """"reply" (default, for the null harness): the answer is the reply's code block.
    "file" (for tool-using harnesses such as bash): the agent writes /work/solution.py, and
    grading switches to isolated scoring with that file as the only artifact."""
    ids: list[str] = []
    """Load only these task ids (empty = every task in `split`). Hosted runs have no task
    selection flag, so this is how they reproduce a fixed subset. Every id must exist in
    `split`; use split "all" to select from both splits."""
    task: PyCodeTaskConfig = PyCodeTaskConfig()


class PyCodeTaskset(vf.Taskset[PyCodeTask, PyCodeConfig]):
    def load(self) -> Iterator[PyCodeTask]:
        if self.config.dataset_path:
            with open(self.config.dataset_path, encoding="utf-8") as f:
                raw = f.read()
        else:
            raw = files("pycode_env").joinpath("data/dataset.jsonl").read_text(encoding="utf-8")
        wanted = set(self.config.ids)
        if wanted:
            # Fail loudly on a typo or a wrong split, instead of silently running fewer tasks.
            in_split = {
                r["id"] for r in map(json.loads, filter(str.strip, raw.splitlines()))
                if self.config.split in ("all", r["split"])
            }
            if missing := sorted(wanted - in_split):
                raise ValueError(
                    f"taskset.ids not found in split {self.config.split!r}: {missing} "
                    "(use split 'all' to select from both splits)"
                )
        for line in raw.splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if self.config.split not in ("all", r["split"]):
                continue
            if wanted and r["id"] not in wanted:
                continue
            if self.config.solution not in ("reply", "file"):
                raise ValueError(f"taskset.solution must be 'reply' or 'file', not {self.config.solution!r}")
            file_mode = self.config.solution == "file"
            task_cls = PyCodeFileTask if file_mode else PyCodeTask
            mode_fields = (
                {"artifacts": [vf.Artifact(source=SOLUTION_PATH)],
                 "scoring": vf.ScoringConfig(mode="isolated")} if file_mode else {}
            )
            yield task_cls(
                PyCodeData(
                    id=r["id"],
                    name=r["id"],
                    prompt=f"{INSTRUCTION_FILE if file_mode else INSTRUCTION}\n\n{r['prompt']}",
                    **mode_fields,
                    entry_point=r["entry_point"],
                    tests=r["tests"],
                    reference=r["reference"],
                    mutants=r.get("mutants", []),
                    meta=r.get("meta", {}),
                    image="python:3.11-slim",
                    workdir=WORKDIR,
                    resources=vf.TaskResources(cpu=1, memory=1, disk=5),
                    timeout=vf.TaskTimeout(setup=300, agent=600, finalize=180, scoring=60),
                    network=vf.NetworkPolicyConfig(allow=[]),  # no egress once the agent starts
                ),
                self.config.task,
            )


class PyCodeEnvConfig(vf.EnvConfig):
    # Default to the tool-less `null` harness: hosted evals cannot pin a harness, and a
    # shell-equipped harness would let the agent tamper with the shared grading sandbox.
    # (Override with --env.agent.harness.id bash only together with isolated scoring.)
    agent: vf.AgentConfig = vf.AgentConfig(harness={"id": "null"})


class PyCodeEnv(vf.Env[PyCodeEnvConfig]):
    async def run(self, task: vf.Task, agents: vf.Agents) -> None:
        # Reply mode grades in the agent's own sandbox (shared scoring). That is safe only
        # when the agent has no tools: with a shell it could plant files that fake a pass.
        # Refuse the combination before the model is called; Prime records the error on the
        # episode, so it can never be mistaken for a model score.
        harness_id = agents.agent.harness.config.id
        if harness_id != "null" and not isinstance(task, PyCodeFileTask):
            raise ValueError(
                f"harness {harness_id!r} gives the agent tools: add --env.taskset.solution file "
                "(hosted: -a '{\"taskset\": {\"solution\": \"file\"}}'), which grades the "
                "solution file in a fresh sandbox"
            )
        await agents.agent.run(task)


__all__ = ["PyCodeEnv", "PyCodeTaskset"]
