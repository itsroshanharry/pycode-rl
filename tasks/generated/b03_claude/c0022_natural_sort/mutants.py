[
    ("digit runs compared as text", 'runs.append((0, int(run), ""))', "runs.append((1, 0, run))"),
    ("case-sensitive comparison of text runs", "runs.append((1, 0, run.casefold()))", "runs.append((1, 0, run))"),
    ("ties not broken by plain string order", "    return (runs, name)", "    return runs"),
]
