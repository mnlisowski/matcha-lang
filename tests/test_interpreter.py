import unittest
import io
from src.lexer.reader import CharReader
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.interpreter.interpreter import (
    Interpreter,
    RuntimeError as InterpreterRuntimeError,
    TypeError as InterpreterTypeError,
    NameError as InterpreterNameError,
    ValueError as InterpreterValueError,
)
import src.ast.ast_nodes as nodes


class TestInterpreter(unittest.TestCase):
    def run_code(self, source_code: str, function_name: str = None, *args):
        stream = io.StringIO(source_code)
        reader = CharReader(stream)
        lexer = Lexer(reader)

        parser_errors = []

        def error_handler(msg):
            parser_errors.append(msg)

        parser = Parser(lexer, error_handler)
        program_ast = parser.parse_program()

        if parser_errors:
            raise Exception(f"Parser errors: {parser_errors}")

        interpreter = Interpreter()
        program_ast.accept(interpreter)

        if function_name:
            arg_nodes = []
            dummy_loc = nodes.SourceLocation(0, 0)

            for arg in args:
                if isinstance(arg, bool):
                    arg_nodes.append(nodes.BoolLiteral(arg, dummy_loc))
                elif isinstance(arg, int):
                    arg_nodes.append(nodes.IntLiteral(arg, dummy_loc))
                elif isinstance(arg, float):
                    arg_nodes.append(nodes.FloatLiteral(arg, dummy_loc))
                elif isinstance(arg, str):
                    arg_nodes.append(nodes.StringLiteral(arg, dummy_loc))
                else:
                    raise ValueError(f"Unsupported argument type: {type(arg)}")

            call_node = nodes.FunctionCall(function_name, arg_nodes, dummy_loc)

            return interpreter.interpret(call_node)

        return None

    def test_simple_addition(self):
        code = """
        fun test() {
            return 5 + 3;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 8)

    def test_simple_subtraction(self):
        code = """
        fun test() {
            return 10.5 - 3.5;
        }
        """
        self.assertAlmostEqual(self.run_code(code, "test"), 7.0)

    def test_multiplication(self):
        code = """
        fun test() {
            return 4 * 5;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 20)

    def test_division(self):
        code = """
        fun test() {
            return 20 / 4;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 5.0)

    def test_string_concatenation(self):
        code = """
        fun test() {
            return "hello" + " world";
        }
        """
        self.assertEqual(self.run_code(code, "test"), "hello world")

    def test_complex_arithmetic(self):
        code = """
        fun test() {
            return 2.0 + 3.0 * 4.0 - 10.0 / 2.0;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 9.0)

    def test_unary_minus(self):
        code = """
        fun test() {
            x = 10;
            return -x;
        }
        """
        self.assertEqual(self.run_code(code, "test"), -10)

    def test_error_add_int_float(self):
        code = """
        fun test() {
            return 5 + 2.5;
        }
        """
        with self.assertRaises(InterpreterTypeError) as ctx:
            self.run_code(code, "test")
        self.assertIn("Cannot perform '+'", str(ctx.exception))

    def test_error_add_int_string(self):
        code = """
        fun test() {
            return 5 + "hello";
        }
        """
        with self.assertRaises(InterpreterTypeError) as ctx:
            self.run_code(code, "test")
        self.assertIn("Cannot perform '+'", str(ctx.exception))

    def test_error_multiply_string(self):
        code = """
        fun test() {
            return "hello" * "world";
        }
        """
        with self.assertRaises(InterpreterTypeError) as ctx:
            self.run_code(code, "test")
        self.assertIn("Operator '*' requires", str(ctx.exception))

    def test_error_divide_by_zero(self):
        code = """
        fun test() {
            return 10 / 0;
        }
        """
        with self.assertRaises(InterpreterValueError) as ctx:
            self.run_code(code, "test")
        self.assertIn("Division by zero", str(ctx.exception))

    def test_error_compare_different_types(self):
        code = """
        fun test() {
            return 5 < "10";
        }
        """
        with self.assertRaises(InterpreterTypeError) as ctx:
            self.run_code(code, "test")
        self.assertIn("Cannot perform", str(ctx.exception))

    def test_error_unary_minus_on_string(self):
        code = """
        fun test() {
            return -"hello";
        }
        """
        with self.assertRaises(InterpreterTypeError) as ctx:
            self.run_code(code, "test")
        self.assertIn("requires numeric type", str(ctx.exception))

    def test_comparison_operators(self):
        code = """
        fun test() {
            a = 5;
            b = 10;
            if (a < b and b > a and a <= 5 and b >= 10) {
                return true;
            }
            return false;
        }
        """
        self.assertTrue(self.run_code(code, "test"))

    def test_equality_operators(self):
        code = """
        fun test() {
            if (5 == 5 and 5 != 3) {
                return true;
            }
            return false;
        }
        """
        self.assertTrue(self.run_code(code, "test"))

    def test_logical_and_short_circuit(self):
        code = """
        fun test() {
            x = 0;
            if (false and (x / 0) > 5) {
                return 1;
            }
            return 2;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 2)

    def test_logical_or_short_circuit(self):
        code = """
        fun test() {
            x = 0;
            if (true or (x / 0) > 5) {
                return 1;
            }
            return 2;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 1)

    def test_variable_assignment_and_retrieval(self):
        code = """
        fun test() {
            x = 42;
            return x;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 42)

    def test_variable_reassignment(self):
        code = """
        fun test() {
            x = 5;
            x = 10;
            x = x + 5;
            return x;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 15)

    def test_block_scope(self):
        code = """
        fun test() {
            x = 10;
            {
                x = 20;
            }
            return x;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 20)

    def test_nested_blocks_scope(self):
        code = """
        fun test() {
            x = 1;
            {
                x = 2;
                {
                    x = 3;
                }
            }
            return x;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 3)

    def test_error_undefined_variable(self):
        code = """
        fun test() {
            return undefined_var;
        }
        """
        with self.assertRaises(InterpreterNameError) as ctx:
            self.run_code(code, "test")
        self.assertIn("Undefined variable", str(ctx.exception))

    def test_if_else_statement(self):
        code = """
        fun test() {
            x = 10;
            if (x > 5) {
                return 1;
            } else {
                return 2;
            }
        }
        """
        self.assertEqual(self.run_code(code, "test"), 1)

    def test_while_loop_sum(self):
        code = """
        fun test() {
            i = 0;
            sum = 0;
            while (i < 5) {
                sum = sum + i;
                i = i + 1;
            }
            return sum;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 10)

    def test_nested_while_loops(self):
        code = """
        fun test() {
            i = 0;
            sum = 0;
            while (i < 3) {
                j = 0;
                while (j < 2) {
                    sum = sum + 1;
                    j = j + 1;
                }
                i = i + 1;
            }
            return sum;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 6)

    def test_function_call_simple(self):
        code = """
        fun add(a, b) {
            return a + b;
        }
        
        fun test() {
            return add(3, 4);
        }
        """
        self.assertEqual(self.run_code(code, "test"), 7)

    def test_recursive_factorial(self):
        code = """
        fun factorial(n) {
            if (n < 2) {
                return 1;
            }
            return n * factorial(n - 1);
        }
        """
        self.assertEqual(self.run_code(code, "factorial", 5), 120)

    def test_function_return_without_value(self):
        code = """
        fun test() {
            return;
        }
        """
        self.assertIsNone(self.run_code(code, "test"))

    def test_error_undefined_function(self):
        code = """
        fun test() {
            return undefined_func();
        }
        """
        with self.assertRaises(InterpreterNameError):
            self.run_code(code, "test")

    def test_error_wrong_number_of_arguments(self):
        code = """
        fun add(a, b) {
            return a + b;
        }
        fun test() {
            return add(1, 2, 3);
        }
        """
        with self.assertRaises(InterpreterRuntimeError) as ctx:
            self.run_code(code, "test")
        self.assertIn("expects 2 arguments", str(ctx.exception))

    def test_builtin_typeof(self):
        code = """
        fun test() {
            return typeof(42);
        }
        """
        self.assertEqual(self.run_code(code, "test"), "int")

    def test_complex_program_calculator(self):
        # Program używa floatów, aby uniknąć błędów typowania przy sumowaniu
        # wyniku dzielenia (float) z resztą wyników.
        code = """
        fun add(a, b) {
            return a + b;
        }
        
        fun subtract(a, b) {
            return a - b;
        }
        
        fun multiply(a, b) {
            return a * b;
        }
        
        fun divide(a, b) {
            if (b == 0.0) {
                return 0.0;
            }
            return a / b;
        }
        
        fun test() {
            x = 10.0;
            y = 5.0;
            
            sum = add(x, y);
            diff = subtract(x, y);
            prod = multiply(x, y);
            quot = divide(x, y);
            
            return sum + diff + prod + quot;
        }
        """
        # 15.0 + 5.0 + 50.0 + 2.0 = 72.0
        self.assertEqual(self.run_code(code, "test"), 72.0)

    def test_complex_program_nested_loops_pattern(self):
        code = """
        fun test() {
            result = 0;
            i = 1;
            while (i <= 3) {
                j = 1;
                while (j <= 3) {
                    k = 1;
                    while (k <= 3) {
                        result = result + 1;
                        k = k + 1;
                    }
                    j = j + 1;
                }
                i = i + 1;
            }
            return result;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 27)

    def test_match_conditional_mode(self):
        code = """
        fun test() {
            x = 10;
            res = 0;
            match x as val {
                val > 5 => {
                    res = 1;
                }
                val < 5 => {
                    res = 2;
                }
            }
            return res;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 1)

    def test_match_positional_simple(self):
        code = """
        fun test() {
            match 10 as x {
                [is string] => { return 1; }
                [is int] => { return 2; }
            }
            return 0;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 2)

    def test_match_positional_wildcard(self):
        code = """
        fun test() {
            match 42 as x {
                [_] => { return true; }
            }
            return false;
        }
        """
        self.assertTrue(self.run_code(code, "test"))

    def test_match_execute_all_logic(self):
        code = """
        fun test() {
            res = 0;
            x = 10;
            match x {
                [> 5] => { 
                    res = res + 1; 
                }
                [10] => { 
                    res = res + 10; 
                }
                [< 0] => { 
                    res = res + 100; 
                }
            }
            return res;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 11)

    def test_match_default_runs(self):
        code = """
        fun test() {
            x = 13;
            match x {
                [> 10] => { return 1; }
                 default => { return 100; }
            }
        }
        """
        self.assertEqual(self.run_code(code, "test"), 1)

    def test_match_multiple_subjects(self):
        code = """
        fun test() {
            match 10, "hello" {
                [> 5, is int] => { return 1; }
                [> 5, is string] => { return 2; }
            }
            return 0;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 2)

    def test_match_alias_usage_in_body(self):
        code = """
        fun test() {
            match 100 as result {
                [is int] => { 
                    return result * 2; 
                }
            }
            return 0;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 200)

    def test_match_complex_mixed_mode(self):
        code = """
        fun test_complex() {
            res = 0;
            status_code = 404;
            
            match status_code, "admin" as mode, 85.5 as score {
                [404, is string, _] => {
                    res = res + 1;
                }
                mode == "admin" and score > 50.0 => {
                    res = res + 10;
                }
                [> 400, != "user", >= 80.0] => {
                    res = res + 100;
                }
                [200, _, _] => {
                    res = res + 1000;
                }
            }
            return res;
        }
        """
        self.assertEqual(self.run_code(code, "test_complex"), 111)

    def test_match_nested_logic(self):
        code = """
        fun test_nested() {
            x = 10;
            y = 20;
            final_res = 0;

            match x as val_x {
                val_x > 5 => {
                    match y {
                        [> 15] => {
                            final_res = final_res + 1;
                        }
                        [< 10] => {
                            final_res = final_res + 9999;
                        }
                    }
                }
                [10] => {
                    match val_x {
                        [10] => {
                            final_res = final_res + 10;
                        }
                    }
                }
            }
            return final_res;
        }
        """
        self.assertEqual(self.run_code(code, "test_nested"), 11)

    def test_args_passed_from_python(self):
        code = """
        fun check_types(i, f, s, b) {
            if (typeof(i) == "int" and 
                typeof(f) == "float" and 
                typeof(s) == "string" and 
                typeof(b) == "bool") {
                return true;
            }
            return false;
        }
        """
        self.assertTrue(self.run_code(code, "check_types", 42, 3.14, "Matcha", True))

    def test_args_as_expressions(self):
        code = """
        fun compute(val) {
            return val;
        }
        
        fun test() {
            x = 10;
            y = 20;
            return compute((x + y) * 2);
        }
        """
        self.assertEqual(self.run_code(code, "test"), 60)

    def test_args_pass_by_value_simulation(self):
        code = """
        fun modify_arg(x) {
            x = 999;
            return x;
        }
        fun test() {
            val = 10;
            modify_arg(val);
            return val;
        }
        """
        self.assertEqual(self.run_code(code, "test"), 10)

    def test_args_shadowing_global(self):
        code = """
        fun test_shadow(x) {
            return x;
        }
        fun test() {
            x = 100;
            return test_shadow(5);
        }
        """
        self.assertEqual(self.run_code(code, "test"), 5)


if __name__ == "__main__":
    unittest.main()
