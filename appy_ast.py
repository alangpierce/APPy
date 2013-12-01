from collections import namedtuple


class Seq(namedtuple('Seq', ['left', 'right'])):
    pass


class Assignment(namedtuple('Assignment', ['left', 'right'])):
    def pretty_print(self):
        return self.left.pretty_print() + ' = ' + self.right.pretty_print()


class ExpressionStatement(namedtuple('ExpressionStatement', ['expr'])):
    def pretty_print(self):
        return self.expr.pretty_print()


class PrintStatement(namedtuple('PrintStatement', ['expr'])):
    def pretty_print(self):
        return 'print ' + self.expr.pretty_print()


class IfStatement(namedtuple('IfStatement', ['condition', 'statement'])):
    def pretty_print(self):
        return 'if ' + self.condition.pretty_print() + ':\n\t' +\
               self.statement.pretty_print()


class BinaryOperator(namedtuple('BinaryOperator',
                                ['operator', 'left', 'right'])):
    def pretty_print(self):
        return ('(' + self.left.pretty_print() + ' ' + self.operator + ' ' +
                self.right.pretty_print() + ')')


# value is of type Value
class Literal(namedtuple('Literal', ['value'])):
    def pretty_print(self):
        return self.value.pretty_print()


class Variable(namedtuple('Variable', ['name'])):
    def pretty_print(self):
        return self.name


# type is one of 'string' or 'int'
# value is a python representation of that value
class Value(namedtuple('Value', ['type', 'value'])):
    def pretty_print(self):
        return str(self.value)
