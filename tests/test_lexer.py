import unittest
from src.reader import CharReader
from src.lexer import Lexer
from src.token_type import TokenType

class TestLexer(unittest.TestCase):
    
    def get_tokens(self, text):
        reader = CharReader(text)
        lexer = Lexer(reader)
        tokens = []
        while True:
            tok = lexer.get_next_token()
            if tok.type == TokenType.EOF:
                break
            tokens.append(tok)
        return tokens

    def test_empty_and_whitespace(self):
        """ Test: pusty plik, i białe znaki """
        self.assertEqual(len(self.get_tokens("")), 0)
        self.assertEqual(len(self.get_tokens("   \t  \n  ")), 0)

    def test_comments(self):
        """Test: Komentarze są ignorowane"""
        code = """
        // To jest komentarz
        var x = 1; // Komentarz na końcu linii
        // Inny komentarz
        """
        tokens = self.get_tokens(code)
        self.assertEqual(len(tokens), 5) # var, x, =, 1, ;
        self.assertEqual(tokens[0].type, TokenType.VAR)
        self.assertEqual(tokens[3].value, 1)

    def test_numbers_simple(self):
        """Test: liczby """
        tokens = self.get_tokens("123 0 45.67 0.1")
        
        self.assertEqual(tokens[0].type, TokenType.INT_LITERAL)
        self.assertEqual(tokens[0].value, 123)
        
        self.assertEqual(tokens[1].type, TokenType.INT_LITERAL)
        self.assertEqual(tokens[1].value, 0)
        
        self.assertEqual(tokens[2].type, TokenType.FLOAT_LITERAL)
        self.assertAlmostEqual(tokens[2].value, 45.67)
        
        self.assertEqual(tokens[3].type, TokenType.FLOAT_LITERAL)
        self.assertAlmostEqual(tokens[3].value, 0.1)

    def test_strings_complex(self):
        """Test: Stringi """
        code = r'"A" "A\nB" "A\"B" "A\\B"'
        tokens = self.get_tokens(code)
        
        self.assertEqual(tokens[0].value, "A")
        self.assertEqual(tokens[1].value, "A\nB") 
        self.assertEqual(tokens[2].value, 'A"B')  
        self.assertEqual(tokens[3].value, r'A\B') 

    def test_keywords_vs_identifiers(self):
        """Test: Rozróżnianie keywords od literałów (nazw)"""
        tokens = self.get_tokens("if if_literal match match_literal")
        
        self.assertEqual(tokens[0].type, TokenType.IF)
        
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "if_literal")
        
        self.assertEqual(tokens[2].type, TokenType.MATCH)
        
        self.assertEqual(tokens[3].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[3].value, "match_literal")

    def test_operators_checknext(self):
        """Test: Operatory jedno i dwu znakowe"""
        code = "= == => < <= ! !="
        tokens = self.get_tokens(code)
        
        types = [t.type for t in tokens]
        expected = [
            TokenType.ASSIGN, TokenType.EQUAL, TokenType.ARROW,
            TokenType.LESS, TokenType.LESS_EQ,
            TokenType.NOT, TokenType.NOT_EQUAL
        ]
        self.assertEqual(types, expected)

    def test_all_symbols(self):
        """Test 7: Reszta symboli """
        code = "+ - * / ( ) { } [ ] , ; _"
        tokens = self.get_tokens(code)
        
        expected = [
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
            TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE,
            TokenType.LBRACKET, TokenType.RBRACKET, TokenType.COMMA, TokenType.SEMICOLON,
            TokenType.WILDCARD
        ]
        self.assertEqual([t.type for t in tokens], expected)

    # TESTY NEGATYWNE 

    def test_error_unclosed_string(self):
        """Test Negatywny: Niezamknięty string"""
        tokens = self.get_tokens('"To jest string bez konca')
        
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.UNKNOWN)
        self.assertEqual("Niezamknięty string", str(tokens[0].value))

    def test_error_unknown_char(self):
        """Test Negatywny: Nieznany znak"""
        tokens = self.get_tokens("var x = @;")
        
        self.assertEqual(tokens[3].type, TokenType.UNKNOWN)
        self.assertEqual(tokens[3].value, '@')

    def test_float(self):
        """Test Negatywny: float bez czesci dziesietnej"""

        tokens = self.get_tokens("12.")
        self.assertEqual(tokens[0].type, TokenType.FLOAT_LITERAL)
        self.assertEqual(tokens[0].value, 12.0)

    def test_sticky_operators(self):
        """Test: Sklejone operatory """
        # Kod: =)>asd+_
        code = "=)>asd+_"
        tokens = self.get_tokens(code)
        
        expected_types = [
            TokenType.ASSIGN,       # =
            TokenType.RPAREN,       # )
            TokenType.GREATER,      # >
            TokenType.IDENTIFIER,   # asd
            TokenType.PLUS,         # +
            TokenType.WILDCARD,     # _
   
        ]
        
        for i, token in enumerate(tokens):
            self.assertEqual(token.type, expected_types[i])
            
        self.assertEqual(tokens[3].value, "asd")

    def test_sticky_math(self):
        """Test: sklejone równania """
        # Kod: 1+2*3/4
        tokens = self.get_tokens("1+2*3/4")
        
        self.assertEqual(tokens[0].value, 1)
        self.assertEqual(tokens[1].type, TokenType.PLUS)
        self.assertEqual(tokens[2].value, 2)
        self.assertEqual(tokens[3].type, TokenType.MULTIPLY)
        self.assertEqual(tokens[4].value, 3)
        self.assertEqual(tokens[5].type, TokenType.DIVIDE)
        self.assertEqual(tokens[6].value, 4)

    def test_sticky_brackets(self):
        """Test: sklejone nawiasy i klamry """

        tokens = self.get_tokens("fn(){return(0);}")
        
        expected_types = [
            TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE,
            TokenType.RETURN, TokenType.LPAREN, TokenType.INT_LITERAL, TokenType.RPAREN,
            TokenType.SEMICOLON, TokenType.RBRACE
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, token in enumerate(tokens):
            self.assertEqual(token.type, expected_types[i])

    def test_tricky_comparisons(self):
        """Test: operatory assign i equal"""
        # Powinno być: ASSIGN, EQUAL, EQUAL, ASSIGN 
        tokens = self.get_tokens("= == ===")
        
        self.assertEqual(tokens[0].type, TokenType.ASSIGN)
        self.assertEqual(tokens[1].type, TokenType.EQUAL)
        self.assertEqual(tokens[2].type, TokenType.EQUAL)
        self.assertEqual(tokens[3].type, TokenType.ASSIGN)
if __name__ == '__main__':
    unittest.main()