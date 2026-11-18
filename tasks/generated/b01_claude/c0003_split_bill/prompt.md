```python
def split_bill(total_cents: int, weights: dict[str, int]) -> dict[str, int]:
    """Split `total_cents` among people in proportion to integer weights.

    Let W be the sum of all weights. Each person first gets
    floor(total_cents * weight / W) cents. The cents left over are then handed out
    one each to the people with the largest remainders (total_cents * weight) mod W;
    ties go to the name that sorts first (plain string comparison). The result maps
    every name to its amount, and the amounts always sum to total_cents.
    total_cents >= 0. Raise ValueError if `weights` is empty or any weight is not a
    positive int.

    >>> split_bill(1000, {"ann": 1, "bob": 1, "cy": 1})
    {'ann': 334, 'bob': 333, 'cy': 333}
    >>> split_bill(100, {"a": 2, "b": 1})
    {'a': 67, 'b': 33}
    """
```
