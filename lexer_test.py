import unittest
from file_lexer import FileLexer
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
newline = ('NEWLINE', '\n')

class LexerTest(unittest.TestCase):
    def test_simple_tokens(self):
        self.assert_tokens(
            '5 + 3',
            [num(5), plus, num(3), newline])

    def test_operators(self):
        self.assert_tokens(
            '1 + 2 - 3 * 4 / 5',
            [num(1), plus, num(2), minus, num(3), times, num(4), dividedby,
             num(5), newline])

    def test_parens(self):
        self.assert_tokens(
            '3*(5 + 5)',
            [num(3), times, lparen, num(5), plus, num(5), rparen, newline])

    def test_single_quote_string_literal(self):
        self.assert_tokens(
            "'Hello, ' + 'world!'",
            [string('Hello, '), plus, string('world!'), newline])

    def test_single_quote_escapes(self):
        self.assert_tokens(
            r"'abc\''",
            [string("abc'"), newline])

    def test_mismatched_quote(self):
        self.assert_lex_failure("'''")

    def test_double_quite_string_literal(self):
        self.assert_tokens(
            '"Hello, " + "world" + \'!\'',
            [string('Hello, '), plus, string('world'), plus, string('!'),
             newline])

    def test_raw_strings(self):
        self.assert_tokens(
            r'r"abc\n"',
            [string(r'abc\n'), newline])

    def test_newline(self):
        self.assert_tokens(
            '5 + 5\n' +
            '1 + 2',
            [num(5), plus, num(5), newline, num(1), plus, num(2), newline])

    def test_newline_inside_parens(self):
        self.assert_tokens(
            '(5 + 5\n' +
            '1 + 2)',
            [lparen, num(5), plus, num(5), num(1), plus, num(2), rparen,
             newline])

    def test_escaped_newline(self):
        self.assert_tokens(
            '5 + 5\\\n' +
            '1 + 2',
            [num(5), plus, num(5), num(1), plus, num(2), newline])

    def test_empty_lines_ignored(self):
        self.assert_tokens(
            '1\n \t\n2',
            [num(1), newline, num(2), newline])

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
