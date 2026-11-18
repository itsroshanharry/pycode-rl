[
    ("fill limit off by one", "out.append(last if have and run <= limit else None)", "out.append(last if have and run < limit else None)"),
    ("gap counter not reset after a real value", "            run = 0\n", ""),
    ("falsy values treated as missing", "        if v is None:", "        if not v:"),
]
