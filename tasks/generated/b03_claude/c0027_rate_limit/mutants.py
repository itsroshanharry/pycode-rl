[
    ("window boundary included (t == T - window still counts)", "while dq and dq[0] <= time - window:", "while dq and dq[0] < time - window:"),
    ("denied requests counted toward the limit", "        if len(dq) < limit:\n            dq.append(time)\n            out.append(True)\n        else:\n            out.append(False)", "        ok = len(dq) < limit\n        dq.append(time)\n        out.append(ok)"),
    ("one shared window for all clients", "dq = allowed.setdefault(client, deque())", "dq = allowed.setdefault(\"*\", deque())"),
]
