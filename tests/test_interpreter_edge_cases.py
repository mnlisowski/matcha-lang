import pytest
from src.interpreter.environment import RuntimeError, TypeError, NameError, ValueError, ArgumentError


class TestEdgeCasesNegative:
    """Testy negatywne i edge case'y."""

    
    @pytest.mark.parametrize("expr", [
        "1 + 1.0",
        "1.0 + 1",
        "5 - 2.0",
        "2.0 * 3",
        "10 / 2", 
    ])
    def test_int_float_promotion(self, run, expr):
        code = f"fun main() {{ x = {expr}; return x + 1; }}"
        with pytest.raises(TypeError):
            run(code)

    @pytest.mark.parametrize("left,right", [
        ("1", '"a"'),
        ('"a"', "1"),
        ("true", "1"),
        ("1", "true"),
        ("true", '"a"'),
    ])
    def test_incompatible_addition(self, run, left, right):
        code = f"fun main() {{ return {left} + {right}; }}"
        with pytest.raises(TypeError):
            run(code)

    @pytest.mark.parametrize("op", ["-", "*", "/"])
    def test_string_string_forbidden(self, run, op):
        code = f'fun main() {{ return "a" {op} "b"; }}'
        with pytest.raises(TypeError):
            run(code)

    def test_division_by_zero_int(self, run):
        code = "fun main() { return 10 / 0; }"
        with pytest.raises(ValueError):
            run(code)

    def test_division_by_small_nuber(self, run):
        code = "fun main() { return 10.0 / 0.000000000001; }"
        with pytest.raises(ValueError):
            run(code)
     

    def test_division_by_zero_float(self, run):
        code = "fun main() { return 10.0 / 0.0; }"
        with pytest.raises(ValueError):
            run(code)

    def test_division_result_is_float(self, run):
        code = "fun main() { return 10 / 2; }"
        result = run(code)
        assert result == 5.0
        assert isinstance(result, float)

    # logiczne

    @pytest.mark.parametrize("expr", [
        "1 and true",
        "true and 1",
        "0 or false",
        '"" and true',
        "!1",
        "!0",
        '!"hello"',
    ])
    def test_logical_operators_require_bool(self, run, expr):
        code = f"fun main() {{ return {expr}; }}"
        with pytest.raises(TypeError):
            run(code)

    # if/while

    @pytest.mark.parametrize("condition", [
        "1",
        "0",
        '""',
        '"true"',
        "1.0",
    ])
    def test_if_requires_bool(self, run, condition):
        code = f"""fun main() {{ if ({condition}) {{ return 1; }} return 0; }}"""
        with pytest.raises(TypeError):
            run(code)

    @pytest.mark.parametrize("condition", [
        "1",
        '""',
    ])
    def test_while_requires_bool(self, run, condition):
        code = f"fun main() {{ while ({condition}) {{ break; }} return 0; }}"
        with pytest.raises(TypeError):
            run(code)

   # break/continue

    def test_break_outside_loop(self, run):
        code = "fun main() { break; }"
        with pytest.raises(RuntimeError):
            run(code)

    def test_continue_outside_loop(self, run):
        code = "fun main() { continue; }"
        with pytest.raises(RuntimeError):
            run(code)

    def test_break_in_if_outside_loop(self, run):
        code = "fun main() { if (true) { break; } }"
        with pytest.raises(RuntimeError):
            run(code)

    def test_break_in_match_outside_loop(self, run):
        code = """
        fun main() {
            match 1 as x {
                [1] => { break; }
            }
        }
        """
        with pytest.raises(RuntimeError):
            run(code)

    # funkcje

    def test_undefined_function(self, run):
        code = "fun main() { return nieistnieje(); }"
        with pytest.raises(NameError):
            run(code)

    def test_undefined_variable(self, run):
        code = "fun main() { return x; }"
        with pytest.raises(NameError):
            run(code)

    @pytest.mark.parametrize("args,expected_error", [
        ("", ArgumentError),      # za mało
        ("1", ArgumentError),     # za mało  
        ("1,2,3", ArgumentError), # za dużo
    ])
    def test_wrong_argument_count(self, run, args, expected_error):
        code = f"""
        fun add(a, b) {{ return a + b; }}
        fun main() {{ return add({args}); }}
        """
        with pytest.raises(expected_error):
            run(code)

    def test_recursion_limit(self, run):
        code = """
        fun infinite(n) {
            return infinite(n + 1);
        }
        fun main() {
            return infinite(0);
        }
        """
        with pytest.raises((RuntimeError, RecursionError)):
            run(code)

    # scope zmiennych

    def test_variable_not_visible_outside_block(self, run):
        code = """
        fun main() {
            if (true) {
                x = 10;
            }
            return x;
        }
        """
        with pytest.raises(NameError):
            run(code)

    def test_variable_shadowing(self, run):
        code = """
        fun test(x) {
            return x;
        }
        fun main() {
            x = 100;
            return test(5);
        }
        """
        assert run(code) == 5

    # match edge cases

    def test_match_no_matching_branch_no_default(self, run):
        code = """
        fun main() {
            match 9 {
                [1] => { return 1; },
                [2] => { return 2; }
            }
            return 0;
        }
        """
        assert run(code) == 0

    def test_match_all_branches_execute(self, run_with_output):
        code = """
        fun main() {
            x = 0;
            match 10 as n {
                [> 5] => { x = x + 1; },
                [> 0] => { x = x + 10; },
                [== 10] => { x = x + 100; }
            }
            return x;
        }
        """
        assert run_with_output(code)[0] == 111

    def test_match_default_skipped_when_matched(self, run):
        code = """
        fun main() {
            match 10 {
                [10] => { return 1; },
                default => { return 2; }
            }
        }
        """
        assert run(code) == 1

    def test_match_default_executes_when_nothing_matches(self, run):
        code = """
        fun main() {
            match 9 {
                [1] => { return 1; },
                default => { return 2; }
            }
        }
        """
        assert run(code) == 2

    def test_match_empty_header(self, run):
        code = """
        fun main() {
            x = 10;
            match {
                x > 5 => { return 1; },
                default => { return 2; }
            }
        }
        """
        assert run(code) == 1

    def test_match_type_pattern_bool_vs_int(self, run):
        code = """
        fun main() {
            match true {
                [is int] => { return "int"; },
                [is bool] => { return "bool"; }
            }
        }
        """
        assert run(code) == "bool"

    def test_match_wildcard_always_matches(self, run):
        code = """
        fun main() {
            match 12345 {
                [_] => { return "matched"; }
            }
        }
        """
        assert run(code) == "matched"

    def test_match_and_pattern(self, run):
        code = """
        fun main() {
            match 15 {
                [> 10 AND < 20] => { return "in range"; },
                default => { return "out of range"; }
            }
        }
        """
        assert run(code) == "in range"

    def test_match_and_pattern_fails(self, run):
        code = """
        fun main() {
            match 25 {
                [> 10 AND < 20] => { return "in range"; },
                default => { return "out of range"; }
            }
        }
        """
        assert run(code) == "out of range"


    def test_return_without_value(self, run):
        """Return bez wartości zwraca None/null."""
        code = """
        fun nothing() {
            return;
        }
        fun main() {
            x = nothing();
            if (x == 0) { return 1; }
            return 0;
        }
        """
        with pytest.raises(TypeError):
            run(code)

    def test_return_stops_execution(self, run):
        code = """
        fun main() {
            return 1;
            return 2;
        }
        """
        assert run(code) == 1

    def test_return_in_while(self, run):
        code = """
        fun main() {
            i = 0;
            while (true) {
                i = i + 1;
                if (i == 5) {
                    return i;
                }
            }
            return 0;
        }
        """
        assert run(code) == 5

    def test_return_in_nested_if(self, run):
        code = """
        fun main() {
            if (true) {
                if (true) {
                    return 42;
                }
            }
            return 0;
        }
        """
        assert run(code) == 42

    # operatory porównania

    @pytest.mark.parametrize("left,right", [
        ("1", "1.0"),
        ("1.0", "1"),
        ('"1"', "1"),
    ])
    def test_comparison_type_not_match(self, run, left, right):
        code = f"fun main() {{ return {left} == {right}; }}"
        with pytest.raises(TypeError):
            run(code)

    def test_compare_strings(self, run):
        """Porównanie stringów."""
        code = 'fun main() { return "abc" == "abc"; }'
        assert run(code) == True

    def test_compare_bools(self, run):
        code = "fun main() { return true == true; }"
        assert run(code) == True


    def test_empty_string(self, run):
        code = 'fun main() { return "" + "a"; }'
        assert run(code) == "a"

    def test_zero_int(self, run):
        code = "fun main() { return 0; }"
        assert run(code) == 0

    def test_zero_float(self, run):
        code = "fun main() { return 0.0; }"
        assert run(code) == 0.0

    def test_negative_numbers(self, run):
        code = "fun main() { return -5 + -3; }"
        assert run(code) == -8

    def test_print_void_function_result(self, run):
        code = """
        fun void_fun() {
            x = 1;
        }
        fun main() {
            print(void_fun());
            return 0;
        }
        """
        with pytest.raises(RuntimeError):
            run(code)

    def test_use_void_result_in_expression(self, run):
        """Użycie wyniku void funkcji w wyrażeniu."""
        code = """
        fun void_fun() {}
        fun main() {
            x = void_fun() + 1;
            return x;
        }
        """
        #  None + 1
        with pytest.raises(TypeError):
            run(code)

    def test_void_result_in_condition(self, run):
        """Użycie wyniku void funkcji w warunku."""
        code = """
        fun void_fun() {}
        fun main() {
            if (void_fun()) {
                return 1;
            }
            return 0;
        }
        """
        # None nie jest bool 
        with pytest.raises(TypeError):
            run(code)