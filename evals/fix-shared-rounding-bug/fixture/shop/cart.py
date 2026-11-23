from shop.money import to_cents


def cart_total_cents(prices: list[float]) -> int:
    return sum(to_cents(p) for p in prices)
