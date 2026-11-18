```python
def render_template(template: str, variables: dict[str, str]) -> str:
    """Substitute variables into a template string.

    - "${name}" is replaced by variables[name] (an empty value is fine). If name is
      missing from `variables`, raise KeyError.
    - "${name:-default}" is replaced by variables[name] if name is present with a
      non-empty value, otherwise by `default`. The default is literal text up to
      the first "}" (it may be empty and is never itself substituted).
    - "$$" produces one literal "$".
    A name is one or more ASCII letters, digits or underscores, not starting with a
    digit. Inserted values are literal and are not scanned again. Text outside
    these forms is copied unchanged.
    Raise ValueError for any other use of "$": a lone "$" (also at the end), "$"
    followed by anything but "{" or "$", "${" with no closing "}", or a missing or
    invalid name (e.g. "${}", "${1a}", "${a b}", "${a:b}").

    >>> render_template("Hi ${user}, you owe $$${amount:-0}.", {"user": "Ann"})
    'Hi Ann, you owe $0.'
    >>> render_template("${a}${b:-x}", {"a": "${b}", "b": ""})
    '${b}x'
    """
```
