from re import match
from ply import lex
from ply.lex import TOKEN, Lexer


class LineLexer(object):
    def tokenize(self, string):
        return LineLexerInstance().tokenize(string)


class LineLexerInstance(object):
    def __init__(self):
        self.paren_nesting_level = 0
        self.brace_nesting_level = 0
        self.bracket_nesting_level = 0
        self.lexer = lex.lex(module=self)

    def tokenize(self, string):
        self.lexer.input(string)
        while True:
            token = self.lexer.token()
            if token:
                yield token
            else:
                break

    tokens = (
        'NUMBER',
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDEDBY',
        'LPAREN',
        'RPAREN',
        'STRING',
        'NEWLINE',
    )

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDEDBY = r'/'

    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %d", t.value)
            t.value = 0
        return t

    # Key-value pairs of all escape characters. Each key has an implicit
    # backslash before it.
    # TODO: Implement the following from the spec:
    # \N{name} 	Character named name in the Unicode database (Unicode only)
    # \uxxxx 	Character with 16-bit hex value xxxx (Unicode only) 	(1)
    # \Uxxxxxxxx 	Character with 32-bit hex value xxxxxxxx (Unicode only) 	(2)
    # \ooo 	Character with octal value ooo 	(3,5)
    # \xhh 	Character with hex value hh 	(4,5)
    ESCAPE_MAPPINGS = [
        ('\n', ''),
        ('\\', '\\'),
        ("'", "'"),
        ('"', '"'),
        ('a', '\a'),
        ('b', '\b'),
        ('f', '\f'),
        ('n', '\n'),
        ('r', '\r'),
        ('t', '\t'),
        ('v', '\v'),
    ]

    def escape_string(self, string):
        for (key, value) in LineLexerInstance.ESCAPE_MAPPINGS:
            string = string.replace('\\' + key, value)
        return string

    def string_regex(delimiter):
        return ('[uUbB]?[Rr]?' +
                delimiter + '([^' + delimiter + r'\\]|\\.)*' + delimiter)

    @TOKEN(string_regex("'") + '|' + string_regex('"'))
    def t_STRING(self, t):
        origin_string = t.value
        delimiter = origin_string[-1]
        delim_start = origin_string.find(delimiter)
        string_contents = origin_string[delim_start + 1:-1]
        prefix = origin_string[0:delim_start]
        # TODO: Unicode, bytes
        if not match('[rR]', prefix):
            string_contents = self.escape_string(string_contents)
        t.value = string_contents
        return t

    def t_LPAREN(self, t):
        r'\('
        self.paren_nesting_level += 1
        return t

    def t_RPAREN(self, t):
        r'\)'
        if self.paren_nesting_level <= 0:
            raise SyntaxError("Unmatched ')'")
        self.paren_nesting_level -= 1
        return t

    def t_NEWLINE(self, t):
        r'\n'
        if (self.paren_nesting_level == 0 and
                    self.bracket_nesting_level == 0 and
                    self.brace_nesting_level == 0):
            return t
            # else ignore the token

    t_ignore_ESCAPED_NEWLINE = r'\\\n'

    t_ignore = ' \t'

    def t_error(self, t):
        raise SyntaxError('Unexpected token: ' + str(t))
