from shop.money import to_cents


def invoice_line_cents(unit_price: float, quantity: int) -> int:
    return to_cents(unit_price) * quantity
