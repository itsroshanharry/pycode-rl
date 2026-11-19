import re

_NAME = r"[A-Za-z]+(?: [A-Za-z]+)*"
_RESULT = re.compile(rf"({_NAME}) ([0-9]+)-([0-9]+) ({_NAME})")


def _stats(matches, teams) -> dict[str, list[int]]:
    """[points, goal difference, goals scored] per team, from the given matches."""
    table = {t: [0, 0, 0] for t in teams}
    for home, hg, ag, away in matches:
        for team, gf, ga in ((home, hg, ag), (away, ag, hg)):
            row = table[team]
            row[0] += 3 if gf > ga else 1 if gf == ga else 0
            row[1] += gf - ga
            row[2] += gf
    return table


def league_table(results: list[str]) -> list[str]:
    matches = []
    for r in results:
        m = _RESULT.fullmatch(r)
        if not m:
            raise ValueError(f"malformed result: {r!r}")
        home, away = m.group(1), m.group(4)
        if home == away:
            raise ValueError(f"team plays itself: {r!r}")
        matches.append((home, int(m.group(2)), int(m.group(3)), away))

    teams = sorted({t for home, _, _, away in matches for t in (home, away)})
    overall = _stats(matches, teams)
    groups: dict[tuple[int, ...], list[str]] = {}
    for t in teams:
        groups.setdefault(tuple(overall[t]), []).append(t)

    order = []
    for key in sorted(groups, reverse=True):
        group = groups[key]
        if len(group) > 1:
            members = set(group)
            h2h = _stats([m for m in matches if m[0] in members and m[3] in members], group)
            group = sorted(group, key=lambda t: (-h2h[t][0], -h2h[t][1], -h2h[t][2], t))
        order.extend(group)
    return order
