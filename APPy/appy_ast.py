from collections import namedtuple

__author__ = 'alangpierce'

class BinaryOperator(namedtuple('BinaryOperator',
                                ['operator', 'left', 'right'])):
    def pretty_print(self):
        return '(' + self.left.pretty_print() + self.operator +\
               self.right.pretty_print() + ')'

class Literal(namedtuple('Literal', ['value'])):
    def pretty_print(self):
        return str(self.value)

# Currently just an int
class Value(namedtuple('Value', ['value'])):
    pass