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
        return ('if ' + self.condition.pretty_print() + ':\n\t' +
                self.statement.pretty_print())


class WhileStatement(namedtuple('WhileStatement', ['condition', 'statement'])):
    def pretty_print(self):
        return ('while ' + self.condition.pretty_print() + ':\n\t' +
                self.statement.pretty_print())


class DefStatement(namedtuple('DefStatement',
                              ['name', 'param_names', 'body'])):
    """
    param_names is a list of strings for the parameter names.
    body is any statement.
    """
    def pretty_print(self):
        return ('def ' + self.name + '(' + ','.join(self.param_names) +
                '):\n\t' + self.body.pretty_print())


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


class FunctionCall(namedtuple('FunctionCall', ['function_expr', 'args'])):
    def pretty_print(self):
        return (self.function_expr.pretty_print() + '(' +
                ','.join(arg.pretty_print() for arg in self.args) + ')')


class Value(namedtuple('Value', ['type', 'data', 'attributes'])):
    """
    * type is a pointer to the type.
    * data refers to the "raw" data contained in this type, such as an
    int, string, or AST. Only primitive-like objects have a value here.
    * attributes is a dictionary of the direct attributes of the object.
    """
    def pretty_print(self):
        return str(self.data)
