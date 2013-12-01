from re import match
from ply import lex
from ply.lex import TOKEN, Lexer


class LineLexer(object):
    def __init__(self):
        self.lexer = lex.lex(module=self)

    def tokenize(self, string):
        lexer = lex.lex(module=self)
        self.lexer.input(string)
        while True:
            token = self.lexer.token()
            if token:
                yield token
            else:
                break

    reserved_words = {
        'if': 'IF',
        'True': 'TRUE',
        'False': 'FALSE',
        'and': 'AND',
        'or': 'OR',
        'not': 'NOT',
        'print': 'PRINT',
    }

    tokens = [
        'NUMBER',
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDEDBY',
        'EQUALS',
        'NOTEQUAL',
        'LESSTHAN',
        'GREATERTHAN',
        'LESSTHANOREQUAL',
        'GREATERTHANOREQUAL',
        'LPAREN',
        'RPAREN',
        'ASSIGN',
        'COLON',
        'STRING',
        'ID',
    ] + reserved_words.values()

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDEDBY = r'/'
    t_EQUALS = r'=='
    t_NOTEQUAL = r'!='
    t_LESSTHAN = r'<'
    t_GREATERTHAN = r'>'
    t_LESSTHANOREQUAL = r'<='
    t_GREATERTHANOREQUAL = r'>='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_ASSIGN = r'='
    t_COLON = r':'

    def string_regex(delimiter):
        return ('[uUbB]?[Rr]?' +
                delimiter + '([^' + delimiter + r'\\]|\\.)*' + delimiter)

    @TOKEN(string_regex("'") + '|' + string_regex('"'))
    def t_STRING(self, t):
        code_string = t.value
        delimiter = code_string[-1]
        delim_start = code_string.find(delimiter)
        string_contents = code_string[delim_start + 1:-1]
        prefix = code_string[0:delim_start]
        # TODO: Unicode, bytes
        if not match('[rR]', prefix):
            string_contents = self.escape_string(string_contents)
        t.value = string_contents
        return t

    # Taken from example at http://www.dabeaz.com/ply/ply.html#ply_nn6
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved_words.get(t.value,'ID')
        if t.value == 'True' or t.value == 'False':
            t.value = (t.value == 'True')
        return t

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
    # \uxxxx 	Character with 16-bit hex value xxxx (Unicode only) (1)
    # \Uxxxxxxxx 	Character with 32-bit hex value xxxxxxxx (Unicode only) (2)
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
        for (key, value) in LineLexer.ESCAPE_MAPPINGS:
            string = string.replace('\\' + key, value)
        return string
    t_ignore = ' \t\n'

    def t_error(self, t):
        raise SyntaxError('Unexpected token: ' + str(t))
