from appy_ast import (Value, ExpressionStatement, PrintStatement, Seq,
                      Assignment, Variable, IfStatement, WhileStatement,
                      DefStatement, FunctionData, FunctionCall, ClassStatement,
                      AttributeAccess, ListLiteral, GetItem)
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
        '''
        @rtype: Value
        '''
        try:
            method = getattr(
                self, '_evaluate_' + expression.__class__.__name__)
        except AttributeError:
            raise NotImplementedError(
                'Missing handler for expression ' + str(expression))
        result = method(expression)
        return result

    def _resolve_assign_function(self, expression):
        """
        An "assignable", a.k.a. an lvalue, is an expression that is
        valid on the left side of an assignment. This method returns a
        function that takes a Value and assigns it to the appropriate
        place.
        @param expression: An assignable expression.
        @rtype Value -> NoneType
        """
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
        assign_function = self._resolve_assign_function(statement.left)
        assign_function(value)

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

    def _execute_ClassStatement(self, statement):
        assert isinstance(statement, ClassStatement)
        # TODO: Use the superclass.
        class_scope = self.scope_chain.with_pushed_mappings({})
        new_environment = ExecutionEnvironment(
            self.stdout_handler, self.type_context, class_scope)
        new_environment.execute_statement(statement.body)
        new_type = Value(self.type_context.type_type, statement.name,
                         class_scope.mappings)
        self.scope_chain.assign_name(statement.name, new_type)

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
        if expression.operator == 'is':
            return self._evaluate_is(expression.left, expression.right)

        op_name = self.BINARY_OPERATORS[expression.operator]
        left_value = self.evaluate_expression(expression.left)
        right_value = self.evaluate_expression(expression.right)
        op_function_value = self._evaluate_attr_on_type(left_value, op_name)
        return self._evaluate_function(op_function_value, right_value)

    def _evaluate_is(self, left, right):
        left_value = self.evaluate_expression(left)
        right_value = self.evaluate_expression(right)
        return self.type_context.bool_value(left_value is right_value)

    def _evaluate_Literal(self, expression):
        return expression.value

    def _evaluate_ListLiteral(self, expression):
        assert isinstance(expression, ListLiteral)
        result_values = [
            self.evaluate_expression(expr) for expr in expression.expressions]
        return Value(self.type_context.list_type, result_values, {})

    def _evaluate_Variable(self, expression):
        assert isinstance(expression, Variable)
        return self.scope_chain.resolve_name(expression.name)

    def _evaluate_FunctionCall(self, expression):
        assert isinstance(expression, FunctionCall)
        function_value = self.evaluate_expression(expression.function_expr)
        arg_values = [self.evaluate_expression(arg) for arg in expression.args]
        return self._evaluate_function(function_value, *arg_values)

    def _evaluate_AttributeAccess(self, expression):
        assert isinstance(expression, AttributeAccess)
        obj = self.evaluate_expression(expression.expr)
        return self._evaluate_attr(obj, expression.attr_name)

    def _evaluate_GetItem(self, expression):
        assert isinstance(expression, GetItem)
        obj_value = self.evaluate_expression(expression.expr)
        method_value = self._evaluate_attr_on_type(obj_value, '__getitem__')
        key_value = self.evaluate_expression(expression.key)
        return self._evaluate_function(method_value, key_value)

    def _evaluate_attr(self, object_value, attribute_name):
        """
        Resolves an attribute on the given object, which includes
        checking attributes on the type and supertypes if necessary.
        @type object_value: Value
        @type attribute_name: str
        """
        try:
            return object_value.attributes[attribute_name]
        except KeyError:
            return self._evaluate_attr_on_type(object_value, attribute_name)

    def _evaluate_attr_on_type(self, object_value, attribute_name):
        try:
            # Functions seem to automatically have __get__, so hard-code
            # that for now.
            # TODO: Full descriptor support
            attr = object_value.type.attributes[attribute_name]
            if attr.type is self.type_context.function_type:
                return self._bind_instance_to_method(object_value, attr)
            else:
                return attr
        except KeyError:
            raise TypeError('Attribute ' + attribute_name +
                            ' does not exist on this type.')

    def _bind_instance_to_method(self, obj, method):
        return Value(
            self.type_context.function_type,
            lambda *args: self._evaluate_function(method, obj, *args),
            {})

    def _evaluate_function(self, func, *args):
        """
        Given a function value, executes it with the given value
        arguments.
        @type args: should only contain elements of type Value
        @type func: Value
        """
        while func.type is not self.type_context.function_type:
            try:
                func = self._evaluate_attr_on_type(func, '__call__')
            except TypeError:
                raise TypeError("'%s' object is not callable" %
                                str(func.type.data))

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

    def _resolve_Variable(self, assignable):
        assert isinstance(assignable, Variable)
        return lambda val: self.scope_chain.assign_name(assignable.name, val)

    def _resolve_AttributeAccess(self, assignable):
        assert isinstance(assignable, AttributeAccess)

        def assign(val):
            obj = self.evaluate_expression(assignable.expr)
            obj.attributes[assignable.attr_name] = val
        return assign

    def _resolve_GetItem(self, assignable):
        assert isinstance(assignable, GetItem)

        def assign(val):
            obj = self.evaluate_expression(assignable.expr)
            method = self._evaluate_attr_on_type(obj, '__setitem__')
            key = self.evaluate_expression(assignable.key)
            self._evaluate_function(method, key, val)
        return assign
