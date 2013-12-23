from collections import namedtuple


class Seq(namedtuple('Seq', ['left', 'right'])):
    def pretty_print(self):
        return self.left.pretty_print() + '\n' + self.right.pretty_print()


class Assignment(namedtuple('Assignment', ['left', 'right'])):
    def pretty_print(self):
        return self.left.pretty_print() + ' = ' + self.right.pretty_print()


class ExpressionStatement(namedtuple('ExpressionStatement', ['expr'])):
    def pretty_print(self):
        return self.expr.pretty_print()


class PassStatement(namedtuple('PassStatement', [])):
    def pretty_print(self):
        return 'pass'


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


class ClassStatement(namedtuple('ClassStatement',
                                ['name', 'superclass', 'body'])):
    def pretty_print(self):
        return ('class ' + self.name + '(' + self.superclass.pretty_print() +
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


class ListLiteral(namedtuple('ListLiteral', ['expressions'])):
    def pretty_print(self):
        return ('[' +
                ','.join(expr.pretty_print() for expr in self.expressions) +
                ']')


class Variable(namedtuple('Variable', ['name'])):
    def pretty_print(self):
        return self.name


class FunctionCall(namedtuple('FunctionCall', ['function_expr', 'args'])):
    def pretty_print(self):
        return (self.function_expr.pretty_print() + '(' +
                ','.join(arg.pretty_print() for arg in self.args) + ')')


class AttributeAccess(namedtuple('AttributeAccess', ['expr', 'attr_name'])):
    def pretty_print(self):
        return self.expr.pretty_print() + '.' + self.attr_name


class GetItem(namedtuple('GetItem', ['expr', 'key'])):
    def pretty_print(self):
        return self.expr.pretty_print() + '[' + self.key.pretty_print() + ']'


class Value(namedtuple('Value', ['type', 'data', 'attributes'])):
    """
    * type is a pointer to the type.
    * data refers to the "raw" data contained in this type:
      -primitives have a a Python primitive with their value
      -functions have either an AST of the function (for user-defined
        functions) or a Python function (for builtin functions).
      -types have a string with the name of the type
    * attributes is a dictionary of the direct attributes of the
        object, each of which has type Value.
    """
    def pretty_print(self):
        return str(self.data)


class FunctionData(namedtuple('FunctionData',
                              ['param_names', 'body', 'parent_scope'])):
    pass
