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

    # Handle indentation as described by
    # http://docs.python.org/2/reference/lexical_analysis.html#indentation
    def tokenize(self, program):
        indentation_levels = [0]
        for logical_line in self._get_logical_lines(program):
            indentation_level = self._get_indentation_level(logical_line)
            if indentation_level > indentation_levels[-1]:
                yield self._create_token('INDENT')
                indentation_levels.append(indentation_level)
            elif indentation_level < indentation_levels[-1]:
                while indentation_level < indentation_levels[-1]:
                    yield self._create_token('DEDENT')
                    indentation_levels.pop()
                if indentation_level != indentation_levels[-1]:
                    raise SyntaxError(
                        'Cannot dedent to a level not previously given.')

            for token in self.delegate_lexer.tokenize(logical_line):
                yield token
            yield self._create_token('NEWLINE')
        while indentation_levels[-1] > 0:
            yield self._create_token('DEDENT')
            indentation_levels.pop()

    # Gets the number of "spaces" at the start of the given line, accounting
    # for tab characters.
    def _get_indentation_level(self, logical_line):
        current_level = 0
        for char in logical_line:
            if char == ' ':
                current_level += 1
            elif char == '\t':
                current_level = self._round_up(current_level, 8)
            else:
                break
        return current_level

    def _round_up(self, number, mod):
        return number + (-number % mod)

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

    # Creates a token with the given type and no value.
    def _create_token(self, type):
        token = LexToken()
        token.type = type
        token.value = ''
        token.lineno = 0
        token.lexpos = 0
        return token
