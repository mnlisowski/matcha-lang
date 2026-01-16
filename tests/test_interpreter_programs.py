import pytest
from src.interpreter.environment import RuntimeError, TypeError, NameError, ValueError

class TestAlgoritms:
    def test_fibonacci(self, run):
        code = """
        fun fib(n) {
            if (n <=1) {
            return n;
            }
            return fib(n-1) + fib(n-2);
        }
        fun main() {
            return fib(20);
        }
        """
        assert run(code) == 6765

    @pytest.mark.parametrize("factor, result", [
        ("1", 1),
        ("10", 3628800),
        pytest.param("20", ValueError, id="overflow"),
    ])
    def test_factorial_recursion(self, run, factor, result):
        code = f"""
        fun factorial(n) {{
            if (n <= 1) {{return 1;}}
            return n * factorial(n-1);
        }}
        fun main() {{
            return factorial({factor});
        }}"""
        
        if isinstance(result, type):
            with pytest.raises(result):
                run(code)
        else:
            assert run(code) == result
        
    def test_gcd(self, run):
        code = """
        fun gcd(a, b) {
            if (b == 0) { return a; }
            if (a > b) {
                return gcd(a - b, b);
            }
            return gcd(a, b - a);
        }
        fun main() {
            return gcd(48, 18);
        }
        """
        assert run(code) == 6

    def test_power_recursive(self, run):
        code = """
        fun power(base, exp) {
            if (exp == 0) { return 1; }
            return base * power(base, exp - 1);
        }
        fun main() {
            return power(2, 10);
        }
        """
        assert run(code) == 1024
   
#petle
    class TestLoops:

        def test_simple_loop(self, run):
            code = """
            fun main() {
                sum = 0;
                i = 1;
                while (i <= 3) {
                    j = 1;
                    while (j <= 3) {
                        sum = sum + i * j;
                        j = j + 1;
                    }
                    i = i + 1;
                }
                return sum;
            }
            """
            # 1*1 + 1*2 + 1*3 + 2*1 + 2*2 + 2*3 + 3*1 + 3*2 + 3*3
            # = 1+2+3 + 2+4+6 + 3+6+9 = 6 + 12 + 18 = 36
            assert run(code) == 36
        
        def nested_loop_break(self, run):
            code = """
        fun main() {
            count = 0;
            i = 0;
            while (i < 5) {
                j = 0;
                while (j < 5) {
                    if (j == 2) {
                        break;
                    }
                    count = count + 1;
                    j = j + 1;
                }
                i = i + 1;
            }
            return count;
        }
        """
            # wewnetrzna przerywa dla 2, zewnatrzna idzie 5 razy
            assert run(code) == 10

        def test_nested_loop_continue(self, run):
            code = """
            fun main() {
                sum = 0;
                i = 0;
                while (i < 5) {
                    i = i + 1;
                    if (i == 3) {
                        continue;
                    }
                    j = 0;
                    while (j < 3) {
                        j = j + 1;
                        sum = sum + 1;
                    }
                }
                return sum;
            }
            """
            # zewnetrzna 4 razy, wewnatrzna 3
            assert run(code) == 12

        def test_triple_nested_loop(self, run):
            code = """
            fun main() {
                count = 0;
                i = 0;
                while (i < 3) {
                    j = 0;
                    while (j < 3) {
                        k = 0;
                        while (k < 3) {
                            count = count + 1;
                            k = k + 1;
                        }
                        j = j + 1;
                    }
                    i = i + 1;
                }
                return count;
            }
            """
            # 3 * 3 * 3 = 27
            assert run(code) == 27

    class TestNestedConditions:

        def test_deeply_nested_if(self, run):
            code = """
            fun classify(n) {
                if (n < 0) {
                    return "negative";
                } else {
                    if (n == 0) {
                        return "zero";
                    } else {
                        if (n < 10) {
                            return "small";
                        } else {
                            if (n < 100) {
                                return "medium";
                            } else {
                                return "large";
                            }
                        }
                    }
                }
            }
            fun main() {
                return classify(50);
            }
            """
            assert run(code) == "medium"
        @pytest.mark.parametrize("value,expected", [
            (-5, "negative"),
            (0, "zero"),
            (5, "small"),
            (50, "medium"),
            (500, "large"),
        ])

        def test_classifiy_number(self, run, value, expected):
            code = f"""
            fun classify(n) {{
                if (n < 0) {{
                    return "negative";
                }} else {{
                    if (n == 0) {{
                        return "zero";
                    }} else {{
                        if (n < 10) {{
                            return "small";
                        }} else {{
                            if (n < 100) {{
                                return "medium";
                            }} else {{
                                return "large";
                            }}
                        }}
                    }}
                }}
            }}
            fun main() {{
                return classify({value});
            }}
            """
            assert run(code) == expected


        def test_complex_boolean_conditions(self, run):
            code = """
            fun check(a, b, c) {
                if ((a > 0 and b > 0)) {
                    if (a + b > 10 and c != 5) {
                        return "case1";
                    } else {
                        return "case2";
                    }
                } else {
                    if (a < 0 and b < 0) {
                        return "case3";
                    } else {
                        return "case4";
                    }
                }
            }
            fun main() {
                return check(5, 7, 3);
            }
            """
            # a=5>0, b=7>0, więc pierwszy if true
            # a+b=12>10, c=3!=5, więc "case1"
            assert run(code) == "case1"
    
    class TestMatch:

        def test_match_multiple_aliases(self, run):
            code = """
            fun main() {
                match 5 as a, 10 as b {
                    a + b == 15 => { return a * b; },
                    default => { return 0; }
                }
            }
            """
            assert run(code) == 50 

        
        @pytest.mark.parametrize("x,y,expected", [
        (5, 10, "both positive"),
        (-5, -10, "both negative"),
        (0, 100, "x is zero"),
        (100, 0, "y is zero"),
        (5, -5, "mixed signs"),
    ])
        def test_pair_classification(self, run, x, y, expected):
            """Klasyfikacja par - parametryzowane."""
            code = f"""
            fun classify_pair(x, y) {{
                match x, y {{
                    [> 0, > 0] => {{ return "both positive"; }},
                    [< 0, < 0] => {{ return "both negative"; }},
                    [== 0, _] => {{ return "x is zero"; }},
                    [_, == 0] => {{ return "y is zero"; }},
                    default => {{ return "mixed signs"; }}
                }}
            }}
            fun main() {{
                return classify_pair({x}, {y});
            }}
            """
            assert run(code) == expected

        def test_match_with_function_in_header(self, run):
            code = """
            fun square(n) {
                return n * n;
            }
            fun main() {
                match square(5) as sq {
                    [> 20] => { return sq; },
                    default => { return 0; }
                }
            }
            """
            assert run(code) == 25

        def test_match_with_complex_expression(self, run):
            code = """
            fun main() {
                a = 3;
                b = 4;
                match a * a + b * b as hyp_sq {
                    [== 25] => { return "3-4-5 triangle"; },
                    default => { return "not a 3-4-5 triangle"; }
                }
            }
            """
            assert run(code) == "3-4-5 triangle"

        def test_match_with_return_in_branch(self, run):
            code = """
            fun test(x) {
                match x {
                    [> 10] => { return "big"; },
                    [> 5] => { return "medium"; },
                    default => { return "small"; }
                }
                return "unreachable";
            }
            fun main() {
                return test(7);
            }
            """
            assert run(code) == "medium"

        def test_triple_nested_match(self, run):
            code = """
            fun deep_classify(a, b, c) {
                match a {
                    [> 0] => {
                        match b {
                            [> 0] => {
                                match c {
                                    [> 0] => { return "all positive"; },
                                    default => { return "a,b positive, c not"; }
                                }
                            },
                            default => { return "only a positive"; }
                        }
                    },
                    default => { return "a not positive"; }
                }
            }
            fun main() {
                return deep_classify(1, 2, 3);
            }
            """
            assert run(code) == "all positive"

        def test_match_in_loop(self, run):
            code = """
            fun count_types(n) {
                positives = 0;
                negatives = 0;
                zeros = 0;
                i = -n;
                while (i <= n) {
                    match i {
                        [> 0] => { positives = positives + 1; },
                        [< 0] => { negatives = negatives + 1; },
                        default => { zeros = zeros + 1; }
                    }
                    i = i + 1;
                }
                return positives;
            }
            fun main() {
                return count_types(5);
            }
            """
        
            assert run(code) == 5

    class TestScopes:

        def test_match_alias_scope(self, run):
            """Zasięg aliasów w match."""
            code = """
            fun main() {
                result = 0;
                match 10 as x, 20 as y {
                    true => {
                        result = x + y;
                    }
                }
                // x i y nie powinny być dostępne tutaj
                return result;
            }
            """
            assert run(code) == 30

        def test_variable_shadowing(self, run):
            code = """
            fun outer() {
                x = 10;
                return inner(x);
            }
            fun inner(x) {
                x = x + 5;
                return x;
            }
            fun main() {
                return outer();
            }
            """
            assert run(code) == 15

    class TestScenarios:

        def test_mega_integration_robot(self, run):
            code = """
            fun mod(val, div) {
                temp = val;
                while (temp >= div) {
                    temp = temp - div;
                }
                return temp;
            }

            // 2. Rekurencja: Obliczanie bonusu 
            fun charge_battery(level) {
                if (level <= 0) { return 0; }
                return level + charge_battery(level - 1);
            }

            fun scan_tile(pos) {
                match pos {
                    // Pola specjalne (ujemne lub zero) - reset
                    [<= 0] => { return 0; },
                    
                    // Pole 'magiczne' nr 10 - duży bonus
                    [== 10] => { return 100; },
                    
                    // Sprawdzamy czy pole jest w bezpiecznym zakresie typów
                    [is int AND > 20] => { return -50; }, // Przepaść
                    
                    default => {
                        // Zwykłe pole: Parzyste = +10 pkt, Nieparzyste = -5 pkt
                        rem = mod(pos, 2);
                        match rem {
                            [0] => { return 10; },
                            default => { return -5; }
                        }
                    }
                }
            }

            fun main() {
                position = 0;
                score = 0;
                battery = 100;
                turn = 1;

                // Symulacja 15 tur ruchu
                while (turn <= 15) {
                    
                    // --- Logika ruchu ---
                    // Co 3 turę "skok" o 2 pola, w pozostałe krok o 1
                    move_dist = 1;
                    
                    rem3 = mod(turn, 3);
                    if (rem3 == 0) {
                        move_dist = 2;
                    }

                    // Aktualizacja pozycji
                    position = position + move_dist;
                    
                    // Koszt ruchu
                    battery = battery - move_dist;

                    // --- Analiza pola (Zagnieżdżone warunki) ---
                    points = scan_tile(position);
                    
                    if (points > 0) {
                        // Dobre pole - dodajemy punkty + bonus z baterii
                        // Wywołanie rekurencyjne (np. dla 3 -> 3+2+1 = 6)
                        bonus = charge_battery(3); 
                        score = score + points + bonus;
                    } else {
                        // Złe pole lub przepaść
                        if (points == -50) {
                            // Wpadł w przepaść (pos > 20)
                            score = score - 50;
                            position = 0; // Reset pozycji
                        } else {
                            score = score + points; // Odejmuje punkty (bo points ujemne)
                        }
                    }

                    // --- Obsługa wyjścia (Break/Continue) ---
                    
                    // Jeśli brak baterii - koniec gry
                    if (battery <= 0) { break; }
                    
                    // Jeśli wynik bardzo wysoki - wygrywamy wcześniej
                    if (score >= 200) { break; }

                    turn = turn + 1;
                }

                return score;
            }
            """
        
            
            assert run(code) == 209