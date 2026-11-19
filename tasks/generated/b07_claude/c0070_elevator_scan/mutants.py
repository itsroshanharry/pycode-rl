[
    ("LOOK instead of SCAN: reverses at the last request ahead", "        distance = abs(end - start) + abs(end - behind[-1])", "        turn = ahead[-1] if ahead else start\n        distance = abs(turn - start) + abs(turn - behind[-1])"),
    ("a request at the start floor is dropped", "    if start in pending:\n        order.append(start)\n        pending.discard(start)\n", ""),
    ("after reversing, floors served farthest first", "        behind = sorted((f for f in pending if f < start), reverse=True)  # nearest first after reversing", "        behind = sorted(f for f in pending if f < start)"),
]
