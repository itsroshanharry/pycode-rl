[
    ("a successful get does not refresh recency", "                cache.move_to_end(key)\n                out.append(cache[key])", "                out.append(cache[key])"),
    ("overwriting put does not refresh recency", "            if key in cache:\n                cache.move_to_end(key)\n            elif", "            if key in cache:\n                pass\n            elif"),
    ("capacity 0 not special-cased (evicts from an empty cache)", "            if capacity <= 0:\n                continue\n", ""),
]
