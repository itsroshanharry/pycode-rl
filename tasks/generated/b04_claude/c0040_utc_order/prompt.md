```python
def utc_order(timestamps: list[str]) -> list[str]:
    """Sort RFC 3339 timestamps by the instant they denote, earliest first.

    Each timestamp is "YYYY-MM-DDTHH:MM:SS", optionally followed by a fraction
    ("." and one or more digits, any number of them), then a UTC offset: "Z", or
    "+HH:MM" / "-HH:MM" meaning local time is that far ahead of / behind UTC
    ("-00:00" is the same as "Z"). "T" and "Z" may also be lowercase. All digits
    are ASCII. Years are 0001-9999; months, days, hours (00-23), minutes (00-59)
    and seconds (00-59; leap second 60 is NOT accepted) must form a real
    proleptic Gregorian date and time. Offset hours are 00-23 and offset
    minutes 00-59.

    Fractions are compared exactly, however many digits they have
    (".5" == ".50", and ".0000001" is later than no fraction).
    Return the original strings, unchanged, in order of their instant;
    timestamps for the same instant keep their input order.
    Raise ValueError if any timestamp is malformed.

    >>> utc_order(["2024-03-10T12:00:00+02:00", "2024-03-10T11:00:00Z", "2024-03-10T09:30:00-01:00"])
    ['2024-03-10T12:00:00+02:00', '2024-03-10T09:30:00-01:00', '2024-03-10T11:00:00Z']
    """
```
