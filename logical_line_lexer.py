from ply.lex import Lexer


class LogicalLineLexer:
    """Wrapper lexer that has two responsibilities:
    -Define the logical lines of a python file
    -Determine the indentation for each line and emit INDENT and DEDENT
    tokens

    This logic technically could be handled directly in the PLY lexer
    using some combination of lexer states, custom lexer fields, and
    special case handlers for the different whitespace characters, but
    this approach splits the responsibilities up in a cleaner way.
    """

    def __init__(self, delegate_lexer):
        assert isinstance(delegate_lexer, Lexer)
        self.delegate_lexer = delegate_lexer

    def token(self):
        return self.delegate_lexer.token()

    def input(self, string):
        self.delegate_lexer.input(string)
