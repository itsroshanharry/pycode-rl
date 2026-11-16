def digit_sum(n):
    if type(n) is not int:
        raise TypeError("n must be an int")
    return sum(int(c) for c in str(abs(n)))
