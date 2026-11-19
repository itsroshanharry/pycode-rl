# Naive but correct: for every entry of a, scan all of b. O(len(a) * len(b)).
def reconcile(a, b, tol):
    if tol < 0:
        raise ValueError("tolerance must be >= 0")
    used = [False] * len(b)
    matches, unmatched_a = [], []
    for a_id, day, amount in a:
        best = None
        for j, (_, bday, bamount) in enumerate(b):
            if used[j] or bamount != amount:
                continue
            d = abs(bday - day)
            if d <= tol and (best is None or (d, bday, j) < best):
                best = (d, bday, j)
        if best is None:
            unmatched_a.append(a_id)
        else:
            used[best[2]] = True
            matches.append((a_id, b[best[2]][0]))
    return matches, unmatched_a, [b[j][0] for j in range(len(b)) if not used[j]]
