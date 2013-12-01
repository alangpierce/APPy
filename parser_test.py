import unittest

from appy_ast import BinaryOperator, Literal, Value
from lexer import create_lexer
from parser import create_parser


def int_literal(int):
    return Literal(Value('int', int))


def string_literal(string):
    return Literal(Value('str', string))


class ParserTest(unittest.TestCase):
    def test_basic_parsing(self):
        self.assert_ast(
            '5 + 3',
            BinaryOperator('+', int_literal(5), int_literal(3)))

    def test_operator_precedence(self):
        self.assert_ast(
            '1*2 + 5*6 - 4/2',
            BinaryOperator(
                '-',
                BinaryOperator(
                    '+',
                    BinaryOperator('*', int_literal(1), int_literal(2)),
                    BinaryOperator('*', int_literal(5), int_literal(6))),
                BinaryOperator('/', int_literal(4), int_literal(2))))

    def test_parens(self):
        self.assert_ast(
            '3 * (1 + 2)',
            BinaryOperator(
                '*',
                int_literal(3),
                BinaryOperator('+', int_literal(1), int_literal(2))))

    def test_string_concat(self):
        self.assert_ast(
            "'Hello, ' + \"world!\"",
            BinaryOperator(
                '+',
                string_literal('Hello, '),
                string_literal('world!')))


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
