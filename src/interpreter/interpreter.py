from typing import Optional, Any, List
from src.ast.visitor import Visitor
import src.ast.ast_nodes as nodes
from .environment import (
    Environment,
    RuntimeError,
    NameError,
    TypeError,
    ValueError,
    ArgumentError,
    LimitError,
)


# Interpreter


class Interpreter(Visitor):
    def __init__(self) -> None:
        self.environment = (
            Environment()
        )  # przydatne przy wywołaniach funkcji gdzie nie chcemy przesłaniać zmiennych
        self._build_builtins()
        self.last_result: Any = None

    MAX_INT = 2147483647
    MIN_INT = -2147483648
    MAX_FLOAT = 1e308
    MIN_FLOAT = -1e308
    DIVISOR = 1e-10

    def _build_builtins(self) -> None:
        builtins = [
            nodes.BuiltinFunction("print", self._builtin_print),
            nodes.BuiltinFunction("println", self._builtin_println),
            nodes.BuiltinFunction("input", self._builtin_input),
            nodes.BuiltinFunction("typeof", self._builtin_typeof),
        ]

        for func in builtins:
            self.environment.define_function(func.name, func)

    def _builtin_print(self, *args: Any) -> None:
        for arg in args:
            if arg is None:
                raise RuntimeError("Cannot print void value", None)
        print(*args, end="")
        return None

    def _builtin_println(self, *args: Any) -> None:
        for arg in args:
            if arg is None:
                raise RuntimeError("Cannot print void value", None)
        print(*args)
        return None

    def _builtin_input(self) -> str:
        return input()

    def _builtin_typeof(self, value: Any) -> str:
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        else:
            return "unknown"

    def consume(self) -> Any:
        result = self.last_result
        self.last_result = None
        return result

    def _check_same_types(
        self, left: Any, right: Any, operator: str, location: nodes.SourceLocation
    ) -> None:
        if type(left) is not type(right):
            raise TypeError(
                f"Cannot perform '{operator}' on {type(left).__name__} and {type(right).__name__}. "
                f"Types must match exactly",
                location,
            )

    def _check_numeric(
        self, value: Any, operator: str, location: nodes.SourceLocation
    ) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(
                f"Operator '{operator}' requires numeric type, got {type(value).__name__}",
                location,
            )

    def _check_numeric_limits(self, value: Any, location: nodes.SourceLocation) -> Any:
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            if value > self.MAX_INT or value < self.MIN_INT:
                raise ValueError(f"Integer overflow: {value}", location)
        elif isinstance(value, float):
            if value > self.MAX_FLOAT or value < self.MIN_FLOAT:
                raise ValueError(f"Float overflow: {value}", location)
        return value

    def _check_divisor(self, value: Any, location: nodes.SourceLocation) -> None:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if abs(value) < self.DIVISOR:
                raise ValueError(f"Division by near zero value: {value}", location)

    def _check_bool(
        self, value: Any, context: str, location: nodes.SourceLocation
    ) -> None:
        if not isinstance(value, bool):
            raise TypeError(
                f"{context} must be bool, got {type(value).__name__}", location
            )

    def interpret(self, node: nodes.ASTNode) -> Any:
        try:
            node.accept(self)
            return self.last_result
        except LimitError as e:
            raise RuntimeError(str(e), None)

    def visit_Program(self, node: nodes.Program) -> None:
        for func_def in node.functions:
            if self.environment.has_function(func_def.name):
                existing = self.environment.get_function(func_def.name)
                if isinstance(existing, nodes.BuiltinFunction):
                    raise RuntimeError(
                        f"Cannot redefine builtin function '{func_def.name}'",
                        func_def.location,
                    )
            self.environment.define_function(func_def.name, func_def)

    def visit_BuiltinFunction(self, node: nodes.BuiltinFunction) -> None:
        self.last_result = node.call(*self.environment.get_args())

    def visit_FunctionDefinition(self, node: nodes.FunctionDefinition) -> None:
        args = self.environment.get_args()

        if node.body is not None:
            if len(args) != len(node.params):
                raise ArgumentError(
                    f"Function '{node.name}' expects {len(node.params)} arguments, got {len(args)}",
                    node.location,
                )

            for param_name, arg_value in zip(node.params, args):
                self.environment.define(param_name, arg_value)

            node.body.accept(self)

            self.last_result = self.environment.get_return_value()

    def visit_FunctionCall(self, node: nodes.FunctionCall) -> None:
        if (func := self.environment.get_function(node.name)) is None:
            raise NameError(f"Function {node.name} not defined", node.location)

        args = []
        for arg_expression in node.arguments:
            arg_expression.accept(self)
            args.append(self.consume())

        self.environment.enter_function(args, node.name, node.location)

        func.accept(self)

        self.environment.exit_function()

    def visit_FunctionCallStatement(self, node: nodes.FunctionCallStatement) -> None:
        call_node = nodes.FunctionCall(node.name, node.arguments, node.location)
        call_node.accept(self)

    def visit_ReturnStatement(self, node: nodes.ReturnStatement) -> None:
        if self.environment.depth() == 0:
            raise RuntimeError("'return' outside of function", node.location)

        if node.expression:
            node.expression.accept(self)
            value = self.consume()
        else:
            value = None

        self.environment.on_return(value)

    def visit_IntLiteral(self, node: nodes.IntLiteral) -> None:
        self.last_result = node.value

    def visit_FloatLiteral(self, node: nodes.FloatLiteral) -> None:
        self.last_result = node.value

    def visit_StringLiteral(self, node: nodes.StringLiteral) -> None:
        self.last_result = node.value

    def visit_BoolLiteral(self, node: nodes.BoolLiteral) -> None:
        self.last_result = node.value

    def visit_Variable(self, node: nodes.Variable) -> None:
        try:
            self.last_result = self.environment.get(node.name)
        except Exception:
            raise NameError(f"Undefined variable '{node.name}", node.location)

    def visit_AssignmentStatement(self, node: nodes.AssignmentStatement) -> None:
        node.expression.accept(self)
        value = self.consume()

        self.environment.define_or_assign(node.variable_name, value)

    def visit_AddExpression(self, node: nodes.AddExpression) -> None:
        node.left.accept(self)
        left = self.consume()
        node.right.accept(self)
        right = self.consume()

        self._check_same_types(left, right, "+", node.location)

        if isinstance(left, str):
            self.last_result = left + right
            return

        self._check_numeric(left, "+", node.location)

        result = left + right
        self.last_result = self._check_numeric_limits(result, node.location)

    def visit_SubtractExpression(self, node: nodes.SubtractExpression) -> None:
        node.left.accept(self)
        left = self.consume()
        node.right.accept(self)
        right = self.consume()

        self._check_same_types(left, right, "-", node.location)
        self._check_numeric(left, "-", node.location)

        result = left - right
        self.last_result = self._check_numeric_limits(result, node.location)

    def visit_MultiplyExpression(self, node: nodes.MultiplyExpression) -> None:
        node.left.accept(self)
        left = self.consume()
        node.right.accept(self)
        right = self.consume()

        self._check_same_types(left, right, "*", node.location)
        self._check_numeric(left, "*", node.location)

        result = left * right
        self.last_result = self._check_numeric_limits(result, node.location)

    def visit_DivideExpression(self, node: nodes.DivideExpression) -> None:
        node.left.accept(self)
        left = self.consume()
        node.right.accept(self)
        right = self.consume()

        self._check_same_types(left, right, "/", node.location)
        self._check_numeric(left, "/", node.location)

        self._check_divisor(right, node.location)
        result = left / right
        self.last_result = self._check_numeric_limits(result, node.location)

    def visit_UnaryMinusExpression(self, node: nodes.UnaryMinusExpression) -> None:
        node.operand.accept(self)
        value = self.consume()

        self._check_numeric(value, "unary -", node.location)

        self.last_result = -value

    def visit_EqualExpression(self, node: nodes.EqualExpression) -> None:
        node.left.accept(self)
        left = self.consume()
        node.right.accept(self)
        right = self.consume()

        self._check_same_types(left, right, "==", node.location)

        self.last_result = left == right

    def visit_NotEqualExpression(self, node: nodes.NotEqualExpression) -> None:
        node.left.accept(self)
        left = self.consume()
        node.right.accept(self)
        right = self.consume()

        self._check_same_types(left, right, "!=", node.location)

        self.last_result = left != right

    def visit_LessExpression(self, node: nodes.LessExpression) -> None:
        node.left.accept(self)
        left = self.consume()
        node.right.accept(self)
        right = self.consume()

        self._check_same_types(left, right, "<", node.location)
        self._check_numeric(left, "<", node.location)

        self.last_result = left < right

    def visit_LessEqualExpression(self, node: nodes.LessEqualExpression) -> None:
        node.left.accept(self)
        left = self.consume()
        node.right.accept(self)
        right = self.consume()

        self._check_same_types(left, right, "<=", node.location)
        self._check_numeric(left, "<=", node.location)

        self.last_result = left <= right

    def visit_GreaterExpression(self, node: nodes.GreaterExpression) -> None:
        node.left.accept(self)
        left = self.consume()
        node.right.accept(self)
        right = self.consume()

        self._check_same_types(left, right, ">", node.location)
        self._check_numeric(left, ">", node.location)

        self.last_result = left > right

    def visit_GreaterEqualExpression(self, node: nodes.GreaterEqualExpression) -> None:
        node.left.accept(self)
        left = self.consume()
        node.right.accept(self)
        right = self.consume()

        self._check_same_types(left, right, ">=", node.location)
        self._check_numeric(left, ">=", node.location)

        self.last_result = left >= right

    # operatory logiczne

    def visit_AndExpression(self, node: nodes.AndExpression) -> None:
        node.left.accept(self)
        left = self.consume()

        self._check_bool(left, "Left operand of 'and'", node.location)

        if not left:
            self.last_result = False
            return

        node.right.accept(self)
        right = self.consume()

        self._check_bool(right, "Right operand of 'and'", node.location)

        self.last_result = right

    def visit_OrExpression(self, node: nodes.OrExpression) -> None:
        node.left.accept(self)
        left = self.consume()

        self._check_bool(left, "Left operand of 'or'", node.location)

        if left:
            self.last_result = True
            return

        node.right.accept(self)
        right = self.consume()

        self._check_bool(right, "Right operand of 'or'", node.location)

        self.last_result = right

    def visit_NotExpression(self, node: nodes.NotExpression) -> None:
        node.operand.accept(self)
        value = self.consume()

        self._check_bool(value, "Operand of '!'", node.location)

        self.last_result = not value

    def visit_Block(self, node: nodes.Block) -> None:
        self.environment.enter_block()

        for statement in node.statements:
            statement.accept(self)
            if self.environment.should_interrupt():
                break
        self.environment.exit_block()

    def visit_IfStatement(self, node: nodes.IfStatement) -> None:
        node.condition.accept(self)
        condition = self.consume()

        self._check_bool(condition, "If condition", node.location)

        if condition:
            node.then_branch.accept(self)
        elif node.else_branch:
            node.else_branch.accept(self)

    def visit_WhileStatement(self, node: nodes.WhileStatement) -> None:
        node.condition.accept(self)
        self._check_bool(self.last_result, "While condition", node.location)

        while self.last_result:
            self.environment.enter_loop()
            node.body.accept(self)

            if self.environment.should_break() or self.environment.should_return():
                self.environment.current_context().exit_loop()
                break

            self.environment.exit_loop()

            node.condition.accept(self)
            self._check_bool(self.last_result, "While condition", node.location)

    def visit_BreakStatement(self, node: nodes.BreakStatement) -> None:
        if not self.environment.is_in_loop():
            raise RuntimeError("'break' outside of loop", node.location)
        self.environment.on_break()

    def visit_ContinueStatement(self, node: nodes.ContinueStatement) -> None:
        if not self.environment.is_in_loop():
            raise RuntimeError("'continue' outside of loop", node.location)
        self.environment.on_continue()

    def visit_MatchStatement(self, node: nodes.MatchStatement) -> None:
        subjects_with_aliases = []
        for expr, alias in node.subjects:
            expr.accept(self)
            value = self.consume()
            subjects_with_aliases.append((value, alias))

        self.environment.enter_match(subjects_with_aliases)

        matched_any = False

        for case in node.cases:
            case.accept(self)

            if self.consume():
                matched_any = True
                case.body.accept(self)

                if self.environment.should_interrupt():
                    break

        if not matched_any and node.default_case:
            node.default_case.body.accept(self)

        self.environment.exit_match()

        self.last_result = None

    def visit_MatchCase(self, node: nodes.MatchCase) -> None:
        if node.is_default:
            self.last_result = True
            return

        if node.condition is None:
            self.last_result = True
            return

        node.condition.accept(self)
        result = self.consume()

        # Dla nodes.Expression musi być bool
        if not isinstance(node.condition, nodes.Pattern):
            self._check_bool(result, "Match case condition", node.location)

        self.last_result = result

    def visit_PositionalPattern(self, node: nodes.PositionalPattern) -> None:
        match_targets = self.environment.get_match_targets()

        if len(node.patterns) != len(match_targets):
            raise RuntimeError(
                f"Pattern count not matching. Expected {len(match_targets)}, "
                f"got {len(node.patterns)}",
                node.location,
            )

        for i, pattern in enumerate(node.patterns):
            self.environment.set_subject_index(i)
            pattern.accept(self)

            if not self.consume():
                self.last_result = False
                return

        self.last_result = True

    def visit_RelationalPattern(self, node: nodes.RelationalPattern) -> None:
        val = self.environment.get_current_target()

        node.expression.accept(self)
        comp_val = self.consume()

        # Różne typy = nie pasuje
        if type(val) is not type(comp_val):
            self.last_result = False
            return

        OPS = {
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }

        op_func = OPS.get(node.op)
        self.last_result = op_func(val, comp_val) if op_func else False

    def visit_TypePattern(self, node: nodes.TypePattern) -> None:
        val = self.environment.get_current_target()

        TYPES = {
            "int": lambda a: isinstance(a, int) and not isinstance(a, bool),
            "float": lambda a: isinstance(a, float),
            "string": lambda a: isinstance(a, str),
            "bool": lambda a: isinstance(a, bool),
        }

        checker = TYPES.get(node.type_name)
        self.last_result = checker(val) if checker else False

    def visit_ConstantPattern(self, node: nodes.ConstantPattern) -> None:
        val = self.environment.get_current_target()
        node.value.accept(self)
        pattern_val = self.consume()

        self.last_result = val == pattern_val

    def visit_WildcardPattern(self, node: nodes.WildcardPattern) -> None:
        self.last_result = True

    def visit_AndPattern(self, node: nodes.AndPattern) -> None:
        node.left.accept(self)
        if not self.consume():
            self.last_result = False
            return

        node.right.accept(self)
        self.last_result = self.consume()

    def load(self, node: nodes.ASTNode) -> None:
        node.accept(self)

    def invoke(self, function_name: str, args: Optional[List[Any]] = None) -> Any:
        if args is None:
            args = []

        func = self.environment.get_function(function_name)
        if func is None:
            raise RuntimeError(f"Function '{function_name}' not found", None)

        self.environment.enter_function(args, function_name, None)
        try:
            func.accept(self)
        finally:
            self.environment.exit_function()

        return self.consume()
