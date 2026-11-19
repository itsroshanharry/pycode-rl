def overtime_pay(daily_minutes: list[int], rate_cents: int) -> int:
    if len(daily_minutes) != 7 or any(not 0 <= m <= 1440 for m in daily_minutes) or rate_cents < 0:
        raise ValueError("bad input")
    seventh = all(m > 0 for m in daily_minutes)
    halves = 0  # sum of multipliers in units of 0.5 (2 = 1.0x, 3 = 1.5x, 4 = 2.0x)
    week = 0
    for day, minutes in enumerate(daily_minutes):
        for k in range(1, minutes + 1):  # k-th minute of the day
            week += 1
            d = 2 if k <= 480 else 3 if k <= 720 else 4
            w = 3 if week > 2400 else 2
            s = (3 if k <= 480 else 4) if seventh and day == 6 else 2
            halves += max(d, w, s)
    # pay = rate/60 * halves/2 = rate * halves / 120, rounded half up once.
    return (rate_cents * halves * 2 + 120) // 240
