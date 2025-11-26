from src.reader import CharReader, EOF
from src.token import Token
from src.token_type import TokenType

KEYWORDS = {
    "fun": TokenType.FUN,
    "return": TokenType.RETURN,
    "var": TokenType.VAR,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "match": TokenType.MATCH,
    "as": TokenType.AS,
    "case": TokenType.CASE,
    "default": TokenType.DEFAULT,
    "is": TokenType.IS,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "int": TokenType.TYPE_INT,
    "string": TokenType.TYPE_STR,
    "float": TokenType.TYPE_FLT,
    "bool": TokenType.TYPE_BOOL,
    "AND": TokenType.AND_PATTERN,
    "_": TokenType.WILDCARD,
}


class Lexer:
    def __init__(self, reader):
        self.reader = reader
        self.current_char = self.reader.current()

    def _read_number(self):
        start_pos = self.reader.position()
        value = 0

        # czesc calkowita liczby
        while self.current_char != EOF and self.current_char.isdigit():
            digit = ord(self.current_char) - ord("0")
            value = value * 10 + digit
            self.advance()

        # jesli jest kropka, to mamy floata
        if self.current_char == ".":
            self.advance()  # kropka zjadana

            value = float(value)
            divisor = 10.0

            # czesc ulamkowa
            while self.current_char != EOF and self.current_char.isdigit():
                digit = ord(self.current_char) - ord("0")
                value += digit / divisor
                divisor *= 10.0
                self.advance()

            return Token(TokenType.FLOAT_LITERAL, value, start_pos)

        # Jeśli nie było kropki, zwracamy Int
        return Token(TokenType.INT_LITERAL, value, start_pos)

    def _read_identifier_or_keyword(self):
        start_pos = self.reader.position()
        text = ""

        while self.current_char != EOF and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            text += self.current_char
            self.advance()

        # Sprawdzamy, czy to słowo kluczowe
        token_type = KEYWORDS.get(text)

        if token_type is not None:  # to wtedy jest keyword
            return Token(token_type, None, start_pos)
        else:
            # to wtedy identyfikator
            return Token(TokenType.IDENTIFIER, text, start_pos)

    def _read_string(self):
        start_pos = self.reader.position()

        self.advance()

        result = ""

        while self.current_char != EOF and self.current_char != '"':
            if self.current_char == "\\":
                self.advance()

                if self.current_char == "n":
                    result += "\n"
                elif self.current_char == "t":
                    result += "\t"
                elif self.current_char == "r":
                    result += "\r"
                elif self.current_char == '"':
                    result += '"'
                elif self.current_char == "\\":
                    result += "\\"
                else:  # reszte traktujemy dosłowmie
                    result += self.current_char
            else:
                # Zwykły znak
                result += self.current_char

            self.advance()

        if self.current_char == '"':
            self.advance()
            return Token(TokenType.STRING_LITERAL, result, start_pos)
        else:
            return Token(TokenType.UNKNOWN, "Niezamknięty string", start_pos)

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

        # Liczby
        if char.isdigit():
            return self._read_number()

        # identyfikatory i słowa kluczowe
        if char.isalpha() or char == "_":
            return self._read_identifier_or_keyword()

        # Stringi
        if char == '"':
            return self._read_string()

        # Operatory matematyczne
        if char == "+":
            self.advance()
            return Token(TokenType.PLUS, None, pos)

        if char == "-":
            self.advance()
            return Token(TokenType.MINUS, None, pos)

        if char == "*":
            self.advance()
            return Token(TokenType.MULTIPLY, None, pos)

        if char == "/":
            self.advance()
            return Token(TokenType.DIVIDE, None, pos)

        # Nawiasy
        if char == "(":
            self.advance()
            return Token(TokenType.LPAREN, None, pos)

        if char == ")":
            self.advance()
            return Token(TokenType.RPAREN, None, pos)

        if char == "{":
            self.advance()
            return Token(TokenType.LBRACE, None, pos)

        if char == "}":
            self.advance()
            return Token(TokenType.RBRACE, None, pos)

        if char == "[":
            self.advance()
            return Token(TokenType.LBRACKET, None, pos)

        if char == "]":
            self.advance()
            return Token(TokenType.RBRACKET, None, pos)

        # Interpunkcja
        if char == ",":
            self.advance()
            return Token(TokenType.COMMA, None, pos)

        if char == ";":
            self.advance()
            return Token(TokenType.SEMICOLON, None, pos)

        if char == "_":
            self.advance()
            return Token(TokenType.WILDCARD, None, pos)

        # Operatory złożone, wymagajace uzycia check_next()

        if char == "=":
            if self.reader.check_next() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.EQUAL, None, pos)
            elif self.reader.check_next() == ">":
                self.advance()
                self.advance()
                return Token(TokenType.ARROW, None, pos)
            else:
                self.advance()
                return Token(TokenType.ASSIGN, None, pos)

        if char == "!":
            if self.reader.check_next() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.NOT_EQUAL, None, pos)
            else:
                self.advance()
                return Token(TokenType.NOT, None, pos)

        if char == "<":
            if self.reader.check_next() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.LESS_EQ, None, pos)
            else:
                self.advance()
                return Token(TokenType.LESS, None, pos)

        if char == ">":
            if self.reader.check_next() == "=":
                self.advance()
                self.advance()
                return Token(TokenType.GREATER_EQ, None, pos)
            else:
                self.advance()
                return Token(TokenType.GREATER, None, pos)

        if char == "&":
            if self.reader.check_next() == "&":
                self.advance()
                self.advance()
                return Token(TokenType.AND, None, pos)
            # Pojedyncze & bedzie unknown

        if char == "|":
            if self.reader.check_next() == "|":
                self.advance()
                self.advance()
                return Token(TokenType.OR, None, pos)
            # Pojedyncze '|' bedzie unknown

        self.advance()

        return Token(TokenType.UNKNOWN, char, pos)
