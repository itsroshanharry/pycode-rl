def exam_slots(exams: dict[str, list[str]], slots: int, per_slot: int) -> dict[str, int]:
    if slots < 1 or per_slot < 1:
        raise ValueError("slots and per_slot must be >= 1")
    students = {e: set(s) for e, s in exams.items()}  # repeated students count once
    by_student: dict[str, set[str]] = {}
    for e, ss in students.items():
        for s in ss:
            by_student.setdefault(s, set()).add(e)
    conflicts: dict[str, set[str]] = {e: set() for e in exams}
    for group in by_student.values():
        for e in group:
            conflicts[e] |= group - {e}  # a set: each other exam counted once
    order = sorted(exams, key=lambda e: (-len(conflicts[e]), -len(students[e]), e))
    slot_of: dict[str, int] = {}
    load = [0] * slots
    for e in order:
        taken = {slot_of[x] for x in conflicts[e] if x in slot_of}
        for t in range(slots):
            if t not in taken and load[t] < per_slot:
                slot_of[e] = t
                load[t] += 1
                break
        else:
            raise ValueError(f"cannot place exam {e!r}")
    return {e: slot_of[e] for e in sorted(exams)}
