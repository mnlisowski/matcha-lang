from src.reader import CharReader, EOF
from src.token import Token
from src.token_type import TokenType
from src.lexer_dicts import KEYWORDS, SINGLE_CHAR_TOKENS, DOUBLE_CHAR_TOKENS


class Lexer:
    def __init__(
        self,
        reader,
        max_identifier_length=64,
        max_int_value=2147483647,
        max_string_length=1024,
        max_comment_length=1024,
        hard_max_identifier=640,
        hard_max_string=10240,
        hard_max_comment=10240,
        max_tokens=100000,
        hard_max_digits=20,
    ):
        self.reader = reader
        self.current_char = self.reader.current()

        self.max_identifier_length = max_identifier_length
        self.max_int_value = max_int_value
        self.max_string_length = max_string_length
        self.max_comment_length = max_comment_length

        self.hard_max_identifier = hard_max_identifier
        self.hard_max_string = hard_max_string
        self.hard_max_comment = hard_max_comment
        self.hard_max_digits = hard_max_digits
        self.max_tokens = max_tokens
        self.token_count = 0

        self.token_strategies = [
            self._try_read_comment,
            self._try_read_number,
            self._try_read_identifier_or_keyword,
            self._try_read_string,
            self._try_read_compound_operator,
            self._try_read_single_char_token,
        ]

    def advance(self):
        self.current_char = self.reader.advance()

    def skip_whitespace(self):
        while self.current_char != EOF and self.current_char.isspace():
            self.advance()

    def _try_read_comment(self):
        if self.current_char != "/" or self.reader.check_next() != "/":
            return None

        start_pos = self.reader.position()
        self.advance()
        self.advance()

        comment_text = []
        exceeded_soft_limit = False

        while self.current_char != EOF and self.current_char != "\n":
            # hard limit
            if len(comment_text) >= self.hard_max_comment:
                raise ValueError(
                    f"Comment is at hard limit ({self.hard_max_comment}) at {start_pos}. "
                )

            comment_text.append(self.current_char)
            self.advance()

            # soft
            if len(comment_text) > self.max_comment_length:
                exceeded_soft_limit = True

        if exceeded_soft_limit:
            return Token(
                TokenType.UNKNOWN,
                f"Comment too long (max {self.max_comment_length})",
                start_pos,
            )

        return Token(TokenType.COMMENT, "".join(comment_text), start_pos)

    def _try_read_number(self):
        if not self.current_char.isdecimal():
            return None

        start_pos = self.reader.position()

        int_value = 0
        frac_value = 0
        frac_digits = 0

        is_float = False
        total_chars = 0

        while self.current_char.isdecimal():
            if total_chars >= self.hard_max_digits:
                raise ValueError(
                    f"Number literal too long (> {self.hard_max_digits}) at {start_pos}."
                )

            digit = ord(self.current_char) - ord("0")
            int_value = int_value * 10 + digit
            total_chars += 1
            self.advance()

        if self.current_char == ".":
            is_float = True
            total_chars += 1
            self.advance()

            while self.current_char != EOF and self.current_char.isdecimal():
                if total_chars >= self.hard_max_digits:
                    raise ValueError(
                        f"Number too long (> {self.hard_max_digits}) at {start_pos}"
                    )

                digit = ord(self.current_char) - ord("0")
                frac_value = frac_value * 10 + digit
                frac_digits += 1
                total_chars += 1
                self.advance()

        if is_float:
            if frac_digits > 0:
                final_value = float(int_value) + (float(frac_value) / (10**frac_digits))
            else:
                final_value = float(int_value)

            return Token(TokenType.FLOAT_LITERAL, final_value, start_pos)

        else:
            if int_value > self.max_int_value:
                return Token(
                    TokenType.UNKNOWN,
                    f"Integer overflow (max {self.max_int_value})",
                    start_pos,
                )

            return Token(TokenType.INT_LITERAL, int_value, start_pos)

    def _try_read_identifier_or_keyword(self):
        if not (self.current_char.isalpha() or self.current_char == "_"):
            return None

        start_pos = self.reader.position()
        text = []
        exceeded_soft_limit = False

        while self.current_char != EOF and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            # hard limit
            if len(text) >= self.hard_max_identifier:
                raise ValueError(
                    f"Exceeded hard limit ({self.hard_max_identifier}) at {start_pos}. "
                )

            text.append(self.current_char)
            self.advance()

            # soft
            if len(text) > self.max_identifier_length:
                exceeded_soft_limit = True

        text_str = "".join(text)

        if exceeded_soft_limit:
            return Token(
                TokenType.UNKNOWN,
                f"Identifier too long (max {self.max_identifier_length})",
                start_pos,
            )

        # Sprawdzamy, czy to słowo kluczowe
        if token_type := KEYWORDS.get(text_str):
            return Token(token_type, None, start_pos)
        else:
            return Token(TokenType.IDENTIFIER, text_str, start_pos)

    def _try_read_string(self):
        if self.current_char != '"':
            return None

        start_pos = self.reader.position()
        self.advance()

        result = []
        exceeded_soft_limit = False
        invalid_escape_sequence = False
        invalid_char_pos = None

        escape_map = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}

        while self.current_char != EOF and self.current_char != '"':
            # hard limit
            if len(result) >= self.hard_max_string:
                raise ValueError(
                    f"String exceeded hard limit ({self.hard_max_string}) at {start_pos}. "
                )

            # soft
            if len(result) > self.max_string_length:
                exceeded_soft_limit = True

            if self.current_char == "\\":
                self.advance()

                if self.current_char in escape_map:
                    result.append(escape_map[self.current_char])
                else:
                    invalid_escape_sequence = True
                    if invalid_char_pos is None:
                        invalid_char_pos = self.reader.position()
                    result.append(self.current_char)
            else:
                result.append(self.current_char)

            self.advance()

        if self.current_char == '"':
            self.advance()

            if invalid_escape_sequence:
                return Token(
                    TokenType.UNKNOWN,
                    f"Invalid escape sequence at {invalid_char_pos}",
                    start_pos,
                )

            if exceeded_soft_limit:
                return Token(
                    TokenType.UNKNOWN,
                    f"String too long (max {self.max_string_length})",
                    start_pos,
                )

            return Token(TokenType.STRING_LITERAL, "".join(result), start_pos)
        else:
            return Token(TokenType.UNKNOWN, "Niezamknięty string", start_pos)

    def _try_read_compound_operator(self):
        """Sprawdza czy to złożony operator i go czyta, lub zwraca None"""
        if self.current_char not in DOUBLE_CHAR_TOKENS:
            return None

        pos = self.reader.position()
        first = self.current_char
        self.advance()

        options = DOUBLE_CHAR_TOKENS[first]
        token_type = options.get(self.current_char)

        if token_type:
            self.advance()
            return Token(token_type, None, pos)

        valid_operator = options[None]
        if valid_operator is None:
            return Token(TokenType.UNKNOWN, first, pos)

        return Token(valid_operator, None, pos)

    def _try_read_single_char_token(self):
        """Sprawdza czy to pojedynczy znak i go czyta, lub zwraca None"""
        if self.current_char not in SINGLE_CHAR_TOKENS:
            return None

        pos = self.reader.position()
        token_type = SINGLE_CHAR_TOKENS[self.current_char]
        self.advance()
        return Token(token_type, None, pos)

    def _try_read_compound_operator(self):
        """Sprawdza czy to złożony operator i go czyta, lub zwraca None"""
        if self.current_char not in DOUBLE_CHAR_TOKENS:
            return None

        pos = self.reader.position()
        first = self.current_char
        self.advance()

        options = DOUBLE_CHAR_TOKENS[first]
        token_type = options.get(self.current_char)

        if token_type:
            self.advance()
            return Token(token_type, None, pos)

        valid_operator = options[None]
        if valid_operator is None:
            return Token(TokenType.UNKNOWN, first, pos)

        return Token(valid_operator, None, pos)

    def get_next_token(self):
        self.token_count += 1

        if self.token_count > self.max_tokens:
            raise ValueError(f"Too many tokens (max {self.max_tokens}). ")

        self.skip_whitespace()

        if self.current_char == EOF:
            return Token(TokenType.EOF, None, self.reader.position())

        for try_read in self.token_strategies:
            token = try_read()
            if token is not None:
                return token

        pos = self.reader.position()
        char = self.current_char
        self.advance()
        return Token(TokenType.UNKNOWN, char, pos)


def tokens_generator(lexer: Lexer):
    while (token := lexer.get_next_token()).type != TokenType.EOF:
        yield token

    yield token
