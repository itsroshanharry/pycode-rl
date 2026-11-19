import re

_WS = " \t"


def _path_matches(cookie_path: str, request_path: str) -> bool:
    # RFC 6265 section 5.1.4: not a plain startswith ("/docs" must not match "/docsx").
    if cookie_path == request_path:
        return True
    if request_path.startswith(cookie_path):
        return cookie_path.endswith("/") or request_path[len(cookie_path)] == "/"
    return False


def cookies_for(set_cookies: list[str], request_path: str) -> str:
    if not request_path.startswith("/"):
        raise ValueError("request path must start with '/'")
    store: dict[tuple[str, str], list] = {}  # (name, path) -> [creation number, value]
    counter = 0
    for header in set_cookies:
        first, *attrs = header.split(";")
        name, eq, value = first.partition("=")
        name, value = name.strip(_WS), value.strip(_WS)
        if not eq or not name:
            continue
        path, delete = "/", False
        for attr in attrs:
            key, _, val = attr.partition("=")
            key, val = key.strip(_WS).lower(), val.strip(_WS)
            if key == "path":
                path = val if val.startswith("/") else "/"
            elif key == "max-age" and re.fullmatch(r"-?[0-9]+", val):
                delete = int(val) <= 0
        ident = (name, path)
        if delete:
            store.pop(ident, None)
        elif ident in store:
            store[ident][1] = value  # keep the original creation order
        else:
            store[ident] = [counter, value]
            counter += 1
    sent = [(-len(p), order, f"{n}={v}") for (n, p), (order, v) in store.items() if _path_matches(p, request_path)]
    return "; ".join(text for _, _, text in sorted(sent))
