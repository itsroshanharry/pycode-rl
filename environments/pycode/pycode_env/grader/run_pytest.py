# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest==8.4.2"]
# ///
"""Grade one candidate solution against a hidden pytest file, inside the sandbox.

usage: run_pytest.py SOLUTION_PATH TESTS_PATH [--call-timeout S] [--total-timeout S] [--mem-mb N]

Prints exactly one JSON line on stdout:
    {"score": 0.0|1.0, "passed": n, "total": m, "failed": f, "errors": e,
     "load_error": str|null, "timeouts": t, "crashes": c, "isolated": bool,
     "first_failure": str|null, "grader": GRADER_VERSION}
Exit code 0 whenever a grade was computed (including score 0 for wrong, crashing or
cheating code). Nonzero ONLY when the grader itself or the hidden tests are broken
(collection error, no tests, internal pytest error) -- the task layer raises on that,
so infrastructure/task bugs are never recorded as model failures.

Threat model and design (why each piece exists):
- The candidate never runs inside the pytest process. Pytest and the trusted test file
  run here; the candidate runs in a separate *worker* process. A `solution` proxy
  module forwards each call (args/returns as plain data) over a pipe. So candidate code
  cannot monkeypatch pytest, rewrite reports, override `assert`, or print a fake result:
  the score is computed only from this process's own pytest hooks.
- Replies are JSON with a tagged encoding of exact builtin types only (no pickle, which
  would let a malicious worker execute code in this process). Objects with a rigged
  `__eq__` (the "always equal" hack) or int/str subclasses cannot cross the boundary.
- The worker drops to uid/gid 65534 (nobody) when started as root, and the hidden tests
  live only in a 0700 root-owned temp dir (the input files are deleted on read), so the
  candidate cannot read the tests or reference and echo expected outputs. It also cannot
  signal or ptrace this process.
- rlimits: address space (memory bombs), file size 0 (no writing files), process count
  (fork bombs), no core dumps. Per-call and total wall-clock timeouts (infinite loops).
- The worker's stdin/stdout/stderr are /dev/null at the fd level, so nothing it prints
  can reach the grader's stdout.
- SystemExit / os._exit / crashes in the candidate only kill the worker; the call fails,
  and the worker is restarted for the next test.
- PYTHONHASHSEED=0 for the worker so set/str-hash iteration order is deterministic.
Tasks therefore must be pure functions over plain data (no classes as entry points, no
in-place mutation of arguments, no generators as return values).
"""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import json
import multiprocessing as mp
import os
import shutil
import signal
import sys
import tempfile
import time
import types

GRADER_VERSION = "1"
NOBODY = 65534
MAX_MSG_BYTES = 8 * 1024 * 1024
MAX_DEPTH = 200
WORKER_NPROC = 32
# Imported before dropping privileges: if the interpreter's stdlib sits in a directory
# `nobody` cannot read, legitimate solutions using these modules still work.
PREIMPORT = (
    "abc", "array", "bisect", "cmath", "collections", "collections.abc", "contextlib",
    "copy", "dataclasses", "datetime", "decimal", "enum", "fractions", "functools",
    "heapq", "itertools", "json", "math", "numbers", "operator", "random", "re",
    "statistics", "string", "struct", "textwrap", "typing", "unicodedata",
)


# ---------------------------------------------------------------------------
# Plain-data codec (shared by both processes). Exact types only: subclasses rejected.
# ---------------------------------------------------------------------------
class Unencodable(Exception):
    pass


def encode(x, depth=0):
    if depth > MAX_DEPTH:
        raise Unencodable("value nested too deeply")
    t = type(x)
    if x is None:
        return ["N"]
    if t is bool:
        return ["b", x]
    if t is int:
        return ["i", str(x)]
    if t is float:
        return ["f", repr(x)]
    if t is str:
        return ["s", x]
    if t is bytes:
        return ["y", base64.b64encode(x).decode("ascii")]
    if t is list:
        return ["l", [encode(v, depth + 1) for v in x]]
    if t is tuple:
        return ["t", [encode(v, depth + 1) for v in x]]
    if t is set:
        return ["S", [encode(v, depth + 1) for v in x]]
    if t is frozenset:
        return ["F", [encode(v, depth + 1) for v in x]]
    if t is dict:
        return ["d", [[encode(k, depth + 1), encode(v, depth + 1)] for k, v in x.items()]]
    raise Unencodable(f"unsupported type {t.__name__} (only builtin plain data crosses)")


def decode(v, depth=0):
    if depth > MAX_DEPTH or not isinstance(v, list) or not v or not isinstance(v[0], str):
        raise ValueError("malformed value")
    tag = v[0]
    if tag == "N" and len(v) == 1:
        return None
    if len(v) != 2:
        raise ValueError("malformed value")
    body = v[1]
    if tag == "b" and type(body) is bool:
        return body
    if tag == "i" and type(body) is str:
        return int(body)
    if tag == "f" and type(body) is str:
        return float(body)
    if tag == "s" and type(body) is str:
        return body
    if tag == "y" and type(body) is str:
        return base64.b64decode(body, validate=True)
    if type(body) is not list:
        raise ValueError("malformed value")
    if tag == "l":
        return [decode(e, depth + 1) for e in body]
    if tag == "t":
        return tuple(decode(e, depth + 1) for e in body)
    if tag == "S":
        return {decode(e, depth + 1) for e in body}
    if tag == "F":
        return frozenset(decode(e, depth + 1) for e in body)
    if tag == "d":
        out = {}
        for pair in body:
            if type(pair) is not list or len(pair) != 2:
                raise ValueError("malformed value")
            out[decode(pair[0], depth + 1)] = decode(pair[1], depth + 1)
        return out
    raise ValueError("malformed value")


def _exc_info(e: BaseException) -> dict:
    """Name of the nearest *builtin* exception class, so `pytest.raises(ValueError)`
    matches a candidate's own `class MyError(ValueError)`."""
    name = "Exception"
    for cls in type(e).__mro__:
        if getattr(builtins, cls.__name__, None) is cls:
            name = cls.__name__
            break
    try:
        msg = str(e)[:300]
    except BaseException:  # a rigged __str__ must not break the protocol
        msg = "<unprintable>"
    return {"t": name, "m": msg}


# ---------------------------------------------------------------------------
# Worker process: runs the untrusted candidate.
# ---------------------------------------------------------------------------
def _worker(conn, source: str, mem_mb: int) -> None:  # pragma: no cover - runs in child
    os.setsid()  # own process group, so the parent can kill everything it spawns
    import resource

    for name in PREIMPORT:
        with contextlib.suppress(Exception):
            __import__(name)
    isolated = False
    if os.geteuid() == 0:
        os.setgroups([])
        os.setgid(NOBODY)
        os.setuid(NOBODY)
        isolated = True
    limit = mem_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    with contextlib.suppress(ValueError, OSError):
        resource.setrlimit(resource.RLIMIT_NPROC, (WORKER_NPROC, WORKER_NPROC))
    devnull = os.open(os.devnull, os.O_RDWR)
    for fd in (0, 1, 2):
        os.dup2(devnull, fd)
    os.chdir("/")

    def send(payload: dict) -> None:
        try:
            data = json.dumps(payload).encode()
        except Exception:
            data = json.dumps({"s": "err", "t": "TypeError", "m": "unserializable reply"}).encode()
        if len(data) > MAX_MSG_BYTES:
            data = json.dumps({"s": "err", "t": "MemoryError", "m": "reply too large"}).encode()
        conn.send_bytes(data)

    ns: dict = {"__name__": "solution", "__builtins__": builtins}
    load_error = None
    try:
        exec(compile(source, "solution.py", "exec"), ns)
    except BaseException as e:
        info = _exc_info(e)
        load_error = f"{info['t']}: {info['m']}"
    send({"s": "ready", "load_error": load_error, "isolated": isolated})

    while True:
        try:
            req = json.loads(conn.recv_bytes(MAX_MSG_BYTES))
        except (EOFError, OSError):
            os._exit(0)
        if load_error is not None:
            send({"s": "err", "t": "ImportError", "m": f"solution failed to load: {load_error}"})
            continue
        fn = ns.get(req.get("name"))
        if not callable(fn):
            send({"s": "err", "t": "AttributeError", "m": f"solution defines no function {req.get('name')!r}"})
            continue
        try:
            args = decode(req["args"])
            kwargs = decode(req["kwargs"])
            result = fn(*args, **kwargs)
            payload = {"s": "ok", "v": encode(result)}
        except Unencodable as e:
            payload = {"s": "err", "t": "TypeError", "m": f"invalid return value: {e}"}
        except BaseException as e:
            payload = {"s": "err", **_exc_info(e)}
        send(payload)


# ---------------------------------------------------------------------------
# Parent side: proxy + pytest (trusted).
# ---------------------------------------------------------------------------
class CandidateError(Exception):
    """A non-builtin exception, crash, or protocol violation from the candidate."""


def _rebuild(msg: dict) -> Exception:
    t, m = str(msg.get("t", "Exception")), str(msg.get("m", ""))
    cls = getattr(builtins, t, None)
    # Exception subclasses only: a candidate's SystemExit/KeyboardInterrupt must fail
    # the test, never abort the pytest session in this process.
    if isinstance(cls, type) and issubclass(cls, Exception):
        # Some builtins can't be built from a message alone (UnicodeDecodeError takes 5
        # args); fall back to the nearest constructible builtin ancestor
        # (UnicodeError, still a ValueError), so `pytest.raises(ValueError)` still matches.
        for base in cls.__mro__:
            if base is Exception or not issubclass(base, Exception):
                break
            try:
                return base(m)
            except Exception:
                continue
    return CandidateError(f"{t}: {m}")


class Candidate:
    def __init__(self, source: str, call_timeout: float, total_timeout: float, mem_mb: int):
        self.source = source
        self.call_timeout = call_timeout
        self.total_timeout = total_timeout
        self.mem_mb = mem_mb
        self.ctx = mp.get_context("spawn")
        self.proc = None
        self.conn = None
        self.spent = 0.0
        self.stats = {"calls": 0, "timeouts": 0, "crashes": 0, "load_error": None, "isolated": None}

    def _recv(self, timeout: float) -> dict:
        if not self.conn.poll(timeout):
            raise TimeoutError
        msg = json.loads(self.conn.recv_bytes(MAX_MSG_BYTES))
        if not isinstance(msg, dict):
            raise ValueError("malformed reply")
        return msg

    def _start(self, timeout: float) -> None:
        parent_conn, child_conn = self.ctx.Pipe(duplex=True)
        self.proc = self.ctx.Process(target=_worker, args=(child_conn, self.source, self.mem_mb), daemon=True)
        self.proc.start()
        child_conn.close()
        self.conn = parent_conn
        msg = self._recv(timeout)
        if msg.get("s") != "ready":
            raise ValueError("worker did not report ready")
        self.stats["load_error"] = msg.get("load_error")
        self.stats["isolated"] = bool(msg.get("isolated"))

    def kill(self) -> None:
        if self.proc is not None:
            with contextlib.suppress(Exception):
                os.killpg(self.proc.pid, signal.SIGKILL)
            with contextlib.suppress(Exception):
                self.proc.kill()
            with contextlib.suppress(Exception):
                self.proc.join(2)
        if self.conn is not None:
            with contextlib.suppress(Exception):
                self.conn.close()
        self.proc = self.conn = None

    def call(self, name: str, args: tuple, kwargs: dict):
        remaining = self.total_timeout - self.spent
        if remaining <= 0:
            raise TimeoutError("total time budget for this solution is exhausted")
        timeout = min(self.call_timeout, remaining)
        self.stats["calls"] += 1
        start = time.monotonic()
        try:
            if self.proc is None:
                self._start(timeout)
            self.conn.send_bytes(json.dumps({"name": name, "args": encode(list(args)), "kwargs": encode(dict(kwargs))}).encode())
            msg = self._recv(max(0.05, timeout - (time.monotonic() - start)))
        except TimeoutError:
            self.stats["timeouts"] += 1
            self.kill()
            raise TimeoutError(f"call to {name}() exceeded {timeout:.1f}s") from None
        except Unencodable:
            raise  # a bad *test argument*: task bug, surfaces as a test error
        except Exception:
            self.stats["crashes"] += 1
            self.kill()
            raise CandidateError("candidate process died or sent a malformed reply") from None
        finally:
            self.spent += time.monotonic() - start
        if msg.get("s") == "ok":
            try:
                return decode(msg.get("v"))
            except Exception:
                raise CandidateError("malformed return value") from None
        if msg.get("s") == "err":
            raise _rebuild(msg)
        raise CandidateError("malformed reply")


def install_proxy(candidate: Candidate) -> None:
    """`solution` module whose every public attribute forwards to the worker; nothing
    of the candidate is imported here, so collection never runs candidate code."""
    mod = types.ModuleType("solution")

    def __getattr__(name: str):
        if name.startswith("__"):
            raise AttributeError(name)

        def proxy(*args, **kwargs):
            return candidate.call(name, args, kwargs)

        proxy.__name__ = proxy.__qualname__ = name
        return proxy

    mod.__getattr__ = __getattr__
    sys.modules["solution"] = mod


class Collector:
    def __init__(self) -> None:
        self.collected = 0
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.collection_errors = 0
        self.first_failure = None

    def pytest_collection_modifyitems(self, items):
        self.collected = len(items)

    def pytest_collectreport(self, report):
        if report.failed:
            self.collection_errors += 1

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            if report.passed:
                self.passed += 1
            else:  # failed or skipped: anything but a pass counts against the solution
                self.failed += 1
        elif report.failed:
            self.errors += 1
        if report.failed and self.first_failure is None:
            text = str(report.longrepr)
            self.first_failure = f"{report.nodeid.split('::')[-1]}: {text[-400:]}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("solution")
    ap.add_argument("tests")
    ap.add_argument("--call-timeout", type=float, default=5.0)
    ap.add_argument("--total-timeout", type=float, default=60.0)
    ap.add_argument("--mem-mb", type=int, default=512)
    args = ap.parse_args()

    with open(args.solution, encoding="utf-8", errors="replace") as f:
        source = f.read()
    with open(args.tests, encoding="utf-8") as f:
        tests_src = f.read()
    for path in (args.solution, args.tests):  # hidden tests now exist only in workdir
        with contextlib.suppress(OSError):
            os.remove(path)
    workdir = tempfile.mkdtemp(prefix="pycode-grade-")  # mode 0700
    test_file = os.path.join(workdir, "test_hidden.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(tests_src)

    os.environ["PYTHONHASHSEED"] = "0"  # inherited by the spawned worker
    sys.dont_write_bytecode = True
    candidate = Candidate(source, args.call_timeout, args.total_timeout, args.mem_mb)
    install_proxy(candidate)
    collector = Collector()

    import pytest

    real_stdout = sys.stdout
    try:
        with contextlib.redirect_stdout(sys.stderr):
            rc = pytest.main(
                [test_file, "-q", "-p", "no:cacheprovider", "--rootdir", workdir, "--no-header"],
                plugins=[collector],
            )
    finally:
        candidate.kill()
        shutil.rmtree(workdir, ignore_errors=True)

    if collector.collection_errors or collector.collected == 0 or int(rc) not in (0, 1):
        print(
            f"grader error: pytest exit={int(rc)} collected={collector.collected} "
            f"collection_errors={collector.collection_errors}",
            file=sys.stderr,
        )
        return 2
    total = collector.collected
    ok = int(rc) == 0 and collector.passed == total and collector.failed == 0 and collector.errors == 0
    result = {
        "score": 1.0 if ok else 0.0,
        "passed": collector.passed,
        "total": total,
        "failed": collector.failed,
        "errors": collector.errors,
        "load_error": candidate.stats["load_error"],
        "timeouts": candidate.stats["timeouts"],
        "crashes": candidate.stats["crashes"],
        "isolated": candidate.stats["isolated"],
        "first_failure": collector.first_failure,
        "grader": GRADER_VERSION,
    }
    real_stdout.write(json.dumps(result) + "\n")
    real_stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
