BYE = "BYE"


def round_robin(teams: list[str]) -> list[list[tuple[str, str]]]:
    if len(teams) < 2 or len(set(teams)) != len(teams) or BYE in teams:
        raise ValueError("need at least 2 unique teams, none named 'BYE'")
    entries = list(teams) + ([BYE] if len(teams) % 2 else [])
    n = len(entries)
    first, rest = entries[0], entries[1:]
    rounds = []
    for r in range(n - 1):
        k = r % len(rest)
        rotated = rest[len(rest) - k :] + rest[: len(rest) - k]  # rotate right by r
        arrangement = [first] + rotated
        matches = []
        for i in range(n // 2):
            a, b = arrangement[i], arrangement[n - 1 - i]
            if BYE not in (a, b):
                matches.append((a, b))
        rounds.append(matches)
    return rounds
