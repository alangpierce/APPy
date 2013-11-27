import unittest

from appy_ast import BinaryOperator, Literal
from lexer import create_lexer
from parser import create_parser

class ParserTest(unittest.TestCase):
    def test_basic_parsing(self):
        input_string = '5 + 3'
        self.assertEqual(BinaryOperator('+', Literal(5), Literal(3)),
                         self.get_ast(input_string))

    def get_ast(self, program):
        parser = create_parser()
        lexer = create_lexer()
        return parser.parse(program, lexer)


if __name__ == '__main__':
    unittest.main()
