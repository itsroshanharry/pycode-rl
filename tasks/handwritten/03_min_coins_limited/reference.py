def min_coins_limited(amount: int, coins: list[tuple[int, int]]) -> int:
    counts: dict[int, int] = {}
    for value, count in coins:
        counts[value] = counts.get(value, 0) + count
    inf = float("inf")
    dp = [0] + [inf] * amount
    for value, count in counts.items():
        # Binary splitting: pieces of 1, 2, 4, ... coins can form any count <= `count`.
        piece = 1
        while count > 0:
            take = min(piece, count)
            weight = take * value
            for a in range(amount, weight - 1, -1):
                if dp[a - weight] + take < dp[a]:
                    dp[a] = dp[a - weight] + take
            count -= take
            piece *= 2
    return int(dp[amount]) if dp[amount] != inf else -1
