from file_lexer import FileLexer
from line_lexer import LineLexer


class PlyLexerAdapter:
    '''PLY uses a weird lexer interface with an input() method to
    specify the string and a token() method to advance state and return
    the next token. Since this interface is kind of hard to work with,
    we have a tokenize(str) method that returns a generator, and build
    a PLY-style lexer from that.
    '''

    def __init__(self, delegate_lexer):
        self.string = None
        self.delegate_lexer = delegate_lexer
        self.generator = None

    def input(self, string):
        self.generator = self.delegate_lexer.tokenize(string)

    def token(self):
        try:
            return self.generator.next()
        except StopIteration:
            return None


def create_lexer():
    return PlyLexerAdapter(FileLexer())

tokens = FileLexer.tokens + LineLexer.tokens
