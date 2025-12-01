from src.reader import CharReader, EOF
from src.token import Token
from src.token_type import TokenType
from src.lexer_dicts import KEYWORDS, SINGLE_CHAR_TOKENS, DOUBLE_CHAR_TOKENS



class Lexer:
    SINGLE_CHAR_TOKENS = {
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '*': TokenType.MULTIPLY,
        '/': TokenType.DIVIDE,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        '{': TokenType.LBRACE,
        '}': TokenType.RBRACE,
        '[': TokenType.LBRACKET,
        ']': TokenType.RBRACKET,
        ',': TokenType.COMMA,
        ';': TokenType.SEMICOLON,
    }

    DOUBLE_CHAR_TOKENS = {
        '=': {
            '=': TokenType.EQUAL,
            '>': TokenType.ARROW,
            None: TokenType.ASSIGN
        },
        '!': {
            '=': TokenType.NOT_EQUAL,
            None: TokenType.NOT
        },
        '<': {
            '=': TokenType.LESS_EQ,
            None: TokenType.LESS
        },
        '>': {
            '=': TokenType.GREATER_EQ,
            None: TokenType.GREATER
        },
        '&': {
            '&': TokenType.AND,
            None: None  
        },
        '|': {
            '|': TokenType.OR,
            None: None  
        }
    }

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

    def _try_read_comment(self):
        if self.current_char != '/' or self.reader.check_next() != '/':
            return None
        
        start_pos = self.reader.position()
        self.advance() 
        self.advance()  
        
        comment_text = []
        exceeded_soft_limit = False
        
        while self.current_char != EOF and self.current_char != '\n':
            if len(comment_text) > self.hard_max_comment:
                raise ValueError(
                    f"Comment exceeded hard limit  at {start_pos}. "
                )
            
            comment_text.append(self.current_char)
            self.advance()
            
            if len(comment_text) > self.max_comment_length:
                exceeded_soft_limit = True
        
        if exceeded_soft_limit:
            return Token(TokenType.UNKNOWN, 
                       f"Comment too long)", start_pos)
        
        return Token(TokenType.COMMENT, ''.join(comment_text), start_pos)

        


    def _try_read_single_char_token(self):
        if self.current_char not in self.SINGLE_CHAR_TOKENS:
            return None
        
        pos = self.reader.position()
        token_type = self.SINGLE_CHAR_TOKENS[self.current_char]
        self.advance()
        return Token(token_type, None, pos)
    
    def _try_read_compound_operator(self):
        if self.current_char not in self.COMPOUND_OPERATORS:
            return None
        
        pos = self.reader.position()
        first = self.current_char
        self.advance()
        
        options = self.DOUBLE_CHAR_TOKENS[first]
        token_type = options.get(self.current_char)
        
        if token_type:
            self.advance()
            return Token(token_type, None, pos)
        
        # Fallback na pojedynczy znak
        fallback = options[None]
        if fallback is None:
            # Pojedyncze & lub | to błąd
            return Token(TokenType.UNKNOWN, first, pos)
        
        return Token(fallback, None, pos)
    

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
        
   


        # # Operatory matematyczne
        # if char == "+":
        #     self.advance()
        #     return Token(TokenType.PLUS, None, pos)

        # if char == "-":
        #     self.advance()
        #     return Token(TokenType.MINUS, None, pos)

        # if char == "*":
        #     self.advance()
        #     return Token(TokenType.MULTIPLY, None, pos)

        # if char == "/":
        #     self.advance()
        #     return Token(TokenType.DIVIDE, None, pos)

        # # Nawiasy
        # if char == "(":
        #     self.advance()
        #     return Token(TokenType.LPAREN, None, pos)

        # if char == ")":
        #     self.advance()
        #     return Token(TokenType.RPAREN, None, pos)

        # if char == "{":
        #     self.advance()
        #     return Token(TokenType.LBRACE, None, pos)

        # if char == "}":
        #     self.advance()
        #     return Token(TokenType.RBRACE, None, pos)

        # if char == "[":
        #     self.advance()
        #     return Token(TokenType.LBRACKET, None, pos)

        # if char == "]":
        #     self.advance()
        #     return Token(TokenType.RBRACKET, None, pos)

        # # Interpunkcja
        # if char == ",":
        #     self.advance()
        #     return Token(TokenType.COMMA, None, pos)

        # if char == ";":
        #     self.advance()
        #     return Token(TokenType.SEMICOLON, None, pos)

        # if char == "_":
        #     self.advance()
        #     return Token(TokenType.WILDCARD, None, pos)

        # # Operatory złożone, wymagajace uzycia check_next()

        # if char == "=":
        #     if self.reader.check_next() == "=":
        #         self.advance()
        #         self.advance()
        #         return Token(TokenType.EQUAL, None, pos)
        #     elif self.reader.check_next() == ">":
        #         self.advance()
        #         self.advance()
        #         return Token(TokenType.ARROW, None, pos)
        #     else:
        #         self.advance()
        #         return Token(TokenType.ASSIGN, None, pos)

        # if char == "!":
        #     if self.reader.check_next() == "=":
        #         self.advance()
        #         self.advance()
        #         return Token(TokenType.NOT_EQUAL, None, pos)
        #     else:
        #         self.advance()
        #         return Token(TokenType.NOT, None, pos)

        # if char == "<":
        #     if self.reader.check_next() == "=":
        #         self.advance()
        #         self.advance()
        #         return Token(TokenType.LESS_EQ, None, pos)
        #     else:
        #         self.advance()
        #         return Token(TokenType.LESS, None, pos)

        # if char == ">":
        #     if self.reader.check_next() == "=":
        #         self.advance()
        #         self.advance()
        #         return Token(TokenType.GREATER_EQ, None, pos)
        #     else:
        #         self.advance()
        #         return Token(TokenType.GREATER, None, pos)

        # if char == "&":
        #     if self.reader.check_next() == "&":
        #         self.advance()
        #         self.advance()
        #         return Token(TokenType.AND, None, pos)
        #     # Pojedyncze & bedzie unknown

        # if char == "|":
        #     if self.reader.check_next() == "|":
        #         self.advance()
        #         self.advance()
        #         return Token(TokenType.OR, None, pos)
        #     # Pojedyncze '|' bedzie unknown

        self.advance()

        return Token(TokenType.UNKNOWN, char, pos)
