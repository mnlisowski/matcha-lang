import unittest
import io

from src.lexer.reader import CharReader
from src.lexer.lexer import Lexer
from src.parser.parser import Parser, ParserError
import src.ast.ast_nodes as nodes


class TestParserIntegration(unittest.TestCase):
    """Comprehensive integration tests for Lexer and Parser."""

    # HELPER METHODS

    def parse_source(self, source_code: str):
        """
        String -> CharReader -> Lexer -> Parser
        """
        stream = io.StringIO(source_code)
        reader = CharReader(stream)
        lexer = Lexer(reader)

        errors = []

        def error_handler(message):
            errors.append(message)

        parser = Parser(lexer, error_handler)
        return parser, errors

    def parse_expr(self, source_code: str):
        parser, errors = self.parse_source(source_code)
        expr = parser.try_parse_expression()
        return expr, errors

    def parse_stmt(self, source_code: str):
        parser, errors = self.parse_source(source_code)
        stmt = parser.try_parse_statement()
        return stmt, errors

    # 1. PRIMARY EXPRESSIONS

    def test_int_literal(self):
        """Test integer literal parsing."""
        expr, errors = self.parse_expr("42")

        self.assertFalse(errors)

        self.assertEqual(expr.value, 42)
        self.assertIsInstance(expr, nodes.IntLiteral)
        self.assertIsNotNone(expr.location)

    def test_float_literal(self):
        """Test float literal parsing."""
        expr, errors = self.parse_expr("3.14159")

        self.assertFalse(errors)
        self.assertAlmostEqual(expr.value, 3.14159, places=5)
        self.assertIsInstance(expr, nodes.FloatLiteral)

    def test_string_literal(self):
        """Test string literal parsing."""
        expr, errors = self.parse_expr('"hello world"')

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.StringLiteral)
        self.assertEqual(expr.value, "hello world")

    def test_boolean_literals(self):
        """Test true and false literals."""
        # True
        expr_true, errors1 = self.parse_expr("true")
        self.assertFalse(errors1)
        self.assertIsInstance(expr_true, nodes.BoolLiteral)
        self.assertEqual(expr_true.value, True)

        # False
        expr_false, errors2 = self.parse_expr("false")
        self.assertFalse(errors2)
        self.assertEqual(expr_false.value, False)

    def test_variable_expression(self):
        expr, errors = self.parse_expr("counter")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.Variable)
        self.assertEqual(expr.name, "counter")
        self.assertIsNotNone(expr.location)

    def test_function_call_with_arguments(self):
        """Test function call with multiple arguments."""
        expr, errors = self.parse_expr("foo(1, x, 2 + 3)")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.FunctionCall)
        self.assertEqual(expr.name, "foo")
        self.assertEqual(len(expr.arguments), 3)

        # First argument: literal 1
        self.assertEqual(expr.arguments[0].value, 1)

        # Second argument: nodes.variable x
        self.assertIsInstance(expr.arguments[1], nodes.Variable)
        self.assertEqual(expr.arguments[1].name, "x")

        # Third argument: nodes.expression 2 + 3
        self.assertIsInstance(expr.arguments[2], nodes.AddExpression)

    def test_function_call_no_arguments(self):
        """Test function call without arguments."""
        expr, errors = self.parse_expr("getTime()")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.FunctionCall)
        self.assertEqual(expr.name, "getTime")
        self.assertEqual(len(expr.arguments), 0)

    def test_parenthesized_expression(self):
        """Test expression in parentheses."""
        expr, errors = self.parse_expr("(42)")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.IntLiteral)
        self.assertEqual(expr.value, 42)

    def test_deeply_nested_parentheses(self):
        """Test deeply nested parenthesized expressions."""
        expr, errors = self.parse_expr("((((x))))")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.Variable)
        self.assertEqual(expr.name, "x")

    # 2. UNARY EXPRESSIONS

    def test_unary_minus(self):
        """Test unary minus operator."""
        expr, errors = self.parse_expr("-42")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.UnaryMinusExpression)
        self.assertEqual(expr.operand.value, 42)
        self.assertIsNotNone(expr.location)

    def test_unary_not(self):
        """Test logical NOT operator."""
        expr, errors = self.parse_expr("!true")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.NotExpression)
        self.assertEqual(expr.operand.value, True)

    def test_double_unary_minus(self):
        """Test double negation: --x."""
        parser, errors = self.parse_source("--x")

        with self.assertRaises(ParserError):
            parser.try_parse_expression()

    def test_unary_not_on_expression(self):
        """Test NOT on complex expression."""
        expr, errors = self.parse_expr("!(x > 5)")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.NotExpression)
        self.assertIsInstance(expr.operand, nodes.GreaterExpression)

    # 3. BINARY ARITHMETIC EXPRESSIONS

    def test_addition(self):
        """Test addition operator."""
        expr, errors = self.parse_expr("1 + 2")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.AddExpression)
        self.assertEqual(expr.left.value, 1)
        self.assertEqual(expr.right.value, 2)

    def test_subtraction(self):
        """Test subtraction operator."""
        expr, errors = self.parse_expr("10 - 3")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.SubtractExpression)
        self.assertEqual(expr.left.value, 10)
        self.assertEqual(expr.right.value, 3)

    def test_multiplication(self):
        """Test multiplication operator."""
        expr, errors = self.parse_expr("4 * 5")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.MultiplyExpression)
        self.assertEqual(expr.left.value, 4)
        self.assertEqual(expr.right.value, 5)

    def test_division(self):
        """Test division operator."""
        expr, errors = self.parse_expr("20 / 4")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.DivideExpression)
        self.assertEqual(expr.left.value, 20)
        self.assertEqual(expr.right.value, 4)

    def test_arithmetic_left_associativity(self):
        """Test left-to-right associativity: 10 - 3 - 2 = (10 - 3) - 2."""
        expr, errors = self.parse_expr("10 - 3 - 2")

        self.assertFalse(errors)
        # Root should be subtraction
        self.assertIsInstance(expr, nodes.SubtractExpression)
        # Right operand should be 2
        self.assertEqual(expr.right.value, 2)
        # Left operand should be (10 - 3)
        self.assertIsInstance(expr.left, nodes.SubtractExpression)
        self.assertEqual(expr.left.left.value, 10)
        self.assertEqual(expr.left.right.value, 3)

    def test_multiplication_precedence(self):
        """Test that * has higher precedence than +."""
        expr, errors = self.parse_expr("2 + 3 * 4")

        self.assertFalse(errors)
        # Root: addition
        self.assertIsInstance(expr, nodes.AddExpression)
        self.assertEqual(expr.left.value, 2)

        # Right side: multiplication
        self.assertIsInstance(expr.right, nodes.MultiplyExpression)
        self.assertEqual(expr.right.left.value, 3)
        self.assertEqual(expr.right.right.value, 4)

    # 4. COMPARISON EXPRESSIONS

    def test_less_than(self):
        """Test < operator."""
        expr, errors = self.parse_expr("a < b")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.LessExpression)
        self.assertEqual(expr.left.name, "a")
        self.assertEqual(expr.right.name, "b")

    def test_less_equal(self):
        """Test <= operator."""
        expr, errors = self.parse_expr("x <= 10")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.LessEqualExpression)
        self.assertEqual(expr.left.name, "x")
        self.assertEqual(expr.right.value, 10)

    def test_greater_than(self):
        """Test > operator."""
        expr, errors = self.parse_expr("count > 0")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.GreaterExpression)
        self.assertEqual(expr.left.name, "count")
        self.assertEqual(expr.right.value, 0)

    def test_greater_equal(self):
        """Test >= operator."""
        expr, errors = self.parse_expr("age >= 18")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.GreaterEqualExpression)
        self.assertEqual(expr.left.name, "age")
        self.assertEqual(expr.right.value, 18)

    def test_comparison_with_arithmetic(self):
        """Test comparison has lower precedence than arithmetic."""
        expr, errors = self.parse_expr("2 + 3 > 4")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.GreaterExpression)
        # Left side should be addition
        self.assertIsInstance(expr.left, nodes.AddExpression)
        self.assertEqual(expr.right.value, 4)

    # 5. EQUALITY EXPRESSIONS

    def test_equality(self):
        """Test == operator."""
        expr, errors = self.parse_expr("x == y")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.EqualExpression)
        self.assertEqual(expr.left.name, "x")
        self.assertEqual(expr.right.name, "y")

    def test_not_equal(self):
        """Test != operator."""
        expr, errors = self.parse_expr("status != 0")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.NotEqualExpression)
        self.assertEqual(expr.left.name, "status")
        self.assertEqual(expr.right.value, 0)

    # 6. LOGICAL EXPRESSIONS

    def test_logical_and(self):
        """Test AND operator."""
        expr, errors = self.parse_expr("a and b")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.AndExpression)
        self.assertEqual(expr.left.name, "a")
        self.assertEqual(expr.right.name, "b")

    def test_logical_or(self):
        """Test OR operator."""
        expr, errors = self.parse_expr("x or y")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.OrExpression)
        self.assertEqual(expr.left.name, "x")
        self.assertEqual(expr.right.name, "y")

    def test_logical_operator_precedence(self):
        """Test that AND has higher precedence than OR."""
        expr, errors = self.parse_expr("a or b and c")

        self.assertFalse(errors)
        # Root: OR
        self.assertIsInstance(expr, nodes.OrExpression)
        self.assertEqual(expr.left.name, "a")

        # Right side: AND
        self.assertIsInstance(expr.right, nodes.AndExpression)
        self.assertEqual(expr.right.left.name, "b")
        self.assertEqual(expr.right.right.name, "c")

    # 7. COMPLEX PRECEDENCE TEST

    def test_full_precedence_chain(self):
        """
        Expression: 2 + 3 * 4 > 10 and x == y or z

        Expected precedence (highest to lowest):
        1. * (multiplication)
        2. + (addition)
        3. > (comparison)
        4. == (equality)
        5. and (logical AND)
        6. or (logical OR)
        """
        source = "2 + 3 * 4 > 10 and x == y or z"
        expr, errors = self.parse_expr(source)

        self.assertFalse(errors)

        # Root: OR
        self.assertIsInstance(expr, nodes.OrExpression)
        self.assertEqual(expr.right.name, "z")

        # Left of OR: AND
        and_expr = expr.left
        self.assertIsInstance(and_expr, nodes.AndExpression)

        # Right of AND: x == y
        eq_expr = and_expr.right
        self.assertIsInstance(eq_expr, nodes.EqualExpression)
        self.assertEqual(eq_expr.left.name, "x")
        self.assertEqual(eq_expr.right.name, "y")

        # Left of AND: (...) > 10
        gt_expr = and_expr.left
        self.assertIsInstance(gt_expr, nodes.GreaterExpression)
        self.assertEqual(gt_expr.right.value, 10)

        # Left of >: 2 + (...)
        add_expr = gt_expr.left
        self.assertIsInstance(add_expr, nodes.AddExpression)
        self.assertEqual(add_expr.left.value, 2)

        # Right of +: 3 * 4
        mul_expr = add_expr.right
        self.assertIsInstance(mul_expr, nodes.MultiplyExpression)
        self.assertEqual(mul_expr.left.value, 3)
        self.assertEqual(mul_expr.right.value, 4)

        # Verify all nodes have location info
        self.assertIsNotNone(expr.location)
        self.assertIsNotNone(mul_expr.location)

    # 8. ASSIGNMENT STATEMENT

    def test_simple_assignment(self):
        """Test simple nodes.variable assignment."""
        stmt, errors = self.parse_stmt("x = 10;")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.AssignmentStatement)
        self.assertEqual(stmt.variable_name, "x")
        self.assertIsInstance(stmt.expression, nodes.IntLiteral)
        self.assertEqual(stmt.expression.value, 10)

    def test_assignment_with_expression(self):
        """Test assignment with complex nodes.expression."""
        stmt, errors = self.parse_stmt("result = a + b * c;")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.AssignmentStatement)
        self.assertEqual(stmt.variable_name, "result")
        self.assertIsInstance(stmt.expression, nodes.AddExpression)

    # 9. FUNCTION CALL STATEMENT

    def test_function_call_statement(self):
        """Test function call as statement."""
        stmt, errors = self.parse_stmt("print(x);")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.FunctionCallStatement)
        self.assertEqual(stmt.name, "print")
        self.assertEqual(len(stmt.arguments), 1)
        self.assertEqual(stmt.arguments[0].name, "x")

    def test_function_call_statement_no_args(self):
        """Test function call with no arguments."""
        stmt, errors = self.parse_stmt("refresh();")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.FunctionCallStatement)
        self.assertEqual(stmt.name, "refresh")
        self.assertEqual(len(stmt.arguments), 0)

    # 10. BLOCK STATEMENT

    def test_empty_block(self):
        """Test empty block statement."""
        stmt, errors = self.parse_stmt("{}")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.Block)
        self.assertEqual(len(stmt.statements), 0)

    def test_block_with_statements(self):
        """Test nodes.block with multiple statements."""
        stmt, errors = self.parse_stmt("{ x = 1; y = 2; return x; }")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.Block)
        self.assertEqual(len(stmt.statements), 3)

        # First statement: assignment
        self.assertIsInstance(stmt.statements[0], nodes.AssignmentStatement)
        self.assertEqual(stmt.statements[0].variable_name, "x")

        # Second statement: assignment
        self.assertIsInstance(stmt.statements[1], nodes.AssignmentStatement)
        self.assertEqual(stmt.statements[1].variable_name, "y")

        # Third statement: return
        self.assertIsInstance(stmt.statements[2], nodes.ReturnStatement)

    def test_nested_blocks(self):
        """Test nested block statements."""
        stmt, errors = self.parse_stmt("{ { x = 1; } }")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.Block)
        self.assertEqual(len(stmt.statements), 1)

        inner_block = stmt.statements[0]
        self.assertIsInstance(inner_block, nodes.Block)
        self.assertEqual(len(inner_block.statements), 1)

    # 11. IF STATEMENT

    def test_if_statement_without_else(self):
        """Test if statement without else branch."""
        stmt, errors = self.parse_stmt("if (x > 0) { return x; }")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.IfStatement)

        # Check condition
        self.assertIsInstance(stmt.condition, nodes.GreaterExpression)
        self.assertEqual(stmt.condition.left.name, "x")

        # Check then branch
        self.assertIsInstance(stmt.then_branch, nodes.Block)
        self.assertEqual(len(stmt.then_branch.statements), 1)

        # Check no else branch
        self.assertIsNone(stmt.else_branch)

    def test_if_statement_with_else(self):
        """Test if-else statement."""
        stmt, errors = self.parse_stmt("if (flag) { x = 1; } else { x = 0; }")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.IfStatement)

        # Check condition
        self.assertIsInstance(stmt.condition, nodes.Variable)
        self.assertEqual(stmt.condition.name, "flag")

        # Check then branch
        self.assertIsInstance(stmt.then_branch, nodes.Block)
        then_stmt = stmt.then_branch.statements[0]
        self.assertEqual(then_stmt.variable_name, "x")
        self.assertEqual(then_stmt.expression.value, 1)

        # Check else branch
        self.assertIsNotNone(stmt.else_branch)
        self.assertIsInstance(stmt.else_branch, nodes.Block)
        else_stmt = stmt.else_branch.statements[0]
        self.assertEqual(else_stmt.variable_name, "x")
        self.assertEqual(else_stmt.expression.value, 0)

    def test_nested_if_statements(self):
        """Test nested if statements (if-else-if chain)."""
        source = """
        if (x < 0) {
            result = -1;
        } else {
            if (x > 0) {
                result = 1;
            } else {
                result = 0;
            }
        }
        """
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.IfStatement)

        # Check else branch contains another if
        else_block = stmt.else_branch
        self.assertIsInstance(else_block, nodes.Block)
        nested_if = else_block.statements[0]
        self.assertIsInstance(nested_if, nodes.IfStatement)

    # 12. WHILE STATEMENT

    def test_while_statement(self):
        """Test while loop."""
        stmt, errors = self.parse_stmt("while (i < 10) { i = i + 1; }")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.WhileStatement)

        # Check condition
        self.assertIsInstance(stmt.condition, nodes.LessExpression)
        self.assertEqual(stmt.condition.left.name, "i")
        self.assertEqual(stmt.condition.right.value, 10)

        # Check body
        self.assertIsInstance(stmt.body, nodes.Block)
        self.assertEqual(len(stmt.body.statements), 1)

        body_stmt = stmt.body.statements[0]
        self.assertIsInstance(body_stmt, nodes.AssignmentStatement)
        self.assertEqual(body_stmt.variable_name, "i")

    def test_while_with_complex_condition(self):
        """Test while with complex boolean condition."""
        stmt, errors = self.parse_stmt("while (running and count < max) { }")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.WhileStatement)
        self.assertIsInstance(stmt.condition, nodes.AndExpression)

    def test_nested_while_loops(self):
        """Test nested while loops."""
        source = """
        while (outer) {
            while (inner) {
                work();
            }
        }
        """
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.WhileStatement)

        inner_while = stmt.body.statements[0]
        self.assertIsInstance(inner_while, nodes.WhileStatement)

    # 13. RETURN STATEMENT

    def test_return_with_value(self):
        """Test return statement with value."""
        stmt, errors = self.parse_stmt("return 42;")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.ReturnStatement)
        self.assertIsNotNone(stmt.expression)
        self.assertEqual(stmt.expression.value, 42)

    def test_return_without_value(self):
        """Test return statement without value."""
        stmt, errors = self.parse_stmt("return;")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.ReturnStatement)
        self.assertIsNone(stmt.expression)

    def test_return_with_expression(self):
        """Test return with complex expression."""
        stmt, errors = self.parse_stmt("return a + b * c;")

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.ReturnStatement)
        self.assertIsInstance(stmt.expression, nodes.AddExpression)

    # 14. NESTED CONTROL FLOW

    def test_if_inside_while(self):
        """Test if statement nested inside while loop."""
        source = """
        while (running) {
            if (condition) {
                process();
            } else {
                skip();
            }
        }
        """
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.WhileStatement)

        # Get if statement from while body
        if_stmt = stmt.body.statements[0]
        self.assertIsInstance(if_stmt, nodes.IfStatement)

        # Check if has both branches
        self.assertIsNotNone(if_stmt.then_branch)
        self.assertIsNotNone(if_stmt.else_branch)

    def test_complex_nested_control_flow(self):
        """Test deeply nested control structures."""
        source = """
        while (run) {
            if (i < 10) {
                i = i + 1;
                if (i == 5) {
                    return i;
                }
            } else {
                return 0;
            }
        }
        """
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.WhileStatement)
        self.assertIsInstance(stmt.condition, nodes.Variable)

        # First level: if inside while
        outer_if = stmt.body.statements[0]
        self.assertIsInstance(outer_if, nodes.IfStatement)

        # Check condition of outer if
        self.assertIsInstance(outer_if.condition, nodes.LessExpression)
        self.assertEqual(outer_if.condition.left.name, "i")
        self.assertEqual(outer_if.condition.right.value, 10)

        # Then branch has 2 statements
        then_stmts = outer_if.then_branch.statements
        self.assertEqual(len(then_stmts), 2)

        # First: assignment
        self.assertIsInstance(then_stmts[0], nodes.AssignmentStatement)
        self.assertEqual(then_stmts[0].variable_name, "i")

        # Second: nested if
        inner_if = then_stmts[1]
        self.assertIsInstance(inner_if, nodes.IfStatement)
        self.assertIsInstance(inner_if.condition, nodes.EqualExpression)

        # Else branch: return 0
        else_stmts = outer_if.else_branch.statements
        self.assertEqual(len(else_stmts), 1)
        self.assertIsInstance(else_stmts[0], nodes.ReturnStatement)
        self.assertEqual(else_stmts[0].expression.value, 0)

    # 15. FUNCTION DEFINITION

    def test_function_no_parameters(self):
        """Test function definition without parameters."""
        source = 'fun sayHello() { print("Hello"); }'
        parser, errors = self.parse_source(source)
        prog = parser.parse_program()

        self.assertFalse(errors)
        self.assertEqual(len(prog.functions), 1)

        func = prog.functions[0]
        self.assertEqual(func.name, "sayHello")
        self.assertEqual(len(func.params), 0)
        self.assertIsInstance(func.body, nodes.Block)

    def test_function_with_parameters(self):
        """Test function definition with parameters."""
        source = "fun add(a, b, c) { return a + b + c; }"
        parser, errors = self.parse_source(source)
        prog = parser.parse_program()

        self.assertFalse(errors)
        func = prog.functions[0]

        self.assertEqual(func.name, "add")
        self.assertEqual(func.params, ["a", "b", "c"])

        # Check body
        self.assertEqual(len(func.body.statements), 1)
        return_stmt = func.body.statements[0]
        self.assertIsInstance(return_stmt, nodes.ReturnStatement)

    def test_function_empty_body(self):
        """Test function with empty body."""
        source = "fun empty() {}"
        parser, errors = self.parse_source(source)
        prog = parser.parse_program()

        self.assertFalse(errors)
        func = prog.functions[0]
        self.assertEqual(len(func.body.statements), 0)

    def test_function_complex_body(self):
        """Test function with complex body."""
        source = """
        fun calculate(x, y) {
            result = 0;
            if (x > y) {
                result = x - y;
            } else {
                result = y - x;
            }
            return result;
        }
        """
        parser, errors = self.parse_source(source)
        prog = parser.parse_program()

        self.assertFalse(errors)
        func = prog.functions[0]

        self.assertEqual(func.name, "calculate")
        self.assertEqual(func.params, ["x", "y"])
        self.assertEqual(len(func.body.statements), 3)

        # First: assignment
        self.assertIsInstance(func.body.statements[0], nodes.AssignmentStatement)

        # Second: if nodes.statement
        self.assertIsInstance(func.body.statements[1], nodes.IfStatement)

        # Third: return
        self.assertIsInstance(func.body.statements[2], nodes.ReturnStatement)

    # 16. PROGRAM WITH MULTIPLE FUNCTIONS

    def test_program_single_function(self):
        """Test program with single function."""
        source = "fun main() { return 0; }"
        parser, errors = self.parse_source(source)
        prog = parser.parse_program()

        self.assertFalse(errors)
        self.assertEqual(len(prog.functions), 1)
        self.assertEqual(prog.functions[0].name, "main")

    def test_program_multiple_functions(self):
        """Test program with multiple functions."""
        source = """
        fun first() { }
        fun second() { }
        fun third() { }
        """
        parser, errors = self.parse_source(source)
        prog = parser.parse_program()

        self.assertFalse(errors)
        self.assertEqual(len(prog.functions), 3)
        self.assertEqual(prog.functions[0].name, "first")
        self.assertEqual(prog.functions[1].name, "second")
        self.assertEqual(prog.functions[2].name, "third")

    def test_complete_program_integration(self):
        """Test complete program with function calls and complex logic."""
        source = """
        fun add(a, b) {
            return a + b;
        }

        fun multiply(x, y) {
            result = 0;
            i = 0;
            while (i < y) {
                result = add(result, x);
                i = i + 1;
            }
            return result;
        }

        fun main() {
            x = 10;
            y = 20;
            sum = add(x, y);
            product = multiply(x, 5);
            print(sum);
            print(product);
        }
        """
        parser, errors = self.parse_source(source)
        program = parser.parse_program()

        self.assertFalse(errors)
        self.assertEqual(len(program.functions), 3)

        # Verify 'add' function
        func_add = program.functions[0]
        self.assertEqual(func_add.name, "add")
        self.assertEqual(func_add.params, ["a", "b"])
        self.assertEqual(len(func_add.body.statements), 1)

        return_stmt = func_add.body.statements[0]
        self.assertIsInstance(return_stmt, nodes.ReturnStatement)
        self.assertIsInstance(return_stmt.expression, nodes.AddExpression)

        # Verify 'multiply' function
        func_mult = program.functions[1]
        self.assertEqual(func_mult.name, "multiply")
        self.assertEqual(func_mult.params, ["x", "y"])
        self.assertEqual(len(func_mult.body.statements), 4)

        # Should have while loop
        while_stmt = func_mult.body.statements[2]
        self.assertIsInstance(while_stmt, nodes.WhileStatement)

        # Verify 'main' function
        func_main = program.functions[2]
        self.assertEqual(func_main.name, "main")
        stmts = func_main.body.statements
        self.assertEqual(len(stmts), 6)

        # Check function calls in main
        sum_assign = stmts[2]
        self.assertIsInstance(sum_assign, nodes.AssignmentStatement)
        self.assertEqual(sum_assign.variable_name, "sum")
        self.assertIsInstance(sum_assign.expression, nodes.FunctionCall)
        self.assertEqual(sum_assign.expression.name, "add")

        # Check arguments of add call
        add_args = sum_assign.expression.arguments
        self.assertEqual(len(add_args), 2)
        self.assertEqual(add_args[0].name, "x")
        self.assertEqual(add_args[1].name, "y")

    # 17. MATCH STATEMENT

    def test_match_empty_header(self):
        """Test match with no subjects."""
        source = "match { default => {} }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.MatchStatement)
        self.assertEqual(len(stmt.subjects), 0)
        self.assertEqual(len(stmt.cases), 0)

    def test_match_single_subject(self):
        """Test match with single subject."""
        source = "match x { default => {} }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.MatchStatement)
        self.assertEqual(len(stmt.subjects), 1)

        subject_expr, alias = stmt.subjects[0]
        self.assertIsInstance(subject_expr, nodes.Variable)
        self.assertEqual(subject_expr.name, "x")
        self.assertIsNone(alias)

    def test_match_with_alias(self):
        """Test match with aliased subject."""
        source = "match x as value { default => {} }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        subject_expr, alias = stmt.subjects[0]
        self.assertEqual(alias, "value")

    def test_match_multiple_subjects(self):
        """Test match with multiple subjects."""
        source = "match x as a, y as b, z { default => {} }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        self.assertEqual(len(stmt.subjects), 3)

        # First subject with alias
        self.assertEqual(stmt.subjects[0][0].name, "x")
        self.assertEqual(stmt.subjects[0][1], "a")

        # Second subject with alias
        self.assertEqual(stmt.subjects[1][0].name, "y")
        self.assertEqual(stmt.subjects[1][1], "b")

        # Third subject without alias
        self.assertEqual(stmt.subjects[2][0].name, "z")
        self.assertIsNone(stmt.subjects[2][1])

    def test_match_default_case(self):
        """Test match with default case."""
        source = "match x { default => { return; } }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        self.assertEqual(len(stmt.cases), 0)

        case = stmt.default_case
        self.assertTrue(case.is_default)
        self.assertIsNone(case.condition)
        self.assertIsInstance(case.body, nodes.Block)

    # 18. MATCH STATEMENT - EXPRESSION CONDITIONS

    def test_match_literal_condition(self):
        """Test match with literal value as condition."""
        source = "match x { 10 => {} }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        case = stmt.cases[0]
        self.assertIsInstance(case.condition, nodes.IntLiteral)
        self.assertEqual(case.condition.value, 10)
        self.assertFalse(case.is_default)

    def test_match_variable_condition(self):
        """Test match with variable as condition."""
        source = "match x { y => {} }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        case = stmt.cases[0]
        self.assertIsInstance(case.condition, nodes.Variable)
        self.assertEqual(case.condition.name, "y")

    def test_match_complex_expression_condition(self):
        """Test match with complex expression as condition."""
        source = "match x { (x1 > 5 or x2 < 2) => { return; } }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        case = stmt.cases[0]

        # Condition should be OrExpression
        self.assertIsInstance(case.condition, nodes.OrExpression)
        self.assertIsInstance(case.condition.left, nodes.GreaterExpression)
        self.assertIsInstance(case.condition.right, nodes.LessExpression)

    def test_match_multiple_cases(self):
        """Test match with multiple cases."""
        source = """
        match x {
            1 => { return 1; }
            2 => { return 2; }
            default => { return 0; }
        }
        """
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        self.assertEqual(len(stmt.cases), 2)

        # First case: literal 1
        self.assertIsInstance(stmt.cases[0].condition, nodes.IntLiteral)
        self.assertEqual(stmt.cases[0].condition.value, 1)
        self.assertFalse(stmt.cases[0].is_default)

        # Second case: literal 2
        self.assertIsInstance(stmt.cases[1].condition, nodes.IntLiteral)
        self.assertEqual(stmt.cases[1].condition.value, 2)
        self.assertFalse(stmt.cases[1].is_default)

    # 19. MATCH STATEMENT - PATTERNS

    def test_match_wildcard_pattern(self):
        """Test match with wildcard pattern."""
        source = "match x { [_] => {} }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        pos_pat = stmt.cases[0].condition
        self.assertIsInstance(pos_pat, nodes.PositionalPattern)
        self.assertEqual(len(pos_pat.patterns), 1)
        self.assertIsInstance(pos_pat.patterns[0], nodes.WildcardPattern)

    def test_match_constant_pattern(self):
        """Test match with constant patterns."""
        source = 'match x { [1, "hello", true] => {} }'
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        pos_pat = stmt.cases[0].condition
        patterns = pos_pat.patterns

        self.assertEqual(len(patterns), 3)

        # First: integer constant
        self.assertIsInstance(patterns[0], nodes.ConstantPattern)
        self.assertEqual(patterns[0].value.value, 1)

        # Second: string constant
        self.assertIsInstance(patterns[1], nodes.ConstantPattern)
        self.assertEqual(patterns[1].value.value, "hello")

        # Third: boolean constant
        self.assertIsInstance(patterns[2], nodes.ConstantPattern)
        self.assertEqual(patterns[2].value.value, True)

    def test_match_type_pattern(self):
        """Test match with type patterns."""
        source = "match x { [is int, is string] => {} }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        patterns = stmt.cases[0].condition.patterns

        self.assertEqual(len(patterns), 2)
        self.assertIsInstance(patterns[0], nodes.TypePattern)
        self.assertIsInstance(patterns[1], nodes.TypePattern)

    def test_match_relational_pattern(self):
        """Test match with relational patterns."""
        source = "match x { [> 5, < 10, >= 0, <= 100] => {} }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        patterns = stmt.cases[0].condition.patterns

        self.assertEqual(len(patterns), 4)

        # Check operators
        self.assertIsInstance(patterns[0], nodes.RelationalPattern)
        self.assertEqual(patterns[0].op, ">")
        self.assertEqual(patterns[0].expression.value, 5)

        self.assertIsInstance(patterns[1], nodes.RelationalPattern)
        self.assertEqual(patterns[1].op, "<")

        self.assertIsInstance(patterns[2], nodes.RelationalPattern)
        self.assertEqual(patterns[2].op, ">=")

        self.assertIsInstance(patterns[3], nodes.RelationalPattern)
        self.assertEqual(patterns[3].op, "<=")

    def test_match_and_pattern(self):
        """Test match with AND nodes.pattern."""
        source = "match x { [is int AND > 0] => {} }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        patterns = stmt.cases[0].condition.patterns

        self.assertEqual(len(patterns), 1)
        and_pat = patterns[0]
        self.assertIsInstance(and_pat, nodes.AndPattern)

        # Left side: type pattern
        self.assertIsInstance(and_pat.left, nodes.TypePattern)

        # Right side: relational pattern
        self.assertIsInstance(and_pat.right, nodes.RelationalPattern)
        self.assertEqual(and_pat.right.op, ">")

    def test_match_complex_and_pattern(self):
        """Test match with chained AND patterns."""
        source = "match x { [is int AND > 0 AND < 100] => {} }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        pattern = stmt.cases[0].condition.patterns[0]

        # Root should be AND
        self.assertIsInstance(pattern, nodes.AndPattern)

        # Right side should be relational (< 100)
        self.assertIsInstance(pattern.right, nodes.RelationalPattern)
        self.assertEqual(pattern.right.op, "<")

        # Left side should be another AND
        self.assertIsInstance(pattern.left, nodes.AndPattern)
        self.assertIsInstance(pattern.left.left, nodes.TypePattern)
        self.assertIsInstance(pattern.left.right, nodes.RelationalPattern)

    def test_match_empty_positional_pattern(self):
        """Test match with empty positional pattern."""
        source = "match x { [] => {} }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        pos_pat = stmt.cases[0].condition
        self.assertIsInstance(pos_pat, nodes.PositionalPattern)
        self.assertEqual(len(pos_pat.patterns), 0)

    def test_match_mixed_patterns(self):
        """Test match with various pattern types mixed."""
        source = 'match x { [1, _, is int, > 5, "text"] => {} }'
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        patterns = stmt.cases[0].condition.patterns

        self.assertEqual(len(patterns), 5)
        self.assertIsInstance(patterns[0], nodes.ConstantPattern)  # 1
        self.assertIsInstance(patterns[1], nodes.WildcardPattern)  # _
        self.assertIsInstance(patterns[2], nodes.TypePattern)  # is int
        self.assertIsInstance(patterns[3], nodes.RelationalPattern)  # > 5
        self.assertIsInstance(patterns[4], nodes.ConstantPattern)  # "text"

    # 20. MATCH STATEMENT - COMPLEX CASES

    def test_match_with_complex_body(self):
        """Test match case with complex body."""
        source = """
        match x {
            1 => {
                i = 0;
                while (i < 10) {
                    i = i + 1;
                }
                return i;
            }
        }
        """
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        case_body = stmt.cases[0].body
        self.assertEqual(len(case_body.statements), 3)

        self.assertIsInstance(case_body.statements[0], nodes.AssignmentStatement)
        self.assertIsInstance(case_body.statements[1], nodes.WhileStatement)
        self.assertIsInstance(case_body.statements[2], nodes.ReturnStatement)

    def test_match_multiple_subjects_with_patterns(self):
        """Test match with multiple subjects and pattern matching."""
        source = """
        match x as a, y as b {
            [is int, > 0] => { return 1; }
            [_, is string] => { return 2; }
            default => { return 0; }
        }
        """
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        self.assertEqual(len(stmt.subjects), 2)
        self.assertEqual(len(stmt.cases), 2)

        # First case: [is int, > 0]
        case1_patterns = stmt.cases[0].condition.patterns
        self.assertIsInstance(case1_patterns[0], nodes.TypePattern)
        self.assertIsInstance(case1_patterns[1], nodes.RelationalPattern)

        # Second case: [_, is string]
        case2_patterns = stmt.cases[1].condition.patterns
        self.assertIsInstance(case2_patterns[0], nodes.WildcardPattern)
        self.assertIsInstance(case2_patterns[1], nodes.TypePattern)

    # 21. SOURCE LOCATION TRACKING

    def test_location_tracking_expressions(self):
        """Test that expressions have proper location information."""
        source = """
        x = 1 + 2 * 3;
        """
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)

        # Assignment should have location
        self.assertIsNotNone(stmt.location)

        # Expression tree should have locations
        expr = stmt.expression
        self.assertIsNotNone(expr.location)

        # Even nested expressions
        mul_expr = expr.right
        self.assertIsNotNone(mul_expr.location)

    def test_location_tracking_statements(self):
        """Test that statements have proper location information."""
        source = """
        if (x > 0) {
            return x;
        }
        """
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)

        # If statement location
        self.assertIsNotNone(stmt.location)

        # Condition location
        self.assertIsNotNone(stmt.condition.location)

        # Body location
        self.assertIsNotNone(stmt.then_branch.location)

        # Return statement location
        return_stmt = stmt.then_branch.statements[0]
        self.assertIsNotNone(return_stmt.location)

    def test_location_tracking_in_program(self):
        """Test location tracking across entire program."""
        source = """
        fun test(a) {
            x = a + 1;
            return x;
        }
        """
        parser, errors = self.parse_source(source)
        program = parser.parse_program()

        self.assertFalse(errors)

        func = program.functions[0]

        # Function location
        self.assertIsNotNone(func.location)
        self.assertEqual(func.location.line, 2)

        # First statement location
        stmt1 = func.body.statements[0]
        self.assertIsNotNone(stmt1.location)
        self.assertEqual(stmt1.location.line, 3)

        # Second statement location
        stmt2 = func.body.statements[1]
        self.assertIsNotNone(stmt2.location)
        self.assertEqual(stmt2.location.line, 4)

    # 22. ERROR HANDLING - MISSING TOKENS


    def test_error_missing_closing_paren(self):
        """Test error when closing parenthesis is missing."""
        with self.assertRaises(ParserError):
            parser, errors = self.parse_source("if (x > 0 {}")
            parser.try_parse_statement()

    def test_error_missing_closing_brace(self):
        """Test error when closing brace is missing."""
        with self.assertRaises(ParserError):
            parser, errors = self.parse_source("{ x = 1;")
            parser.try_parse_block()

    def test_error_missing_expression_in_assignment(self):
        """Test error when expression is missing in assignment."""
        with self.assertRaises(ParserError):
            parser, errors = self.parse_source("x = ;")
            parser.try_parse_statement()

    def test_error_missing_expression_in_condition(self):
        """Test error when expression is missing in if condition."""
        parser, errors = self.parse_source("if () {}")

        with self.assertRaises(ParserError):
            parser.try_parse_statement()

    # 23. ERROR HANDLING - INVALID SYNTAX

    def test_error_invalid_assignment_target(self):
        """Test error when trying to assign to function call."""

        with self.assertRaises(ParserError):
            parser, errors = self.parse_stmt("foo() = 5;")

    def test_error_duplicate_function_definition(self):
        """Test error when function is defined twice."""
        source = """
        fun test() {}
        fun test() {}
        """
        parser, errors = self.parse_source(source)
        with self.assertRaises(ParserError):
            parser.parse_program()

    def test_error_missing_function_name(self):
        """Test critical error when function name is missing."""
        parser, errors = self.parse_source("fun (a, b) {}")

        with self.assertRaises(ParserError):
            parser.parse_program()

    def test_error_missing_function_body(self):
        """Test error when function body is missing."""
        parser, errors = self.parse_source("fun test()")

        with self.assertRaises(ParserError):
            parser.parse_program()

    def test_error_statement_with_no_effect(self):
        """Test error for statement that has no effect."""
        parser, errors = self.parse_source("x;")

        with self.assertRaises(ParserError):
            parser.try_parse_statement()

        # self.assertTrue(len(errors) > 0)

    # 24. ERROR HANDLING - MATCH STATEMENT ERRORS

    def test_error_match_missing_arrow(self):
        """Test error when => is missing in match case."""
        with self.assertRaises(ParserError):
            parser, errors = self.parse_source("match x { 1 {} }")
            parser.try_parse_statement()

    def test_error_match_missing_case_body(self):
        """Test error when match case body is missing."""
        parser, errors = self.parse_source("match x { 1 => }")

        with self.assertRaises(ParserError):
            parser.try_parse_statement()

    def test_error_match_missing_closing_bracket(self):
        """Test error when ] is missing in positional pattern."""
        with self.assertRaises(ParserError):
            parser, errors = self.parse_source("match x { [1, 2 => {} }")
            parser.try_parse_statement()

    # 25. EDGE CASES

    def test_edge_case_single_identifier_statement_error(self):
        """Test that single identifier without effect causes error."""
        parser, errors = self.parse_source("someVariable;")

        with self.assertRaises(ParserError):
            parser.try_parse_statement()

    def test_edge_case_very_long_expression(self):
        """Test parsing of very long chained expression."""
        source = "result = " + " + ".join([str(i) for i in range(20)]) + ";"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)
        self.assertIsInstance(stmt, nodes.AssignmentStatement)

    def test_edge_case_deeply_nested_blocks(self):
        """Test deeply nested block structures."""
        source = "{ { { { x = 1; } } } }"
        stmt, errors = self.parse_stmt(source)

        self.assertFalse(errors)

        # Navigate through nesting
        level1 = stmt
        self.assertIsInstance(level1, nodes.Block)

        level2 = level1.statements[0]
        self.assertIsInstance(level2, nodes.Block)

        level3 = level2.statements[0]
        self.assertIsInstance(level3, nodes.Block)

        level4 = level3.statements[0]
        self.assertIsInstance(level4, nodes.Block)

        assignment = level4.statements[0]
        self.assertIsInstance(assignment, nodes.AssignmentStatement)

    def test_edge_case_function_with_many_parameters(self):
        """Test function with many parameters."""
        params = ", ".join([f"p{i}" for i in range(20)])
        source = f"fun test({params}) {{}}"

        parser, errors = self.parse_source(source)
        prog = parser.parse_program()

        self.assertFalse(errors)
        func = prog.functions[0]
        self.assertEqual(len(func.params), 20)

    def test_edge_case_function_call_with_many_arguments(self):
        """Test function call with many arguments."""
        args = ", ".join([str(i) for i in range(15)])
        expr, errors = self.parse_expr(f"foo({args})")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.FunctionCall)
        self.assertEqual(len(expr.arguments), 15)

    def test_edge_case_empty_program(self):
        """Test parsing empty program (should fail)."""
        parser, errors = self.parse_source("")

        self.assertFalse(errors)

    def test_edge_case_whitespace_only_program(self):
        """Test parsing program with only whitespace."""
        parser, errors = self.parse_source("   \n  \t  \n  ")

        self.assertFalse(errors)

    # 26. SPECIAL INTEGRATION CASES

    def test_integration_lexer_string_escape_sequences(self):
        """Test that lexer properly handles escape sequences in strings."""
        expr, errors = self.parse_expr('"hello\\nworld\\t!"')

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.StringLiteral)
        self.assertEqual(expr.value, "hello\nworld\t!")

    def test_integration_lexer_float_numbers(self):
        """Test that lexer properly tokenizes float numbers."""
        expr, errors = self.parse_expr("3.14159")

        self.assertFalse(errors)
        self.assertIsInstance(expr, nodes.FloatLiteral)
        self.assertAlmostEqual(expr.value, 3.14159)

    def test_integration_lexer_comments_ignored(self):
        """Test that lexer properly ignores comments."""
        source = """
        fun test() { // This is a comment
            x = 1; // Another comment
            return x; // Final comment
        }
        """
        parser, errors = self.parse_source(source)
        prog = parser.parse_program()

        self.assertFalse(errors)
        func = prog.functions[0]
        self.assertEqual(len(func.body.statements), 2)

    def test_integration_lexer_keywords_vs_identifiers(self):
        """Test that lexer distinguishes keywords from identifiers."""
        # 'if' is keyword, 'iff' is identifier
        expr1, _ = self.parse_expr("if")  # Should fail to parse as expression
        self.assertIsNone(expr1)

        expr2, errors2 = self.parse_expr("iff")
        self.assertFalse(errors2)
        self.assertIsInstance(expr2, nodes.Variable)
        self.assertEqual(expr2.name, "iff")

    def test_integration_complex_match_in_function(self):
        """Test match statement integration within function."""
        source = """
        fun classify(x, y) {
            result = 0;
            match x as val, y {
                [is int AND > 0, is int] => {
                    result = 1;
                }
                [_, > 10] => {
                    result = 2;
                }
                default => {
                    result = -1;
                }
            }
            return result;
        }
        """
        parser, errors = self.parse_source(source)
        prog = parser.parse_program()

        self.assertFalse(errors)
        func = prog.functions[0]

        # Should have 3 statements: assign, match, return
        self.assertEqual(len(func.body.statements), 3)

        match_stmt = func.body.statements[1]
        self.assertIsInstance(match_stmt, nodes.MatchStatement)

        # Verify match structure
        self.assertEqual(len(match_stmt.subjects), 2)
        self.assertEqual(len(match_stmt.cases), 2)

    def test_visualize_ast(self):
        """
        wizualizacja
        """
        source = """
        fun main() {
            x = 10;
            if (x > ( 5*2+2/(123 > 8))) {
                return x;
            }
            match x {
                1 => { return 0; }
                default => { return 1; }
            }
        }
        """

        parser, errors = self.parse_source(source)

        print("\n\nzrzut drzewa ast")

        self.assertFalse(errors)

    if __name__ == "__main__":
        unittest.main()
