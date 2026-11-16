from collections import OrderedDict


def lru_trace(capacity: int, ops: list[tuple]) -> list[int]:
    cache: OrderedDict = OrderedDict()
    out = []
    for op in ops:
        if op[0] == "get":
            key = op[1]
            if key in cache:
                cache.move_to_end(key)
                out.append(cache[key])
            else:
                out.append(-1)
        else:
            _, key, value = op
            if capacity <= 0:
                continue
            if key in cache:
                cache.move_to_end(key)
            elif len(cache) >= capacity:
                cache.popitem(last=False)
            cache[key] = value
    return out
