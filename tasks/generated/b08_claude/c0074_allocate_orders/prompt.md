```python
def allocate_orders(orders: list[tuple[str, int, str, int]],
                    warehouses: list[tuple[str, dict[str, int]]]) -> list[tuple[str, list[tuple[str, int]], int]]:
    """Reserve stock for orders across warehouses, with partial fulfilment.

    `orders` are (order_id, priority, sku, qty) with qty >= 1; `warehouses`
    are (name, {sku: units in stock}) listed in PREFERENCE order.
    Orders are processed by priority, highest first; equal priorities keep
    their input order. Each order takes stock from the warehouses in
    preference order, as much as each one has of that sku, until the order's
    quantity is reached or stock runs out; taken stock is no longer available
    to later orders.

    For each order return (order_id, [(warehouse, units taken), ...],
    shortfall), listing only warehouses it took more than 0 units from (in
    preference order); shortfall is the quantity it did not get. The result
    is in the ORIGINAL order of `orders`, not the processing order.

    Raise ValueError for qty < 1, a duplicate order id, a duplicate
    warehouse name, or a negative stock level.

    >>> allocate_orders([("o1", 1, "A", 5), ("o2", 9, "A", 4)], [("north", {"A": 3}), ("south", {"A": 3})])
    [('o1', [('south', 2)], 3), ('o2', [('north', 3), ('south', 1)], 0)]
    """
```
