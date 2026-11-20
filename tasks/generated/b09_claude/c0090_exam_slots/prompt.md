```python
def exam_slots(exams: dict[str, list[str]], slots: int, per_slot: int) -> dict[str, int]:
    """Greedy exam timetabling so that no student sits two exams at once.

    `exams` maps an exam id to its students (a student listed twice counts
    once). Two exams CONFLICT if they share at least one student. Time slots are
    numbered 0 .. slots-1, and a slot holds at most `per_slot` exams.

    Place the exams one at a time, in this order:
      1. more conflicting exams first (the number of DISTINCT other exams it
         conflicts with, not the number of shared students);
      2. then more distinct students first;
      3. then exam id ascending (plain string order).
    Each exam goes into the lowest-numbered slot that has no already-placed
    conflicting exam and fewer than `per_slot` exams so far.

    Return {exam id: slot} with keys in ascending id order.
    Raise ValueError if slots < 1 or per_slot < 1, or if some exam cannot be
    placed in any slot.

    >>> exam_slots({"math": ["ann", "bob"], "art": ["bob"], "bio": ["cat"], "chem": ["ann", "cat"]}, 3, 2)
    {'art': 0, 'bio': 1, 'chem': 0, 'math': 1}
    """
```
