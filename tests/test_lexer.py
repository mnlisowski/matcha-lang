import unittest
from src.reader import CharReader
from src.lexer import Lexer
from src.token_type import TokenType

class TestLexer(unittest.TestCase):
    
    def get_tokens(self, text):
    
        # Uruchamia lekser na tekście i zwraca listę wszystkich tokenów
        
        reader = CharReader(text)
        lexer = Lexer(reader)
        tokens = []
        
        while True:
            tok = lexer.get_next_token()
            if tok.type == TokenType.EOF:
                break
            tokens.append(tok)
            
        return tokens

    def test_empty_source(self):
        # Pusty tekst 
        tokens = self.get_tokens("")
        self.assertEqual(len(tokens), 0)

    def test_skip_whitespace(self):
        # same białe znaki
        tokens = self.get_tokens("   \n  \t  ")
        self.assertEqual(len(tokens), 0)

    def test_skip_comments(self):
        # Sam komentarz 
        tokens = self.get_tokens("// to jest komentarz")
        self.assertEqual(len(tokens), 0)

    def test_skip_mixed(self):
        # białe znaki i komentarze -
        code = """
        // komentarz 1
             // komentarz 2
        
        """
        tokens = self.get_tokens(code)
        self.assertEqual(len(tokens), 0)

    def test_stops_at_code(self):
        # Lekser powinien pominąć komentarze i białe znakii zatrzymać się na znaku a
        code = "   // komentarz \n  a"
        tokens = self.get_tokens(code)
        
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.UNKNOWN)
        self.assertEqual(tokens[0].value, 'a')

    def test_multiple_unknown(self):
        code = "a b"
        tokens = self.get_tokens(code)
        
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].value, 'a')
        self.assertEqual(tokens[1].value, 'b')

if __name__ == '__main__':
    unittest.main()