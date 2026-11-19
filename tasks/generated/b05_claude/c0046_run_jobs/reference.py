def run_jobs(jobs: list[tuple[str, int, int, int]], aging: int) -> list[tuple[str, int]]:
    if aging < 1:
        raise ValueError("aging must be >= 1")
    ids = set()
    for job_id, arrival, _, duration in jobs:
        if arrival < 0 or duration < 1 or job_id in ids:
            raise ValueError(f"bad job: {job_id!r}")
        ids.add(job_id)

    pending = list(enumerate(jobs))  # (input index, job)
    t, out = 0, []
    while pending:
        ready = [(i, j) for i, j in pending if j[1] <= t]
        if not ready:
            t = min(j[1] for _, j in pending)  # idle until the next arrival
            continue
        # Effective priority is evaluated at the moment the worker picks.
        i, job = max(ready, key=lambda ij: (ij[1][2] + (t - ij[1][1]) // aging, -ij[1][1], -ij[0]))
        pending.remove((i, job))
        out.append((job[0], t))
        t += job[3]
    return out
