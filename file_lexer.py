from ply.lex import LexToken
import re
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

    tokens = [
        'INDENT',
        'DEDENT',
        'NEWLINE',
    ]

    def __init__(self):
        self.delegate_lexer = LineLexer()

    def tokenize(self, program):
        for logical_line in self._get_logical_lines(program):
            for token in self.delegate_lexer.tokenize(logical_line):
                yield token
            yield self._create_newline_token()

    def _get_logical_lines(self, program):
        nesting_level = 0
        current_lines = []
        for line in program.split('\n'):
            if self._is_line_blank(line):
                continue
            nesting_level += self._get_nesting_difference(line)
            if nesting_level > 0:
                current_lines.append(line)
                continue
            if line[-1] == '\\':
                current_lines.append(line[:-1])
                continue
            current_lines.append(line)
            # No reason to continue, so this is the end of the logical line.
            # Make sure there's at least some whitespace between lines.
            yield ' '.join(current_lines)
            del current_lines[:]
        if nesting_level != 0 or len(current_lines) > 0:
            raise SyntaxError('Unexpected end of file.')

    def _is_line_blank(self, line):
        return re.match(r'^[ \t]*$', line)

    def _get_nesting_difference(self, line):
        """Determines the net number of nesting levels introduced by
        this line.
        """
        return (line.count('(') + line.count('[') + line.count('{') -
                line.count(')') - line.count(']') - line.count('}'))

    def _create_newline_token(self):
        token = LexToken()
        token.type = 'NEWLINE'
        token.value = '\n'
        token.lineno = 0
        token.lexpos = 0
        return token
