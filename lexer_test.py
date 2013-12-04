import unittest
from file_lexer import FileLexer
from lexer import create_lexer


def num(n):
    return ('NUMBER', n)
def ident(s):
    return ('ID', s)
plus = ('PLUS', '+')
minus = ('MINUS', '-')
times = ('TIMES', '*')
dividedby = ('DIVIDEDBY', '/')
equals = ('EQUALS', '==')
assign = ('ASSIGN', '=')
lparen = ('LPAREN', '(')
rparen = ('RPAREN', ')')
def string(s):
    return ('STRING', s)
if_token = ('IF', 'if')
while_token = ('WHILE', 'while')
colon = ('COLON', ':')
comma = ('COMMA', ',')
newline = ('NEWLINE', '')
indent = ('INDENT', '')
dedent = ('DEDENT', '')
print_token = ('PRINT', 'print')
def_token = ('DEF', 'def')

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

    def test_if(self):
        self.assert_tokens(
            'if 1 + 1:\n'
            '    2 + 3',
            [if_token, num(1), plus, num(1), colon, newline, indent, num(2),
             plus, num(3), newline, dedent])

    def test_while(self):
        self.assert_tokens(
            'while x == 5:\n'
            '    print x',
            [while_token, ident('x'), equals, num(5), colon, newline, indent,
             print_token, ident('x'), newline, dedent])

    def test_identifier(self):
        self.assert_tokens('x + 5', [ident('x'), plus, num(5), newline])

    def test_conflicting_identifiers(self):
        self.assert_tokens(
            'iframe + r',
            [ident('iframe'), plus, ident('r'), newline])

    def test_print(self):
        self.assert_tokens(
            'print "Hello"',
            [print_token, string('Hello'), newline])

    def test_function_def(self):
        self.assert_tokens(
            '''
def blah(a, b, c):
    x = 5''',
            [def_token, ident('blah'), lparen, ident('a'), comma, ident('b'),
             comma, ident('c'), rparen, colon, newline, indent, ident('x'),
             assign, num(5), newline, dedent]
        )

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
