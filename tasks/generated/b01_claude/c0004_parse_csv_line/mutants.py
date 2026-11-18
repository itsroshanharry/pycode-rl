[
    ("doubled quote treated as the closing quote", "if i + 1 < n and line[i + 1] == '\"':", "if False:"),
    ("double quote accepted inside an unquoted field", "            if '\"' in field:\n                raise ValueError(\"double quote inside an unquoted field\")\n", ""),
    ("unterminated quoted field silently accepted", "                if i >= n:\n                    raise ValueError(\"unterminated quoted field\")\n", "                if i >= n:\n                    break\n"),
]
