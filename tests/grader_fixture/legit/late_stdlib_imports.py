# Imports happen inside the call, i.e. after the worker dropped privileges.
def digit_sum(n):
    import calendar, collections, functools, operator  # calendar is not pre-imported
    if type(n) is not int:
        raise TypeError("n must be an int")
    assert calendar.isleap(2024)
    counts = collections.Counter(str(abs(n)))
    return functools.reduce(operator.add, (int(d) * c for d, c in counts.items()), 0)
