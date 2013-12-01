from ply.lex import LexToken
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

    tokens = (
        'INDENT',
        'DEDENT',
        'NEWLINE',
    )

    def __init__(self):
        self.delegate_lexer = LineLexer()

    def tokenize(self, string):
        nesting_level = 0
        assert isinstance(string, str)
        raw_lines = string.split('\n')
        current_lines = []
        for line in raw_lines:
            nesting_level = (nesting_level +
                line.count('(') + line.count('[') + line.count('{') -
                line.count(')') - line.count(']') - line.count('}'))
            if nesting_level > 0:
                current_lines.append(line)
                continue
            if line[-1] == '\\':
                current_lines.append(line[:-1])
                continue
            current_lines.append(line)
            # No reason to continue, so this is the end of the logical line.
            # Make sure
            logical_line = ' '.join(current_lines)
            for token in self.delegate_lexer.tokenize(logical_line):
                yield token
            yield self.create_newline_token()
            del current_lines[:]
        if nesting_level != 0:
            raise SyntaxError('Nonzero ending nesting level: ' + nesting_level)

    def create_newline_token(self):
        token = LexToken()
        token.type = 'NEWLINE'
        token.value = '\n'
        token.lineno = 0
        token.lexpos = 0
        return token
