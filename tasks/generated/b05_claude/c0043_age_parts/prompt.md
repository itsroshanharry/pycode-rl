```python
def age_parts(birth: str, on: str) -> tuple[int, int]:
    """Age on a given date as (full years, days since the most recent birthday).

    Dates are "YYYY-MM-DD" (ASCII digits, years 0001-9999, Gregorian calendar).
    A person's birthday in year Y has the birth month and day, except that a
    Feb 29 birthday falls on MARCH 1 in years that have no Feb 29.
    The person is 0 years old on the birth date and one year older on each
    birthday. The second number counts days from the most recent birthday
    (or the birth date) up to `on`.

    Raise ValueError for a malformed or impossible date, or if `on` is
    before `birth`.

    >>> age_parts("2020-02-29", "2023-02-28")
    (2, 364)
    >>> age_parts("2020-02-29", "2023-03-01")
    (3, 0)
    """
```
