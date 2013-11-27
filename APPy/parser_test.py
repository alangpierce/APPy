import unittest
from appy_ast import BinaryOperator, Literal
from parser import create_parser


class ParserTest(unittest.TestCase):
    def test_something(self):
        input_string = '5 + 3'
        self.assert_ast(BinaryOperator('+', Literal(5), Literal(3)),
                        input_string)

    def assert_ast(self, expected_ast, program):
        ast = self.get_ast(program)

    def get_ast(self, program):
        parser = create_parser()
        return parser.parse(program)


if __name__ == '__main__':
    unittest.main()
