import unittest
import io
from src.reader import CharReader
from src.lexer import (
    Lexer, 
    tokens_generator, 
    LexerError,
    HardLimitError,
    InvalidCharacterError,
    UnterminatedStringError,
    InvalidEscapeSequenceError,
    IntegerOverflowError,
    SoftLimitWarning
)
from src.token_type import TokenType


class TestLexer(unittest.TestCase):
    def setUp(self):
        self.errors = []

    def error_handler(self, error):
        self.errors.append(error)

    def get_lexer(self, text, **kwargs):
        stream = io.StringIO(text)
        reader = CharReader(stream)
        return Lexer(reader, error_handler=self.error_handler, **kwargs)

    def get_tokens(self, text, **kwargs):
        return list(tokens_generator(self.get_lexer(text, **kwargs)))

    # Helpery

    def assert_single_token(self, input_code, expected_type, expected_value=None):
        tokens = self.get_tokens(input_code)
        self.assertEqual(tokens[0].type, expected_type)
        if expected_value is not None:
            self.assertEqual(tokens[0].value, expected_value)

    def assert_token_types(self, input_code, expected_types):
        tokens = self.get_tokens(input_code)
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type, f"Token {i} nie zgadza się")

    # Testy EOF i białych znaków

    def test_eof_multiple_calls(self):
        """Test: Wielokrotne wywołanie po osiągnięciu EOF"""
        lexer = self.get_lexer("")

        eof1 = lexer.get_next_token()
        eof2 = lexer.get_next_token()
        eof3 = lexer.get_next_token()

        for eof in [eof1, eof2, eof3]:
            self.assertEqual(eof.type, TokenType.EOF)

        self.assertEqual(eof1.position, eof2.position)
        self.assertEqual(eof2.position, eof3.position)

    def test_empty_and_whitespace(self):
        """Test: pusty plik i białe znaki"""
        cases = [
            ("puste", ""),
            ("spacje", "   "),
            ("tabulatory", "\t\t\t"),
            ("nowe linie", "\n\n\n"),
            ("powrót karetki", "\r\r"),
            ("mieszane", "   \t  \n \r "),
        ]

        for name, input_code in cases:
            with self.subTest(case=name):
                tokens = self.get_tokens(input_code)
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].type, TokenType.EOF)

    # Testy komentarzy

    def test_comments(self):
        """Test: Komentarze jako tokeny"""
        cases = [
            ("prosty", "// comment", " comment"),
            ("pusty", "//", ""),
            ("ze spacjami", "//   text  ", "   text  "),
            ("tylko /", "//////", "////"),
        ]

        for name, input_code, expected_value in cases:
            with self.subTest(case=name):
                self.assert_single_token(input_code, TokenType.COMMENT, expected_value)

    def test_comment_in_code(self):
        """Test: Komentarz w kodzie"""
        tokens = self.get_tokens("var x = 1; // comment")
        self.assertEqual(len(tokens), 7)  # var, x, =, 1, ;, comment, EOF
        self.assertEqual(tokens[5].type, TokenType.COMMENT)
        self.assertEqual(tokens[5].value, " comment")

    # Testy liczb

    def test_int_literals(self):
        """Test: Literały intów"""
        cases = [
            ("zero", "0", 0),
            ("jeden", "1", 1),
            ("dwie cyfry", "42", 42),
            ("max_int", "2147483647", 2147483647),
        ]

        for name, input_code, expected_value in cases:
            with self.subTest(case=name):
                self.assert_single_token(
                    input_code, TokenType.INT_LITERAL, expected_value
                )

    def test_int_overflow(self):
        """Test: Overflow intów (teraz zwraca INT_LITERAL + Warning)"""
        input_code = "2147483648"
        tokens = self.get_tokens(input_code)
        
        self.assertEqual(tokens[0].type, TokenType.INT_LITERAL)

        self.assertTrue(any(isinstance(e, IntegerOverflowError) for e in self.errors))
        self.assertIn("overflow", str(self.errors[0]).lower())

    def test_float_literals(self):
        """Test: Literały floatów"""
        cases = [
            ("zero", "0.0", 0.0),
            ("half", "0.5", 0.5),
            ("pi_approx", "3.14", 3.14),
            ("multiple_digits", "123.456", 123.456),
            ("no_fractional", "12.", 12.0),
            ("precision", "0.123456789", 0.123456789),
        ]

        for name, input_code, expected_value in cases:
            with self.subTest(case=name):
                tokens = self.get_tokens(input_code)
                self.assertEqual(tokens[0].type, TokenType.FLOAT_LITERAL)
                self.assertAlmostEqual(tokens[0].value, expected_value, places=9)

    def test_incorrect_float(self):
        """Test: Test negatywny floata (.5) - kropka na początku"""
  
        input_code = ".5"
        with self.assertRaises(InvalidCharacterError):
            self.get_tokens(input_code)


    def test_string_literals(self):
        """Test: Literały stringów"""
        cases = [
            ("empty", '""', ""),
            ("single_char", '"A"', "A"),
            ("word", '"Hello"', "Hello"),
            ("with_spaces", '"Hello World"', "Hello World"),
            ("newline", r'"A\nB"', "A\nB"),
            ("tab", r'"A\tB"', "A\tB"),
            ("quote", r'"A\"B"', 'A"B'),
            ("backslash", r'"A\\B"', "A\\B"),
        ]

        for name, input_code, expected_value in cases:
            with self.subTest(case=name):
                self.assert_single_token(
                    input_code, TokenType.STRING_LITERAL, expected_value
                )

    def test_string_errors(self):
        """Test: Błędy w stringach (zwracają token + warning)"""
        
     
        self.errors = []
        tokens = self.get_tokens(r'"A\xB"')
     
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL)
     
        self.assertTrue(any(isinstance(e, InvalidEscapeSequenceError) for e in self.errors))

        # Niezamknięty string
        self.errors = []
        tokens = self.get_tokens('"Unclosed')
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL)
        self.assertEqual(tokens[0].value, "Unclosed")
        self.assertTrue(any(isinstance(e, UnterminatedStringError) for e in self.errors))

    def test_string_unicode(self):
        """Test: Unicode w stringach"""
        tokens = self.get_tokens('"Hello 世界 🌍"')
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL)
        self.assertIn("世界", tokens[0].value)

    # Testy identyfikatorów
    def test_identifiers(self):
        """Test: Identyfikatory"""
        cases = [
            ("single_char", "x", "x"),
            ("word", "abc", "abc"),
            ("camelCase", "myVariable", "myVariable"),
            ("with_underscore", "_private", "_private"),
            ("trailing_underscore", "test_", "test_"),
            ("with_digits", "var123", "var123"),
        ]

        for name, input_code, expected_value in cases:
            with self.subTest(case=name):
                self.assert_single_token(
                    input_code, TokenType.IDENTIFIER, expected_value
                )

    def test_identifier_too_long(self):
        """Test: Zbyt długi identyfikator (Soft Limit Warning)"""
     
        long_id = "a" * 65
        tokens = self.get_tokens(long_id)
        
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertTrue(any(isinstance(e, SoftLimitWarning) for e in self.errors))
        self.assertIn("Identifier", str(self.errors[0]))

 

    def test_keywords(self):
        """Test: Słowa kluczowe"""
        cases = [
            ("fun", "fun", TokenType.FUN),
            ("return", "return", TokenType.RETURN),
            ("var", "var", TokenType.VAR),
            ("if", "if", TokenType.IF),
            ("else", "else", TokenType.ELSE),
            ("while", "while", TokenType.WHILE),
            ("match", "match", TokenType.MATCH),
            ("case", "case", TokenType.CASE),
            ("default", "default", TokenType.DEFAULT),
            ("true", "true", TokenType.TRUE),
            ("false", "false", TokenType.FALSE),
        ]

        for name, input_code, expected_type in cases:
            with self.subTest(case=name):
                self.assert_single_token(input_code, expected_type)

    def test_type_keywords(self):
        """Test: Typy danych"""
        cases = [
            ("int", "int", TokenType.TYPE_INT),
            ("string", "string", TokenType.TYPE_STR),
            ("float", "float", TokenType.TYPE_FLT),
            ("bool", "bool", TokenType.TYPE_BOOL),
        ]

        for name, input_code, expected_type in cases:
            with self.subTest(case=name):
                self.assert_single_token(input_code, expected_type)

    def test_keyword_vs_identifier(self):
        """Test: Keywords vs identyfikatory"""
        tokens = self.get_tokens("if if_var ifx xif")

        self.assertEqual(tokens[0].type, TokenType.IF)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "if_var")
        self.assertEqual(tokens[2].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[3].type, TokenType.IDENTIFIER)

 

    def test_operators(self):
        """Test: Operatory"""
        cases = [
            ("plus", "+", TokenType.PLUS),
            ("minus", "-", TokenType.MINUS),
            ("multiply", "*", TokenType.MULTIPLY),
            ("divide", "/", TokenType.DIVIDE),
            ("less", "<", TokenType.LESS),
            ("greater", ">", TokenType.GREATER),
            ("less_eq", "<=", TokenType.LESS_EQ),
            ("greater_eq", ">=", TokenType.GREATER_EQ),
            ("equal", "==", TokenType.EQUAL),
            ("not_equal", "!=", TokenType.NOT_EQUAL),
            ("not", "!", TokenType.NOT),
            ("and", "and", TokenType.AND),
            ("or", "or", TokenType.OR),
            ("assign", "=", TokenType.ASSIGN),
            ("arrow", "=>", TokenType.ARROW),
        ]

        for name, input_code, expected_type in cases:
            with self.subTest(case=name):
                self.assert_single_token(input_code, expected_type)

    def test_invalid_operators(self):
        """Test: Nieprawidłowe znaki (rzucają InvalidCharacterError)"""
        for char in ["&", "|"]:
            with self.subTest(char=char):
                with self.assertRaises(InvalidCharacterError):
                    self.get_tokens(char)

    def test_tricky_equals(self):
        """Test: Trudne przypadki z ="""
        cases = [
            ("single", "=", [TokenType.ASSIGN]),
            ("double", "==", [TokenType.EQUAL]),
            ("triple", "===", [TokenType.EQUAL, TokenType.ASSIGN]),
            ("quad", "====", [TokenType.EQUAL, TokenType.EQUAL]),
        ]

        for name, input_code, expected_types in cases:
            with self.subTest(case=name):
                self.assert_token_types(input_code, expected_types)

   

    def test_punctuation(self):
        """Test: Znaki interpunkcyjne"""
        cases = [
            ("lparen", "(", TokenType.LPAREN),
            ("rparen", ")", TokenType.RPAREN),
            ("lbrace", "{", TokenType.LBRACE),
            ("rbrace", "}", TokenType.RBRACE),
            ("lbracket", "[", TokenType.LBRACKET),
            ("rbracket", "]", TokenType.RBRACKET),
            ("comma", ",", TokenType.COMMA),
            ("semicolon", ";", TokenType.SEMICOLON),
            ("wildcard", "_", TokenType.WILDCARD),
        ]

        for name, input_code, expected_type in cases:
            with self.subTest(case=name):
                self.assert_single_token(input_code, expected_type)

 

    def test_sticky_tokens(self):
        """Test: Tokeny bez spacji"""
        cases = [
            (
                "operators",
                "=)>asd+_",
                [
                    TokenType.ASSIGN,
                    TokenType.RPAREN,
                    TokenType.GREATER,
                    TokenType.IDENTIFIER,
                    TokenType.PLUS,
                    TokenType.WILDCARD,
                ],
            ),
            (
                "math",
                "1+2*3",
                [
                    TokenType.INT_LITERAL,
                    TokenType.PLUS,
                    TokenType.INT_LITERAL,
                    TokenType.MULTIPLY,
                    TokenType.INT_LITERAL,
                ],
            ),
            (
                "brackets",
                "fn(){}",
                [
                    TokenType.IDENTIFIER,
                    TokenType.LPAREN,
                    TokenType.RPAREN,
                    TokenType.LBRACE,
                    TokenType.RBRACE,
                ],
            ),
        ]

        for name, input_code, expected_types in cases:
            with self.subTest(case=name):
                self.assert_token_types(input_code, expected_types)

    def test_complex_expression(self):
        """Test: Złożone wyrażenie"""
        tokens = self.get_tokens("x==(y+1)and z!=0")

        expected = [
            (TokenType.IDENTIFIER, "x"),
            (TokenType.EQUAL, None),
            (TokenType.LPAREN, None),
            (TokenType.IDENTIFIER, "y"),
            (TokenType.PLUS, None),
            (TokenType.INT_LITERAL, 1),
            (TokenType.RPAREN, None),
            (TokenType.AND, None),
            (TokenType.IDENTIFIER, "z"),
            (TokenType.NOT_EQUAL, None),
            (TokenType.INT_LITERAL, 0),
        ]

        for i, (exp_type, exp_val) in enumerate(expected):
            self.assertEqual(tokens[i].type, exp_type)
            if exp_val is not None:
                self.assertEqual(tokens[i].value, exp_val)

   

    def test_unknown_characters(self):
        """Test: Nieznane znaki rzucają wyjątek"""
        for char in ["@", "#", "$", "%", "^", "`", "~"]:
            with self.subTest(char=char):
                with self.assertRaises(InvalidCharacterError):
                    self.get_tokens(char)

 

    def test_simple_function(self):
        """Test: Prosta funkcja"""
        code = """
        fun add(a, b) {
            return a + b;
        }
        """
        tokens = self.get_tokens(code)

        self.assertEqual(tokens[0].type, TokenType.FUN)
        self.assertEqual(tokens[1].value, "add")
        self.assertTrue(any(t.type == TokenType.RETURN for t in tokens))

    def test_control_structures(self):
        """Test: Struktury kontrolne"""
        cases = [
            ("if_else", "if (x > 0) {} else {}", [TokenType.IF, TokenType.ELSE]),
            ("while", "while (i < 10) {}", [TokenType.WHILE]),
            ("match", "match x { case 1 => {} }", [TokenType.MATCH, TokenType.CASE]),
        ]

        for name, code, expected_keywords in cases:
            with self.subTest(case=name):
                tokens = self.get_tokens(code)
                token_types = [t.type for t in tokens]
                for keyword in expected_keywords:
                    self.assertIn(keyword, token_types)

    # Testy limitów (Hard Limits)

    def test_hard_limits(self):
        """Test: Hard limity rzucają HardLimitError"""
        cases = [
            ("long_string", '"' + "a" * 11000 + '"', {"hard_max_string": 10240}),
            ("long_identifier", "a" * 700, {"hard_max_identifier": 640}),
            ("long_comment", "//" + "x" * 6000, {"hard_max_comment": 5120}),
            ("long_int", "2" * 21, {"hard_max_digits": 20}),
        ]

        for name, input_code, limits in cases:
            with self.subTest(case=name):
                # Przekazujemy limity do konstruktora Lexera
                with self.assertRaises(HardLimitError):
                    self.get_tokens(input_code, **limits)

 

    def test_edge_cases(self):
        """Test: Przypadki brzegowe"""
        with self.subTest(case="merged_floats"):
          
            try:
                tokens = self.get_tokens("1.2.3")
          
                self.assertEqual(tokens[0].type, TokenType.FLOAT_LITERAL)
                self.assertEqual(tokens[0].value, 1.2)
            except InvalidCharacterError:
              
                pass

        with self.subTest(case="nested_parens"):
            tokens = self.get_tokens("((()))")

            expected_types = [
                TokenType.LPAREN,
                TokenType.LPAREN,
                TokenType.LPAREN,
                TokenType.RPAREN,
                TokenType.RPAREN,
                TokenType.RPAREN,
                TokenType.EOF,
            ]

            self.assertEqual(len(tokens), len(expected_types))
            for i, expected in enumerate(expected_types):
                self.assertEqual(tokens[i].type, expected, f"Błąd na indeksie {i}")

        with self.subTest(case="no spaces"):
            tokens = self.get_tokens("var\nx\r\n=\r5;")

            expected_types = [
                TokenType.VAR,
                TokenType.IDENTIFIER,
                TokenType.ASSIGN,
                TokenType.INT_LITERAL,
                TokenType.SEMICOLON,
                TokenType.EOF,
            ]

            expected_values = [None, "x", None, 5, None, None]

            for i, (exp_type, exp_value) in enumerate(
                zip(expected_types, expected_values)
            ):
                self.assertEqual(tokens[i].type, exp_type, exp_value)


if __name__ == "__main__":
    unittest.main()