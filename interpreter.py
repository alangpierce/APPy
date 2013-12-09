from appy_ast import (Value, ExpressionStatement, PrintStatement, Seq,
                      Assignment, Variable, IfStatement, WhileStatement,
                      DefStatement, FunctionData, FunctionCall)
from builtin_types import TypeContext
from lexer import create_lexer
from parser import Parser
from scope import ScopeChain


class Interpreter(object):
    def __init__(self, stdout_handler):
        self.stdout_handler = stdout_handler
        self.type_context = TypeContext()

    def execute_program(self, program):
        '''
        Executes a program from the top level. Use the stdout_handler
        to capture the output.
        @type program: str
        @param program: Text of program to execute.
        '''
        executor = ExecutionEnvironment(self.stdout_handler, self.type_context)
        ast = self._parse(program, self.type_context)
        executor.execute_statement(ast)

    def evaluate_expression(self, expression):
        '''
        @type expression: str
        @param expression:
        @return: A native Python value corresponding to the evaluated
        value of the expression, which must be a native Python type.
        '''
        executor = ExecutionEnvironment(self.stdout_handler, self.type_context)
        ast = self._parse(expression, self.type_context)
        assert isinstance(ast, ExpressionStatement)
        expr_ast = ast.expr
        return executor.evaluate_expression(expr_ast)

    def _parse(self, program, type_context):
        parser = Parser(type_context)
        lexer = create_lexer()
        return parser.parse(program, lexer)


class ExecutionEnvironment(object):
    """Tracks all state that needs to be tracked during regular
    execution, and contains the implementation of the handlers for the
    various types of expressions and statements.
    """

    def __init__(self, stdout_handler, type_context, scope_chain=None):
        """
        @type type_context: TypeContext
        """
        if scope_chain is None:
            scope_chain = ScopeChain()
        self.stdout_handler = stdout_handler
        self.type_context = type_context
        self.scope_chain = scope_chain

    def execute_statement(self, statement):
        try:
            method = getattr(self, '_execute_' + statement.__class__.__name__)
        except AttributeError:
            raise NotImplementedError(
                'Missing handler for statement ' + str(statement))
        return method(statement)

    def evaluate_expression(self, expression):
        try:
            method = getattr(
                self, '_evaluate_' + expression.__class__.__name__)
        except AttributeError:
            raise NotImplementedError(
                'Missing handler for expression ' + str(expression))
        return method(expression)


    # An "assignable", a.k.a. an lvalue, is an expression that is valid on
    # the left side of an assignment. Assignables are still of type
    # expression, but only some expressions are valid assignables.
    def resolve_assignable(self, expression):
        try:
            method = getattr(self, '_resolve_' + expression.__class__.__name__)
        except AttributeError:
            raise NotImplementedError(
                'Missing handler for assignable ' + str(expression))
        return method(expression)


    def _execute_Seq(self, statement):
        assert isinstance(statement, Seq)
        self.execute_statement(statement.left)
        self.execute_statement(statement.right)


    def _execute_Assignment(self, statement):
        assert isinstance(statement, Assignment)
        value = self.evaluate_expression(statement.right)
        assignable = self.resolve_assignable(statement.left)
        if isinstance(assignable, Variable):
            self.scope_chain.assign_name(assignable.name, value)
        else:
            raise NotImplementedError('Unexpected assignable type: ' +
                                      assignable.__class__.__name__)

    def _execute_ExpressionStatement(self, statement):
        assert isinstance(statement, ExpressionStatement)
        self.evaluate_expression(statement.expr)

    def _execute_PassStatement(self, statement):
        pass

    def _execute_PrintStatement(self, statement):
        assert isinstance(statement, PrintStatement)
        value = self.evaluate_expression(statement.expr)
        self.stdout_handler(str(value.data))

    def _execute_IfStatement(self, statement):
        assert isinstance(statement, IfStatement)
        condition_value = self.evaluate_expression(statement.condition)
        # TODO: This is lame and hides the interesting stuff.
        if condition_value.data:
            self.execute_statement(statement.statement)

    def _execute_WhileStatement(self, statement):
        assert isinstance(statement, WhileStatement)
        while True:
            condition_value = self.evaluate_expression(statement.condition)
            if not condition_value.data:
                break
            self.execute_statement(statement.statement)

    def _execute_DefStatement(self, statement):
        assert isinstance(statement, DefStatement)
        self.scope_chain.assign_name(statement.name, Value(
            self.type_context.function_type,
            FunctionData(
                statement.param_names, statement.body, self.scope_chain),
            {}))

    BINARY_OPERATORS = {
        '+': '__add__',
        '-': '__sub__',
        '*': '__mul__',
        '/': '__floordiv__',
        '==': '__eq__',
        '!=': '__ne__',
        '<': '__lt__',
        '>': '__gt__',
        '<=': '__le__',
        '>=': '__ge__',
        # TODO: short circuit
        'and': '__and__',
        'or': '__or__',
    }

    def _evaluate_BinaryOperator(self, expression):
        op_name = self.BINARY_OPERATORS[expression.operator]
        left_value = self.evaluate_expression(expression.left)
        right_value = self.evaluate_expression(expression.right)
        op_function_value = self._evaluate_attribute(left_value, op_name)
        return self._evaluate_function(
            op_function_value, left_value, right_value)

    def _evaluate_Literal(self, expression):
        return expression.value

    def _evaluate_Variable(self, expression):
        assert isinstance(expression, Variable)
        return self.scope_chain.resolve_name(expression.name)

    def _evaluate_FunctionCall(self, expression):
        assert isinstance(expression, FunctionCall)
        function_value = self.evaluate_expression(expression.function_expr)
        arg_values = [self.evaluate_expression(arg) for arg in expression.args]
        return self._evaluate_function(function_value, *arg_values)

    def _evaluate_attribute(self, object_value, attribute_name):
        """
        Resolves an attribute on the given object, which includes
        checking attributes on the type and supertypes if necessary.
        @type object_value: Value
        @type attribute_name: str
        """
        try:
            return object_value.attributes[attribute_name]
        except KeyError:
            try:
                return object_value.type.attributes[attribute_name]
            except KeyError:
                raise TypeError('Attribute ' + attribute_name +
                                ' does not exist on this type.')

    def _evaluate_function(self, func, *args):
        """
        Given a function value, executes it with the given value
        arguments.
        @type args: should only contain elements of type Value
        @type func: Value
        """
        # Built-in functions use a regular python function.
        # User-defined functions use a FunctionData structure.
        data = func.data
        if isinstance(data, FunctionData):
            new_scope = data.parent_scope.with_pushed_mappings(
                {name: value for (name, value) in zip(data.param_names, args)})
            new_environment = ExecutionEnvironment(
                self.stdout_handler, self.type_context, new_scope)
            # TODO: Return values
            new_environment.execute_statement(data.body)
        else:
            return data(*args)

    def _resolve_Variable(self, expression):
        return expression
