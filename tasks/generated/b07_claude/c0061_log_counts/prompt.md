```python
def log_counts(lines: list[str]) -> tuple[list[tuple[str, str, int]], int]:
    """Count log lines per minute and level.

    A trailing "\\n" or "\\r\\n" is removed from each line first. Lines that are
    then empty or only whitespace are ignored. Every other line must be:
      <timestamp> <spaces> <level> [" " <message>]
    - timestamp: "YYYY-MM-DDTHH:MM:SS" (ASCII digits), optionally followed by
      "." and 1+ digits, optionally followed by "Z"; it must be a real date and
      time (seconds 00-59);
    - one or more spaces;
    - level: letters, either bare (ERROR) or in square brackets ([ERROR]);
      case-insensitive; must be DEBUG, INFO, WARN, WARNING or ERROR, where
      WARNING counts as WARN;
    - optionally a single space and any message text.
    Anything else (leading spaces, unknown level, unbalanced bracket, ...) is a
    malformed line.

    Return (rows, malformed): rows are (minute, LEVEL, count) for each minute
    "YYYY-MM-DDTHH:MM" and normalized uppercase level that occurs, sorted by
    minute, then by severity DEBUG < INFO < WARN < ERROR; malformed is the
    number of malformed lines.

    >>> log_counts(["2024-05-01T10:15:42Z [error] disk full", "2024-05-01T10:15:59.123 WARNING slow", "oops"])
    ([('2024-05-01T10:15', 'WARN', 1), ('2024-05-01T10:15', 'ERROR', 1)], 1)
    """
```
