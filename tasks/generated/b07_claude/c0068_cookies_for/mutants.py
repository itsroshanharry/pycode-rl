[
    ("plain prefix match for paths", "        return cookie_path.endswith(\"/\") or request_path[len(cookie_path)] == \"/\"", "        return True"),
    ("replacing a cookie moves it to the end of the creation order", "        elif ident in store:\n            store[ident][1] = value  # keep the original creation order", "        elif ident in store:\n            store[ident] = [counter, value]\n            counter += 1"),
    ("only Max-Age=0 deletes (negative values ignored)", "                delete = int(val) <= 0", "                delete = int(val) == 0"),
]
