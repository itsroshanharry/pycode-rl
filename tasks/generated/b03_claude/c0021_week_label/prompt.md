```python
def week_label(date: str, week_start: int = 0) -> str:
    """Week-numbering label "YYYY-Www" for a date, with a configurable first weekday.

    `date` is "YYYY-MM-DD" (exactly that form) with a year from 1900 to 2100.
    Weeks are blocks of 7 days beginning on `week_start` (0 = Monday ... 6 =
    Sunday). Week 1 of a year is the week that contains January 4 of that year;
    later weeks are numbered 2, 3, ... The label's year is the year whose week 1
    starts this numbering, which can differ from the calendar year for dates near
    January 1 (late December dates may belong to week 1 of the next year, early
    January dates to the last week of the previous year). The week number has two
    digits. With week_start == 0 this is exactly ISO-8601 week numbering.
    Raise ValueError if `date` is malformed or invalid, or if week_start is not an
    int from 0 to 6.

    >>> week_label("2021-01-03")
    '2020-W53'
    >>> week_label("2021-01-03", 6)
    '2021-W01'
    """
```
