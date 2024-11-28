 
import unittest

class TestFactorialRecursive(unittest.TestCase):

    def test_non_negative_integer(self):
        self.assertEqual(factorial(5), 120)

    def test_zero_input(self):
        with self.assertRaises(str):
            factorial(-3)

    def test_invalid_input(self):
        with self.assertRaises(str):
            factorial('abc')

    def test_edge_cases(self):
        self.assertEqual(factorial(0), 1)
        self.assertEqual(factorial(1), 1)
 
print("OK")