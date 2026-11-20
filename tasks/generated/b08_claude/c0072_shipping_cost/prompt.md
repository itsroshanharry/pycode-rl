```python
def shipping_cost(weight_g: int, dims_cm: tuple[int, int, int], zone: str, subtotal: int,
                  rates: dict[str, list[tuple[int, int]]], free_over: dict[str, int]) -> int:
    """Shipping price in cents for one parcel.

    1. Dimensional weight in grams = ceil(L * W * H / 5), i.e. the volume in
       cm^3 divided by 5000, in kg, rounded UP to a whole gram.
    2. Billable weight = max(actual weight, dimensional weight), then rounded
       UP to a multiple of 500 g (exact multiples stay as they are).
    3. `rates[zone]` is a list of (max_grams, price_cents) with strictly
       increasing max_grams: the price is that of the first entry whose
       max_grams >= billable weight. Heavier than the last entry: ValueError.
    4. Free shipping: if `zone` is in `free_over` and subtotal >= free_over[zone],
       the price is 0 (but the weight checks above still apply).
    Raise ValueError for weight_g < 1, any dimension < 1, an unknown zone, or
    a parcel that is too heavy.

    >>> shipping_cost(1200, (30, 20, 10), "EU", 4999, {"EU": [(1000, 500), (2000, 800), (5000, 1500)]}, {"EU": 5000})
    800
    """
```
