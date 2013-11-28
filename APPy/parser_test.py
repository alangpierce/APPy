import unittest

from appy_ast import BinaryOperator, Literal
from lexer import create_lexer
from parser import create_parser

class ParserTest(unittest.TestCase):
    def test_basic_parsing(self):
        self.assert_ast(
            '5 + 3',
            BinaryOperator('+', Literal(5), Literal(3)))

    def test_operator_precedence(self):
        self.assert_ast(
            '1*2 + 5*6 - 4/2',
            BinaryOperator('-',
                BinaryOperator('+',
                    BinaryOperator('*', Literal(1), Literal(2)),
                    BinaryOperator('*', Literal(5), Literal(6))),
                BinaryOperator('/', Literal(4), Literal(2))))

    def assert_ast(self, program, expected_ast):
        actual_ast = self.get_ast(program)
        self.assertEqual(expected_ast, actual_ast,
                         "Expected: " + expected_ast.pretty_print() +
                         ", Actual: " + actual_ast.pretty_print(), )

    def get_ast(self, program):
        parser = create_parser()
        lexer = create_lexer()
        return parser.parse(program, lexer)


if __name__ == '__main__':
    unittest.main()
