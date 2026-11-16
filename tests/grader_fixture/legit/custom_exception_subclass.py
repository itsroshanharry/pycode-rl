class BadInput(TypeError):
    pass


def digit_sum(n):
    if type(n) is not int:
        raise BadInput("not an int")  # must still satisfy pytest.raises(TypeError)
    return sum(map(int, str(abs(n))))
