from collections import namedtuple

__author__ = 'alangpierce'

class BinaryOperator(namedtuple('BinaryOperator',
                                ['operator', 'left', 'right'])):
    pass

class Literal(namedtuple('Literal', ['value'])):
    pass

# Currently just an int
class Value(namedtuple('Value', ['value'])):
    pass