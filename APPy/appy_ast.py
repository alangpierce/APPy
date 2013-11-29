from collections import namedtuple

__author__ = 'alangpierce'


class BinaryOperator(namedtuple('BinaryOperator',
                                ['operator', 'left', 'right'])):
    def pretty_print(self):
        return '(' + self.left.pretty_print() + self.operator + \
               self.right.pretty_print() + ')'


# value is of type Value
class Literal(namedtuple('Literal', ['value'])):
    def pretty_print(self):
        return str(self.value)

# type is one of 'string' or 'int'
# value is a python representation of that value
class Value(namedtuple('Value', ['type', 'value'])):
    def pretty_print(self):
        return str(self.value)
