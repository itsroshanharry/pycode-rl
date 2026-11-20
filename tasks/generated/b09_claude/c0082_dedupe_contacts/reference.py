_GMAIL = ("gmail.com", "googlemail.com")


def _norm_email(raw):
    if not raw:
        return None
    e = raw.strip().lower()
    if e.count("@") != 1:
        return None
    local, domain = e.split("@")
    if not local or not domain:
        return None
    local = local.split("+", 1)[0]  # "+tag" is dropped for every domain
    if domain in _GMAIL:
        local = local.replace(".", "")  # dots only matter outside Gmail
        domain = "gmail.com"
    return f"{local}@{domain}" if local else None


def _norm_phone(raw):
    if not raw:
        return None
    digits = "".join(c for c in raw if c in "0123456789")
    if len(digits) == 11 and digits[0] == "1":
        digits = digits[1:]  # North American country code
    return digits if len(digits) >= 7 else None


def dedupe_contacts(records: list[dict[str, str]]) -> list[dict]:
    n = len(records)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    emails = [_norm_email(r.get("email")) for r in records]
    phones = [_norm_phone(r.get("phone")) for r in records]
    owner: dict = {}  # normalized key -> first record id holding it
    for i in range(n):
        for key in (("e", emails[i]), ("p", phones[i])):
            if key[1] is None:
                continue
            if key in owner:
                a, b = find(i), find(owner[key])
                if a != b:
                    parent[max(a, b)] = min(a, b)  # union: transitive merging
            else:
                owner[key] = i

    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)

    out = []
    for ids in sorted(groups.values(), key=lambda g: g[0]):
        name = None
        for i in ids:  # ids ascending, so ">" keeps the earliest on ties
            v = (records[i].get("name") or "").strip()
            if v and (name is None or len(v) > len(name)):
                name = v
        company = None
        for i in ids:  # later non-empty values overwrite: the largest id wins
            v = (records[i].get("company") or "").strip()
            if v:
                company = v
        out.append({
            "ids": ids,
            "name": name,
            "emails": sorted({emails[i] for i in ids if emails[i]}),
            "phones": sorted({phones[i] for i in ids if phones[i]}),
            "company": company,
        })
    return out
