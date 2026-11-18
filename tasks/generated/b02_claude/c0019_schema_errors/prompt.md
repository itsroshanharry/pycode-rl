```python
def schema_errors(value, schema: dict) -> list[str]:
    """Validate a JSON-like value against a small schema and list every error.

    A schema is a dict with a "type": "int", "float", "str", "bool", "null", "list"
    or "dict", plus optional keys: "min"/"max" (inclusive) for int and float;
    "max_len" for str; "items" (schema for every element) for list; "fields" (dict
    of field name -> schema) and "required" (list of field names) for dict. Fields
    not listed in "fields" are allowed and ignored.
    Type rules: "int" accepts int but not bool; "float" accepts int or float but not
    bool; "bool" only bool; "null" only None; "list" only list; "dict" only dict.
    Each error is "<path>: <message>". The top-level path is "$"; a dict field
    appends "." + name, a list item appends "[i]". Messages are exactly
    "expected <type>", "below min <min>", "above max <max>", "longer than <max_len>"
    and "missing required field" (numbers written with str()). If a value has the
    wrong type, report only "expected <type>" for it and check nothing inside it.
    Order: depth-first; for a dict, first the present fields in the order of the
    schema's "fields", then missing required fields in "required" order; list items
    by index; for a number, a min error before a max error. A valid value gives [].

    >>> schema_errors({"age": -1, "tags": ["a", 3]}, {"type": "dict", "fields": {"age": {"type": "int", "min": 0}, "tags": {"type": "list", "items": {"type": "str"}}, "name": {"type": "str"}}, "required": ["name"]})
    ['$.age: below min 0', '$.tags[1]: expected str', '$.name: missing required field']
    """
```
