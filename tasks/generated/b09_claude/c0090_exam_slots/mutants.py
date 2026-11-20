[
    ("degree counts shared (student, exam) pairs instead of distinct exams", "    order = sorted(exams, key=lambda e: (-len(conflicts[e]), -len(students[e]), e))", "    order = sorted(exams, key=lambda e: (-sum(len(by_student[s]) - 1 for s in students[e]), -len(students[e]), e))"),
    ("a slot accepts per_slot + 1 exams", "            if t not in taken and load[t] < per_slot:", "            if t not in taken and load[t] <= per_slot:"),
    ("student count skipped as the second ordering key", "    order = sorted(exams, key=lambda e: (-len(conflicts[e]), -len(students[e]), e))", "    order = sorted(exams, key=lambda e: (-len(conflicts[e]), e))"),
]
