import unittest

from appy_ast import Value
from interpreter import evaluate_expression
from lexer import create_lexer
from parser import create_parser

class InterpreterTest(unittest.TestCase):
    def test_basic_interpreter(self):
        program = '5 + 3'
        program_expr = self.get_ast(program)
        self.assertEqual(Value(8), evaluate_expression(program_expr))

    def get_ast(self, program):
        parser = create_parser()
        lexer = create_lexer()
        return parser.parse(program)

if __name__ == '__main__':
    unittest.main()
