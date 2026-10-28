"""Checks for the calculator operations."""

import unittest

from calculator import add, multiply, subtract


class CalculatorTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_subtract(self):
        self.assertEqual(subtract(2, 3), -1)

    def test_multiply(self):
        for a, b, expected in [(2, 3, 6), (-2, 3, -6), (0, 3, 0)]:
            with self.subTest(a=a, b=b):
                self.assertEqual(multiply(a, b), expected)
