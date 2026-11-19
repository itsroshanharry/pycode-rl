```python
def run_jobs(jobs: list[tuple[str, int, int, int]], aging: int) -> list[tuple[str, int]]:
    """Simulate one worker running jobs with priorities and aging.

    Each job is (job_id, arrival, priority, duration) with integer arrival >= 0,
    priority (any int, higher = more urgent) and duration >= 1.
    The clock starts at 0. Whenever the worker is free at time t:
    - the candidates are the jobs not yet started with arrival <= t;
    - if there are none, the worker stays idle until the next arrival time;
    - otherwise it starts the candidate with the highest EFFECTIVE priority
      priority + (t - arrival) // aging, i.e. one extra point for every full
      `aging` time units the job has waited so far. Ties go to the earlier
      arrival, then to the job listed first in `jobs`.
    A started job runs to completion (no preemption), so the worker is next
    free at t + duration.

    Return (job_id, start_time) for every job, in the order the jobs start.
    Raise ValueError if aging < 1, an arrival is negative, a duration is < 1,
    or two jobs share an id.

    >>> run_jobs([("x", 0, 1, 10), ("old", 1, 0, 3), ("new", 9, 3, 1)], 2)
    [('x', 0), ('old', 10), ('new', 13)]
    """
```
