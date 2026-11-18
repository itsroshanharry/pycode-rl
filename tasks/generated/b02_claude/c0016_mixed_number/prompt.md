```python
def mixed_number(numerator: int, denominator: int) -> str:
    """Write the fraction numerator/denominator as a simplified mixed number.

    Reduce the fraction to lowest terms. Then:
    - if it is a whole number, return that integer ("3", "-2", "0");
    - if its absolute value is less than 1, return "a/b";
    - otherwise return "w a/b", where w is the whole part and 0 < a/b < 1.
    A negative result has exactly one "-" at the very front ("-1 2/3", "-2/3"),
    never inside the fraction, and zero is "0" (never "-0"). Both arguments are ints
    and either may be negative. Raise ZeroDivisionError if denominator is 0.

    >>> mixed_number(-10, 6)
    '-1 2/3'
    >>> mixed_number(4, -6)
    '-2/3'
    """
```
