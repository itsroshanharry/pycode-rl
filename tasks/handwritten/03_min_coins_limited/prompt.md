```python
def min_coins_limited(amount: int, coins: list[tuple[int, int]]) -> int:
    """Fewest coins that sum exactly to `amount`, using each coin type a limited
    number of times.

    `coins` holds (value, count) pairs: `count` coins of denomination `value` are
    available. Values are positive, counts are >= 0, and the same value may appear
    in several pairs (their counts add up). Return the minimum number of coins
    whose values sum to exactly `amount`, or -1 if it is impossible. An amount of
    0 needs 0 coins. Inputs satisfy 0 <= amount <= 10_000 and the total number of
    coins is at most 10_000.

    >>> min_coins_limited(11, [(5, 1), (2, 5), (1, 0)])
    4
    >>> min_coins_limited(3, [(2, 3)])
    -1
    """
```
