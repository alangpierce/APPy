import unittest
from lexer import create_lexer

def num(n):
    return ('NUMBER', n)
plus = ('PLUS', '+')
minus = ('MINUS', '-')
times = ('TIMES', '*')
dividedby = ('DIVIDEDBY', '/')
lparen = ('LPAREN', '(')
rparen = ('RPAREN', ')')
def string(s):
    return ('STRING', s)

class LexerTest(unittest.TestCase):
    def test_simple_tokens(self):
        self.assert_tokens(
            '5 + 3',
            [num(5), plus, num(3)])

    def test_operators(self):
        self.assert_tokens(
            '1 + 2 - 3 * 4 / 5',
            [num(1), plus, num(2), minus, num(3), times, num(4), dividedby,
             num(5)])

    def test_parens(self):
        self.assert_tokens(
            '3*(5 + 5)',
            [num(3), times, lparen, num(5), plus, num(5), rparen])

    def test_single_quote_string_literal(self):
        self.assert_tokens(
            "'Hello, ' + 'world!'",
            [string('Hello, '), plus, string('world!')])

    def test_single_quote_escapes(self):
        self.assert_tokens(
            r"'abc\''",
            [string("abc'")])

    def test_mismatched_quote(self):
        self.assert_lex_failure("'''")

    def test_double_quite_string_literal(self):
        self.assert_tokens(
            '"Hello, " + "world" + \'!\'',
            [string('Hello, '), plus, string('world'), plus, string('!')])

    def test_raw_strings(self):
        self.assert_tokens(
            r'r"abc\n"',
            [string(r'abc\n')])

    def assert_tokens(self, program, expected_tokens):
        tokens = self.get_tokens(program)
        self.assertEqual(expected_tokens,
                         [(tok.type, tok.value) for tok in tokens])

    def assert_lex_failure(self, program):
        self.assertRaises(SyntaxError, self.get_tokens, program)

    def get_tokens(self, input):
        lexer = create_lexer()
        lexer.input(input)
        result = []
        while True:
            token = lexer.token()
            if not token:
                break
            result.append(token)
        return result


if __name__ == '__main__':
    unittest.main()
