from src.reader import CharReader, EOF
from src.token import Token
from src.token_type import TokenType


class Lexer:
    def __init__(self, reader):
        self.reader = reader
        self.current_char = self.reader.current()

    def advance(self):
        # zeby ciagle nie pisac self.reader.advance()
        self.current_char = self.reader.advance()

    def skip_whitespace(self):
        while self.current_char != EOF and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        # czytamytak długo, aż trafimy na koniec linii albo koniec pliku
        while self.current_char != EOF and self.current_char != "\n":
            self.advance()
        # '\n' zjadamy w get_next_token()

    def skip_all(self):
        # Wywołuje skip_whitespace i skip_comment aż do EOF lub do rzeczywistego tokenu
        while self.current_char != EOF:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == "/" and self.reader.check_next() == "/":
                self.skip_comment()
                continue

            break

    def get_next_token(self):
        self.skip_all()

        if self.current_char == EOF:
            return Token(TokenType.EOF, None, self.reader.position())

        pos = self.reader.position()
        char = self.current_char

        
        # Operatory matematyczne
        if char == '+':
            self.advance()
            return Token(TokenType.PLUS, None, pos)
        
        if char == '-':
            self.advance()
            return Token(TokenType.MINUS, None, pos)
            
        if char == '*':
            self.advance()
            return Token(TokenType.MULTIPLY, None, pos)
            
        if char == '/':
            self.advance()
            return Token(TokenType.DIVIDE, None, pos)
            
        # Nawiasy
        if char == '(':
            self.advance()
            return Token(TokenType.LPAREN, None, pos)
            
        if char == ')':
            self.advance()
            return Token(TokenType.RPAREN, None, pos)
            
        if char == '{':
            self.advance()
            return Token(TokenType.LBRACE, None, pos)
            
        if char == '}':
            self.advance()
            return Token(TokenType.RBRACE, None, pos)
            
        if char == '[':
            self.advance()
            return Token(TokenType.LBRACKET, None, pos)
            
        if char == ']':
            self.advance()
            return Token(TokenType.RBRACKET, None, pos)
            
        # Interpunkcja
        if char == ',':
            self.advance()
            return Token(TokenType.COMMA, None, pos)
            
        if char == ';':
            self.advance()
            return Token(TokenType.SEMICOLON, None, pos)

        if char == '_':
            self.advance()
            return Token(TokenType.WILDCARD, None, pos)
        
        self.advance()

        return Token(TokenType.UNKNOWN, char, pos)
