[
    ("ISBN-13 weights 3,1 instead of 1,3", "(1 if i % 2 == 0 else 3)", "(3 if i % 2 == 0 else 1)"),
    ("979 ISBN-13s accepted", "        if not s.startswith(\"978\"):\n            raise ValueError(\"only 978 ISBN-13s have an ISBN-10 form\")\n", ""),
    ("ISBN-10 check value 10 written as '10' (wrong length) instead of X", 'return "X" if c == 10 else str(c)', "return str(c)"),
]
