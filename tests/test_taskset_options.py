"""Unit tests for the taskset options and the harness guard. No sandbox, no model call.

Linux only: verifiers' runtimes do not import on native Windows (`fcntl`).
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="verifiers needs Linux")

if sys.platform != "win32":
    import verifiers.v1 as vf

    from pycode_env.taskset import (
        SOLUTION_PATH,
        SOLVER_MARKER,
        PyCodeAnyTask,
        PyCodeConfig,
        PyCodeEnv,
        PyCodeTaskset,
    )

ROOT = Path(__file__).resolve().parents[1]
ROWS = [
    json.loads(line)
    for line in (ROOT / "environments/pycode/pycode_env/data/dataset.jsonl").read_text().splitlines()
    if line.strip()
]
TRAIN_ID = next(r["id"] for r in ROWS if r["split"] == "train")
TEST_ID = next(r["id"] for r in ROWS if r["split"] == "test")


def load(**config) -> list:
    return list(PyCodeTaskset(PyCodeConfig(**config)).load())


# --- taskset.ids -------------------------------------------------------------------------

def test_no_ids_loads_the_whole_split_as_before():
    assert len(load()) == sum(r["split"] == "test" for r in ROWS)
    assert len(load(split="all")) == len(ROWS)


def test_ids_select_exactly_those_tasks():
    tasks = load(split="all", ids=[TEST_ID, TRAIN_ID])
    assert sorted(t.data.id for t in tasks) == sorted([TEST_ID, TRAIN_ID])


def test_unknown_id_raises_instead_of_running_fewer_tasks():
    with pytest.raises(ValueError, match="pc-does-not-exist"):
        load(split="all", ids=[TEST_ID, "pc-does-not-exist"])


def test_id_outside_the_chosen_split_raises():
    with pytest.raises(ValueError, match=TRAIN_ID):
        load(split="test", ids=[TRAIN_ID])


def test_harness_study_selection_loads_in_file_mode():
    sel = json.loads((ROOT / "data/reports/harness/selection.json").read_text())["tasks"]
    tasks = load(split="all", ids=sel, solution="file")
    assert sorted(t.data.id for t in tasks) == sorted(sel)
    assert all(type(t) is PyCodeAnyTask and t.data.solution == "file" for t in tasks)
    assert all(t.data.scoring.mode == "isolated" for t in tasks)


# --- hosted runs rebuild tasks from their data ------------------------------------------

def rebuild_like_hosted(task, config: "PyCodeConfig"):
    """What prime-rl's env server does (`EnvServer._build_task`): validate the dumped data
    into the declared data type and wrap it in the taskset's declared task class."""
    task_cls = PyCodeTaskset.task_type()
    data = task_cls.data_type().model_validate(task.data.model_dump())
    return task_cls(data, config.task)


@pytest.mark.parametrize("solution", ["reply", "file"])
def test_mode_survives_the_hosted_rebuild(solution):
    config = PyCodeConfig(split="all", ids=[TEST_ID], solution=solution)
    (task,) = PyCodeTaskset(config).load()
    rebuilt = rebuild_like_hosted(task, config)
    assert type(rebuilt) is PyCodeAnyTask
    assert rebuilt.data.solution == solution
    assert rebuilt.data.scoring.mode == ("isolated" if solution == "file" else task.data.scoring.mode)
    assert rebuilt.data.prompt == task.data.prompt
    if solution == "file":  # the hosted smoke test of 0.2.2 failed exactly here
        assert run_env(rebuilt, "bash") == [rebuilt]


class FakeRuntime:
    """Just enough of vf.Runtime for the file-mode hooks: an in-memory file system."""

    def __init__(self, files: dict[str, bytes] | None = None):
        self.files = dict(files or {})

    async def write(self, path, data):
        self.files[path] = data

    async def read(self, path, max_bytes=None):
        return self.files[path]

    async def run(self, argv, env):
        script = argv[2] if argv[:2] == ["sh", "-c"] else ""
        out = ""
        if "stat -c" in script:
            out = str(len(self.files[argv[3]])) if argv[3] in self.files else "missing"
        elif "test -e" in script:
            out = "shared" if SOLVER_MARKER in self.files else "fresh"
        elif argv[:2] == ["rm", "-rf"]:
            self.files.pop(argv[2], None)
        return SimpleNamespace(exit_code=0, stdout=out, stderr="")


def task_with_fake_grader(solution: str):
    config = PyCodeConfig(split="all", ids=[TEST_ID], solution=solution)
    (task,) = PyCodeTaskset(config).load()
    task = rebuild_like_hosted(task, config)
    graded: list[str] = []

    async def fake_grade(runtime, code):
        graded.append(code)
        return {"score": 1.0, "passed": 3, "total": 3}

    task._grade = fake_grade  # the real grader needs a sandbox; this checks the routing only
    return task, graded


REPLY = "Here it is:\n```python\ndef f():\n    return 1\n```"


def test_reply_mode_grades_the_reply_in_finalize():
    task, graded = task_with_fake_grader("reply")
    trace = SimpleNamespace(last_reply=REPLY, info={})
    asyncio.run(task.finalize(trace, FakeRuntime()))
    assert graded == ["def f():\n    return 1"]
    assert asyncio.run(task.grading_details(trace, FakeRuntime()))["frac_tests_passed"] == 1.0


def test_file_mode_grades_only_the_file_and_only_in_a_fresh_sandbox():
    task, graded = task_with_fake_grader("file")
    trace = SimpleNamespace(last_reply=REPLY, info={})
    solver = FakeRuntime({SOLUTION_PATH: b"def f():\n    return 2\n"})
    asyncio.run(task.finalize(trace, solver))
    assert graded == []  # nothing is graded in the agent's sandbox
    assert SOLVER_MARKER in solver.files and trace.info["solution_source"] == "file"

    with pytest.raises(RuntimeError, match="fresh sandbox"):  # grading in the solver box is refused
        asyncio.run(task.grading_details(trace, solver))

    fresh = FakeRuntime({SOLUTION_PATH: solver.files[SOLUTION_PATH]})  # what isolated scoring restores
    asyncio.run(task.grading_details(trace, fresh))
    assert graded == ["def f():\n    return 2\n"] and trace.info["graded_in_fresh_sandbox"]


# --- harness guard in PyCodeEnv.run ------------------------------------------------------

class FakeAgent:
    """Stands in for `agents.agent`: the same `harness.config.id` path, and records runs."""

    def __init__(self, harness_id: str):
        self.harness = SimpleNamespace(config=SimpleNamespace(id=harness_id))
        self.ran: list = []

    async def run(self, task):
        self.ran.append(task)


def run_env(task, harness_id: str) -> list:
    agent = FakeAgent(harness_id)
    env = object.__new__(PyCodeEnv)  # run() reads no env state
    asyncio.run(env.run(task, SimpleNamespace(agent=agent)))
    return agent.ran


def test_guard_allows_no_tools_reply_mode():
    (task,) = load(split="all", ids=[TEST_ID])
    assert task.data.solution == "reply"
    assert run_env(task, "null") == [task]


def test_guard_allows_tool_harness_in_file_mode():
    (task,) = load(split="all", ids=[TEST_ID], solution="file")
    assert run_env(task, "bash") == [task]


def test_guard_refuses_tool_harness_in_reply_mode_before_the_agent_runs():
    (task,) = load(split="all", ids=[TEST_ID])
    agent = FakeAgent("bash")
    env = object.__new__(PyCodeEnv)
    with pytest.raises(ValueError, match="solution file"):
        asyncio.run(env.run(task, SimpleNamespace(agent=agent)))
    assert agent.ran == []  # refused before any sandbox or model call


def test_real_agent_exposes_the_harness_id_the_guard_reads():
    # Guards against the attribute path changing in a verifiers upgrade.
    for harness_id in ("null", "bash"):
        agent = vf.Agent(vf.AgentConfig(harness={"id": harness_id}, model="test/model"))
        assert agent.harness.config.id == harness_id
