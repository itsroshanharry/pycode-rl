import random

import pytest
from solution import expand_abbreviations

A = {"approx": "approximately", "e.g.": "for example", "asap": "as soon as possible", "dr": "doctor",
     "i.e.": "that is", "kg": "kilograms", "us": "United States"}


def _oracle(text, abbrevs):
    # independent: manual scan into tokens, explicit rule checks
    up = lambda c: "A" <= c <= "Z"
    low = lambda s: "".join(chr(ord(c) + 32) if up(c) else c for c in s)
    table = {low(k): v for k, v in abbrevs.items()}

    def case(src, exp):
        L = [c for c in src if up(c) or "a" <= c <= "z"]
        if len(L) >= 2 and all(up(c) for c in L):
            return exp.upper()
        if L and up(L[0]):
            return exp[:1].upper() + exp[1:]
        return exp

    out, i = [], 0
    is_tok = lambda c: up(c) or "a" <= c <= "z" or c == "."
    while i < len(text):
        if not is_tok(text[i]):
            out.append(text[i])
            i += 1
            continue
        j = i
        while j < len(text) and is_tok(text[j]):
            j += 1
        tok = text[i:j]
        if low(tok) in table:
            tok = case(tok, table[low(tok)])
        elif tok.endswith(".") and low(tok[:-1]) in table:
            tok = case(tok[:-1], table[low(tok[:-1])]) + "."
        out.append(tok)
        i = j
    return "".join(out)


CASES = [
    ("Approx. 5 kg, e.g. apples; ASAP!", A),
    ("", A),
    ("nothing here", A),
    ("approximate approx approxx", A),
    ("Dr. Who and DR. No; dr", A),
    ("E.G. and E.g. and e.G. and eg.", A),
    ("I.E. i.e.. ie", A),
    ("US us Us uS U.S.", A),
    ("Mr.Smith kg.kg KG? kG!", A),
    ("approx..", A),
    ("(asap)-asap_asap", A),
    ("café approxé", A),
    ("X x", {"X": "ex"}),
    ("Ab ab AB", {"ab": "alpha beta"}),
    ("ok", {"ok": ""}),
]

# Literal results produced by _oracle (not by hand).
FIXED = [
    (CASES[0], "Approximately. 5 kilograms, for example apples; AS SOON AS POSSIBLE!"),
    (CASES[4], "Doctor. Who and DOCTOR. No; doctor"),
    (CASES[7], "UNITED STATES United States United States United States U.S."),
    (CASES[12], "Ex ex"),
]


@pytest.mark.parametrize("text, abbrevs", CASES)
def test_against_oracle(text, abbrevs):
    assert expand_abbreviations(text, abbrevs) == _oracle(text, abbrevs)


@pytest.mark.parametrize("args, expected", FIXED)
def test_fixed(args, expected):
    assert expand_abbreviations(*args) == expected


def test_random_against_oracle():
    rng = random.Random(101)
    pieces = ["approx", "Approx", "APPROX", "e.g.", "E.G.", ".", " ", ",", "kg", "KG", "Kg", "us", "x", "-", "é", "dr", "DR"]
    for _ in range(500):
        text = "".join(rng.choice(pieces) for _ in range(rng.randint(0, 15)))
        assert expand_abbreviations(text, A) == _oracle(text, A), text
