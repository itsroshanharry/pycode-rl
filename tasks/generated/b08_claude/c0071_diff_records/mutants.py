[
    ("plain == comparison (1 == 1.0 == True)", "        \"changed\": sorted(k for k in old if k in new and not _same(old[k], new[k])),", "        \"changed\": sorted(k for k in old if k in new and old[k] != new[k]),"),
    ("lists compared with plain == (only the top level is strict)", "        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))", "        return a == b"),
    ("added keys in insertion order", "        \"added\": sorted(k for k in new if k not in old),", "        \"added\": [k for k in new if k not in old],"),
]
