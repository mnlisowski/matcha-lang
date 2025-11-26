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

    def get_next_token(self):
        self.skip_whitespace()

        if self.current_char == EOF:
            return Token(TokenType.EOF, None, self.reader.position())

        # narazie zwracamy token UNKNOWN
        pos = self.reader.position()
        char = self.current_char
        self.advance() 
        return Token(TokenType.UNKNOWN, char, pos)