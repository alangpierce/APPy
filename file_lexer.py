from ply.lex import Lexer
from line_lexer import LineLexer


class FileLexer(object):
    """Wrapper lexer that has two responsibilities:
    -Define the logical lines of a python file
    -Determine the indentation for each line and emit INDENT and DEDENT
    tokens

    This logic technically could be handled directly in the PLY lexer
    using some combination of lexer states, custom lexer fields, and
    special case handlers for the different whitespace characters, but
    this approach splits the responsibilities up in a cleaner way.
    """

    def __init__(self):
        self.delegate_lexer = LineLexer()

    def tokenize(self, string):
        return self.delegate_lexer.tokenize(string)
