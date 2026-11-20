```python
def dedupe_contacts(records: list[dict[str, str]]) -> list[dict]:
    """Merge contact records that belong to the same person.

    Each record is a dict that may have the keys "name", "email", "phone" and
    "company" (string values; a key may be missing or the value empty). The
    record's id is its position in `records` (0, 1, 2, ...).

    Normalization:
    - email: strip surrounding whitespace, then str.lower(). It is invalid (as
      if absent) unless it has exactly one "@" with a non-empty part on each
      side. In the local part (before "@"), drop "+" and everything after it,
      for every domain. ONLY for the domains "gmail.com" and "googlemail.com":
      also remove every "." from the local part, and write the domain as
      "gmail.com". If the local part is then empty, the email is invalid.
    - phone: keep only the ASCII digits 0-9. If that gives exactly 11 digits
      starting with "1", drop that leading "1". Fewer than 7 digits: invalid.

    Two records belong to the same person if they share a normalized email OR
    a normalized phone, and this is transitive (A~B and B~C put A, B, C
    together). A record with neither a valid email nor a valid phone is a
    person on its own.

    Return one dict per person, ordered by the person's smallest record id:
      "ids":     sorted list of record ids;
      "name":    the longest name after stripping whitespace; ties go to the
                 record with the smaller id; None if no record has a name;
      "emails":  sorted list of the distinct normalized valid emails;
      "phones":  sorted list of the distinct normalized valid phones;
      "company": the stripped company of the record with the LARGEST id that
                 has a non-empty company; None if there is none.

    >>> dedupe_contacts([{"name": "Al", "email": "A.L+work@Gmail.com"}, {"name": "Alan", "phone": "+1 (415) 555-0100"}, {"email": "al@gmail.com", "phone": "415 555 0100", "company": "Acme"}])
    [{'ids': [0, 1, 2], 'name': 'Alan', 'emails': ['al@gmail.com'], 'phones': ['4155550100'], 'company': 'Acme'}]
    """
```
