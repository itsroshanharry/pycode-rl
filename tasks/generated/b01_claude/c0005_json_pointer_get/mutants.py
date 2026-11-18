[
    ("leading zeros accepted in list indices", '_INDEX = re.compile(r"0|[1-9][0-9]*")', '_INDEX = re.compile(r"[0-9]+")'),
    ("~0 decoded as '/'", '            if nxt == "0":\n                out.append("~")', '            if nxt == "0":\n                out.append("/")'),
    ("missing key returns None instead of raising", "            if tok not in cur:\n                raise KeyError(tok)\n            cur = cur[tok]", "            cur = cur.get(tok)"),
]
