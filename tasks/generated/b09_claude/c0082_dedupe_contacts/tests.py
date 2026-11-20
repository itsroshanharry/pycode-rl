import random
import re

import pytest
from solution import dedupe_contacts


def _email(raw):
    if not raw:
        return None
    e = raw.strip().lower()
    m = re.fullmatch(r"([^@]+)@([^@]+)", e)
    if not m:
        return None
    local, domain = m.group(1).partition("+")[0], m.group(2)
    if domain in {"gmail.com", "googlemail.com"}:
        local, domain = "".join(local.split(".")), "gmail.com"
    return local + "@" + domain if local else None


def _phone(raw):
    d = re.sub(r"[^0-9]", "", raw or "", flags=re.ASCII)
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return d if len(d) >= 7 else None


def _oracle(records):
    # pairwise "shares a key" graph + BFS components (independent of union-find)
    keys = [{("e", _email(r.get("email"))), ("p", _phone(r.get("phone")))} - {("e", None), ("p", None)} for r in records]
    seen, groups = set(), []
    for s in range(len(records)):
        if s in seen:
            continue
        comp, stack = [], [s]
        seen.add(s)
        while stack:
            i = stack.pop()
            comp.append(i)
            for j in range(len(records)):
                if j not in seen and keys[i] & keys[j]:
                    seen.add(j)
                    stack.append(j)
        groups.append(sorted(comp))
    out = []
    for ids in groups:
        names = [(records[i].get("name") or "").strip() for i in ids]
        names = [(len(v), -i, v) for i, v in zip(ids, names) if v]
        comps = [(records[i].get("company") or "").strip() for i in ids]
        comps = [v for v in comps if v]
        out.append({
            "ids": ids,
            "name": max(names)[2] if names else None,
            "emails": sorted({k[1] for i in ids for k in keys[i] if k[0] == "e"}),
            "phones": sorted({k[1] for i in ids for k in keys[i] if k[0] == "p"}),
            "company": comps[-1] if comps else None,
        })
    return out


def _norm(result):
    return [{k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in g.items()} for g in result]


DOC = [{"name": "Al", "email": "A.L+work@Gmail.com"}, {"name": "Alan", "phone": "+1 (415) 555-0100"},
       {"email": "al@gmail.com", "phone": "415 555 0100", "company": "Acme"}]

# Literal expected values were produced by _oracle above, not by hand.
FIXED = [
    (DOC, [{"ids": [0, 1, 2], "name": "Alan", "emails": ["al@gmail.com"], "phones": ["4155550100"], "company": "Acme"}]),
    ([], []),
    ([{"name": "  Solo  "}], [{"ids": [0], "name": "Solo", "emails": [], "phones": [], "company": None}]),
    ([{"email": "a.b@corp.com"}, {"email": "ab@corp.com"}],
     [{"ids": [0], "name": None, "emails": ["a.b@corp.com"], "phones": [], "company": None},
      {"ids": [1], "name": None, "emails": ["ab@corp.com"], "phones": [], "company": None}]),
    ([{"email": "x.y@googlemail.com", "company": "A"}, {"email": "XY@gmail.com", "company": " B "}],
     [{"ids": [0, 1], "name": None, "emails": ["xy@gmail.com"], "phones": [], "company": "B"}]),
]


@pytest.mark.parametrize("records, expected", FIXED)
def test_fixed(records, expected):
    assert _norm(dedupe_contacts(records)) == expected


CASES = [
    # transitivity: 0~1 by email, 1~2 by phone, 2~3 by email
    [{"email": "a@x.org"}, {"email": "A@X.org", "phone": "555-1234"}, {"phone": "5551234", "email": "c@y.io"}, {"email": "c@y.io"}],
    # two groups that get joined by a later record
    [{"email": "p@q.com"}, {"phone": "212-555-0000"}, {"email": "p@q.com", "phone": "(212) 555 0000"}],
    # invalid emails / phones never link
    [{"email": "a@b@c"}, {"email": "a@b@c"}, {"email": "@x.com"}, {"email": "@x.com"}, {"email": "x@"}, {"phone": "123456"}, {"phone": "12-34-56"}],
    # "+tag" for every domain, empty local after the tag
    [{"email": "bob+news@corp.com"}, {"email": "Bob@Corp.com"}, {"email": "+only@corp.com"}, {"email": "+only@corp.com"}],
    # NANP: 11 digits starting with 1 lose the 1; 11 digits starting with 2 do not; 12 digits do not
    [{"phone": "1-800-555-0199"}, {"phone": "800 555 0199"}, {"phone": "28005550199"}, {"phone": "118005550199"}],
    # name ties -> smaller id, longest wins otherwise; company -> largest id with a value
    [{"name": "Ann", "email": "z@z.zz", "company": "First"}, {"name": "Bea", "email": "z@z.zz"}, {"name": "Carla", "email": "z@z.zz", "company": ""},
     {"name": "Dora ", "email": "z@z.zz", "company": "  Last "}, {"email": "z@z.zz", "company": "   "}],
    # whitespace and case around emails; gmail dots and googlemail
    [{"email": "  J.Doe@GoogleMail.com "}, {"email": "jdoe+x@gmail.com"}, {"email": "j.doe@gmail.co"}],
    # non-ASCII digits are not digits
    [{"phone": "５５５１２３４"}, {"phone": "5551234"}],
    # missing keys and empty strings
    [{}, {"name": "", "email": "", "phone": "", "company": ""}, {"name": "X"}],
]


@pytest.mark.parametrize("records", CASES)
def test_against_oracle(records):
    assert _norm(dedupe_contacts(records)) == _oracle(records)


def test_random_against_oracle():
    rng = random.Random(89)
    emails = ["a@x.com", "A@X.com", "a+1@x.com", "a.b@gmail.com", "ab@googlemail.com", "AB+z@gmail.com", "bad", "c@y.org", "", None]
    phones = ["555-0100", "1 555 0100", "(555) 0100", "1-212-555-0100", "212.555.0100", "123", "", None, "999-9999"]
    for _ in range(300):
        recs = []
        for _ in range(rng.randint(0, 9)):
            r = {}
            for key, pool in (("email", emails), ("phone", phones), ("name", ["Al", "Alan", "  Bo ", "", None]), ("company", ["A", "", " B", None])):
                v = rng.choice(pool)
                if v is not None:
                    r[key] = v
            recs.append(r)
        assert _norm(dedupe_contacts(recs)) == _oracle(recs), recs
