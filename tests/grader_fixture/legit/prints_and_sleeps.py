import time

print("debug output at import")


def digit_sum(n):
    print("computing", n)
    time.sleep(0.3)
    if type(n) is not int:
        raise TypeError
    return sum(map(int, str(abs(n))))
