import unittest

from appy_ast import Value
from interpreter import evaluate_expression
from lexer import create_lexer
from parser import create_parser

class InterpreterTest(unittest.TestCase):
    def test_basic_interpreter(self):
        self.assert_evaluate('5 + 3', Value(8))

    def test_order_of_operations(self):
        self.assert_evaluate('1 + 2 * 3', Value(7))

    def test_parens(self):
        self.assert_evaluate('5 / (1 + 1)', Value(2))

    def assert_evaluate(self, program, expected_value):
        ast = self.get_ast(program)
        self.assertEqual(expected_value, evaluate_expression(ast))

    def get_ast(self, program):
        parser = create_parser()
        lexer = create_lexer()
        return parser.parse(program)

if __name__ == '__main__':
    unittest.main()
