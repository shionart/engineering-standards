import unittest

from shop.cart import cart_total_cents
from shop.money import to_cents


class MoneyTests(unittest.TestCase):
    def test_whole_amount(self):
        self.assertEqual(to_cents(5.0), 500)

    def test_cart_total(self):
        self.assertEqual(cart_total_cents([1.5, 2.0]), 350)


if __name__ == "__main__":
    unittest.main()
