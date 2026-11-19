import re

_H = "[0-9A-Fa-f]"
_HYPHENATED = rf"({_H}{{8}})-({_H}{{4}})-({_H}{{4}})-({_H}{{4}})-({_H}{{12}})"
_FORMS = [
    re.compile(_HYPHENATED),
    re.compile(r"\{" + _HYPHENATED + r"\}"),
    re.compile(r"(?i:urn:uuid:)" + _HYPHENATED),
]
_PLAIN = re.compile(rf"({_H}{{8}})({_H}{{4}})({_H}{{4}})({_H}{{4}})({_H}{{12}})")


def normalize_uuid(text: str) -> str:
    for pattern in [*_FORMS, _PLAIN]:
        m = pattern.fullmatch(text)
        if m:
            return "-".join(m.groups()).lower()
    raise ValueError(f"not a UUID in an accepted form: {text!r}")
