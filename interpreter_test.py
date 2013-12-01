import unittest

from appy_ast import Value
from interpreter import evaluate_expression
from lexer import create_lexer
from parser import create_parser

def int_value(int_val):
    return Value('int', int_val)

def string_value(string_val):
    return Value('str', string_val)

def bool_value(bool_val):
    return Value('bool', bool_val)

class InterpreterTest(unittest.TestCase):

    def test_basic_interpreter(self):
        self.assert_evaluate('5 + 3', int_value(8))

    def test_order_of_operations(self):
        self.assert_evaluate('1 + 2 * 3', int_value(7))

    def test_parens(self):
        self.assert_evaluate('5 / (1 + 1)', int_value(2))

    def test_string_concat(self):
        self.assert_evaluate('"hello" + "world"', string_value('helloworld'))

    def test_string_subtract_is_illegal(self):
        self.assert_type_error('"hello" - "world"')

    def test_string_multiply_right(self):
        self.assert_evaluate('"hello" * 3', string_value('hellohellohello'))

    def test_string_multiply_left(self):
        self.assert_evaluate('2 * "hello"', string_value('hellohello'))

    def test_boolean_operators(self):
        self.assert_evaluate('True or False and True', bool_value(True))

    def test_comparisons(self):
        self.assert_evaluate('5 == 5 and 3 < 5 and 1 != 2', bool_value(True))
        self.assert_evaluate('1 > 3 or 100 <= 10', bool_value(False))

    def assert_evaluate(self, program, expected_value):
        ast = self.get_ast(program)
        self.assertEqual(expected_value, evaluate_expression(ast))

    def assert_type_error(self, program):
        ast = self.get_ast(program)
        self.assertRaises(TypeError, evaluate_expression, ast)

    def get_ast(self, program):
        parser = create_parser()
        lexer = create_lexer()
        return parser.parse(program, lexer)

if __name__ == '__main__':
    unittest.main()
