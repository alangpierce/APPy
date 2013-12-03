import unittest

from appy_ast import BinaryOperator, Literal, Value, ExpressionStatement, PrintStatement, IfStatement, Assignment, Variable, WhileStatement
from lexer import create_lexer
from parser import Parser


def int_literal(int_value):
    return Literal(Value('int', int_value, {}))


def string_literal(string_value):
    return Literal(Value('str', string_value, {}))


def bool_literal(bool_value):
    return Literal(Value('bool', bool_value, {}))


class ParserTest(unittest.TestCase):
    def test_basic_parsing(self):
        self.assert_ast_expression(
            '5 + 3',
            BinaryOperator('+', int_literal(5), int_literal(3)))

    def test_operator_precedence(self):
        self.assert_ast_expression(
            '1*2 + 5*6 - 4/2',
            BinaryOperator(
                '-',
                BinaryOperator(
                    '+',
                    BinaryOperator('*', int_literal(1), int_literal(2)),
                    BinaryOperator('*', int_literal(5), int_literal(6))),
                BinaryOperator('/', int_literal(4), int_literal(2))))

    def test_parens(self):
        self.assert_ast_expression(
            '3 * (1 + 2)',
            BinaryOperator(
                '*',
                int_literal(3),
                BinaryOperator('+', int_literal(1), int_literal(2))))

    def test_string_concat(self):
        self.assert_ast_expression(
            "'Hello, ' + \"world!\"",
            BinaryOperator(
                '+',
                string_literal('Hello, '),
                string_literal('world!')))

    def test_boolean_expression(self):
        self.assert_ast_expression(
            'True or False and True',
            BinaryOperator(
                'or',
                bool_literal(True),
                BinaryOperator(
                    'and',
                    bool_literal(False),
                    bool_literal(True))))

    def test_comparisons(self):
        self.assert_ast_expression(
            '1 == 2',
            BinaryOperator('==', int_literal(1), int_literal(2)))
        self.assert_ast_expression(
            '1 < 2',
            BinaryOperator('<', int_literal(1), int_literal(2)))
        self.assert_ast_expression(
            '1 > 2',
            BinaryOperator('>', int_literal(1), int_literal(2)))
        self.assert_ast_expression(
            '1 <= 2',
            BinaryOperator('<=', int_literal(1), int_literal(2)))
        self.assert_ast_expression(
            '1 >= 2',
            BinaryOperator('>=', int_literal(1), int_literal(2)))

    def test_print(self):
        self.assert_ast(
            'print "Hello"',
            PrintStatement(string_literal('Hello')))

    def test_if(self):
        self.assert_ast(
            '''
if True:
    x = 5''',
            IfStatement(bool_literal(True),
                        Assignment(Variable('x'), int_literal(5)))
        )

    def test_while(self):
        self.assert_ast(
            '''
while False:
    print "Banana"''',
            WhileStatement(
                bool_literal(False),
                PrintStatement(string_literal('Banana'))))

    def assert_ast(self, program, expected_ast):
        actual_ast = self.get_ast(program)
        self.assertEqual(expected_ast, actual_ast,
                         "Expected: " + expected_ast.pretty_print() +
                         ", Actual: " + actual_ast.pretty_print(), )

    def assert_ast_expression(self, program, expected_ast_expression):
        self.assert_ast(program, ExpressionStatement(expected_ast_expression))

    def get_ast(self, program):
        parser = Parser()
        lexer = create_lexer()
        return parser.parse(program, lexer)


if __name__ == '__main__':
    unittest.main()
