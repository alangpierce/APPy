import unittest
from lexer import create_lexer

class LexerTest(unittest.TestCase):
    def test_simple_tokens(self):
        input_string = '5 + 3'
        tokens = self.get_tokens(input_string)
        self.assert_tokens(
            [('NUMBER', 5),
             ('PLUS', '+'),
             ('NUMBER', 3)],
            input_string)

    def assert_tokens(self, expected_tokens, program):
        tokens = self.get_tokens(program)
        self.assertEqual(expected_tokens,
                         [(tok.type, tok.value) for tok in tokens])

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
