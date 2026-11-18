[
    ("batch still usable on its expiry day", "        while batches and batches[0][0] <= day:", "        while batches and batches[0][0] < day:"),
    ("newest batch spent first", "                    take = min(need, batches[0][1])\n                    batches[0][1] -= take\n                    need -= take\n                    if batches[0][1] == 0:\n                        batches.popleft()", "                    take = min(need, batches[-1][1])\n                    batches[-1][1] -= take\n                    need -= take\n                    if batches[-1][1] == 0:\n                        batches.pop()"),
    ("insufficient balance spends everything instead of rejecting", "            if sum(b[1] for b in batches) >= points:\n                need = points", "            if True:\n                need = min(points, sum(b[1] for b in batches))"),
]
