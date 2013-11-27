from ply import lex

class AppyLexer:
    def __init__(self):
        pass

    tokens = (
        'NUMBER',
        'PLUS',
    )

    t_PLUS = r'\+'

    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %d", t.value)
            t.value = 0
        return t

    t_ignore = ' \t\n'

    def t_error(self, t):
        raise SyntaxError('Unexpected token: ' + str(t))


def create_lexer():
    return lex.lex(module=AppyLexer())

