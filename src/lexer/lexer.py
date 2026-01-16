from typing import Optional, Any, Generator
from src.lexer.reader import CharReader, EOF
from src.lexer.token import Token
from src.lexer.token_type import TokenType
from src.lexer.lexer_dicts import KEYWORDS, SINGLE_CHAR_TOKENS, DOUBLE_CHAR_TOKENS
from src.common.position import Position


class LexerError(Exception):
    def __init__(self, message: str, position: Position) -> None:
        self.message = message
        self.position = position
        super().__init__(f"{message} at {position}")

    def __str__(self) -> str:
        return f"Błąd leksykalny {self.position}: {self.message}"


class HardLimitError(LexerError):
    def __init__(self, element_type: str, limit: int, position: Position) -> None:
        message = f"{element_type} exceeded hard limit ({limit})"
        super().__init__(message, position)
        self.element_type = element_type
        self.limit = limit


class InvalidCharacterError(LexerError):
    def __init__(self, char: str, position: Position) -> None:
        message = f"Unexpected character '{char}'"
        super().__init__(message, position)
        self.char = char


class UnterminatedStringError(LexerError):
    def __init__(self, position: Position) -> None:
        message = "Unterminated string literal"
        super().__init__(message, position)


class InvalidEscapeSequenceError(LexerError):
    def __init__(self, escape_char: str, position: Position) -> None:
        message = f"Invalid escape sequence '\\{escape_char}'"
        super().__init__(message, position)
        self.escape_char = escape_char


class IntegerOverflowError(LexerError):
    def __init__(self, value: int, max_value: int, position: Position) -> None:
        message = f"Integer overflow: {value} exceeds ({max_value})"
        super().__init__(message, position)
        self.value = value
        self.max_value = max_value


class SoftLimitError(LexerError):
    def __init__(self, element_type: str, limit: int, position: Position) -> None:
        self.element_type = element_type
        self.limit = limit
        self.position = position

    def __str__(self) -> str:
        return f"Warning {self.position}: {self.element_type} exceeded soft limit ({self.limit})"


class Lexer:
    def __init__(
        self,
        reader: CharReader,
        error_handler=None,
        max_identifier_length: int = 64,
        max_int_value: int = 2147483647,
        max_string_length: int = 1024,
        max_comment_length: int = 1024,
        hard_max_identifier: int = 640,
        hard_max_string: int = 10240,
        hard_max_comment: int = 10240,
        max_tokens: int = 100000,
        hard_max_digits: int = 20,
    ) -> None:
        self.reader = reader
        self.current_char = self.reader.current()
        self.error_handler = error_handler

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
            self._try_read_EOF,
            self._try_read_comment,
            self._try_read_number,
            self._try_read_identifier_or_keyword,
            self._try_read_string,
            self._try_read_compound_operator,
            self._try_read_single_char_token,
        ]

    def advance(self) -> None:
        self.current_char = self.reader.advance()

    def skip_whitespace(self) -> None:
        while self.current_char.isspace():
            self.advance()

    def _report_warning(self, error: Any) -> None:
        if self.error_handler:
            self.error_handler(error)

    def _try_read_comment(self) -> Optional[Token]:
        if self.current_char != "/" or self.reader.check_next() != "/":
            return None

        start_pos = self.reader.position()
        self.advance()
        self.advance()

        comment_text = []
        exceeded_soft_limit = False

        while self.current_char != EOF and self.current_char != "\n":
            # Hard limit
            if len(comment_text) >= self.hard_max_comment:
                raise HardLimitError("Comment", self.hard_max_comment, start_pos)

            comment_text.append(self.current_char)
            self.advance()

            # Soft limit
            if len(comment_text) > self.max_comment_length:
                exceeded_soft_limit = True

        if exceeded_soft_limit:
            self._report_warning(
                SoftLimitError("Comment", self.max_comment_length, start_pos)
            )

        return Token(TokenType.COMMENT, "".join(comment_text), start_pos)

    def _try_read_number(self) -> Optional[Token]:
        if not self.current_char.isdecimal():
            return None

        start_pos = self.reader.position()

        int_value = 0
        frac_value = 0
        frac_digits = 0
        total_chars = 0

        while self.current_char.isdecimal():
            if total_chars >= self.hard_max_digits:
                raise HardLimitError("Number literal", self.hard_max_digits, start_pos)

            digit = ord(self.current_char) - ord("0")
            int_value = int_value * 10 + digit
            total_chars += 1
            self.advance()

        if self.current_char == ".":
            total_chars += 1
            self.advance()

            while self.current_char.isdecimal():
                if total_chars >= self.hard_max_digits:
                    raise HardLimitError(
                        "Number literal", self.hard_max_digits, start_pos
                    )

                digit = ord(self.current_char) - ord("0")
                frac_value = frac_value * 10 + digit
                frac_digits += 1
                total_chars += 1
                self.advance()

            if frac_digits > 0:
                final_value = float(int_value) + (float(frac_value) / (10**frac_digits))
            else:
                final_value = float(int_value)

            return Token(TokenType.FLOAT_LITERAL, final_value, start_pos)

        else:
            if int_value > self.max_int_value:
                self._report_warning(
                    IntegerOverflowError(int_value, self.max_int_value, start_pos)
                )

            return Token(TokenType.INT_LITERAL, int_value, start_pos)

    def _try_read_identifier_or_keyword(self) -> Optional[Token]:
        if not (self.current_char.isalpha() or self.current_char == "_"):
            return None

        start_pos = self.reader.position()
        text = []
        exceeded_soft_limit = False

        while self.current_char.isalnum() or self.current_char == "_":
            # Hard limit
            if len(text) >= self.hard_max_identifier:
                raise HardLimitError("Identifier", self.hard_max_identifier, start_pos)

            text.append(self.current_char)
            self.advance()

            # Soft limit
            if len(text) > self.max_identifier_length:
                exceeded_soft_limit = True

        text_str = "".join(text)

        if exceeded_soft_limit:
            self._report_warning(
                SoftLimitError("Identifier", self.max_identifier_length, start_pos)
            )

        if token_type := KEYWORDS.get(text_str):
            return Token(token_type, None, start_pos)
        else:
            return Token(TokenType.IDENTIFIER, text_str, start_pos)

    def _try_read_string(self) -> Optional[Token]:
        if self.current_char != '"':
            return None

        start_pos = self.reader.position()
        self.advance()

        result = []
        exceeded_soft_limit = False
        invalid_escape_char = None
        invalid_escape_pos = None

        escape_map = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}

        while self.current_char != EOF and self.current_char != '"':
            # Hard limit
            if len(result) >= self.hard_max_string:
                raise HardLimitError("String literal", self.hard_max_string, start_pos)

            # Soft limit
            if len(result) > self.max_string_length:
                exceeded_soft_limit = True

            if self.current_char == "\\":
                self.advance()

                if self.current_char in escape_map:
                    result.append(escape_map[self.current_char])
                else:
                    if invalid_escape_char is None:
                        invalid_escape_char = self.current_char
                        invalid_escape_pos = self.reader.position()
                    result.append(self.current_char)
            else:
                result.append(self.current_char)

            self.advance()

        if self.current_char == '"':
            self.advance()

            if invalid_escape_char is not None:
                self._report_warning(
                    InvalidEscapeSequenceError(invalid_escape_char, invalid_escape_pos)
                )

            if exceeded_soft_limit:
                self._report_warning(
                    SoftLimitError(
                        "String literal", self.max_string_length, start_pos
                    )
                )

            return Token(TokenType.STRING_LITERAL, "".join(result), start_pos)
        else:
            self._report_warning(UnterminatedStringError(start_pos))
            return Token(TokenType.STRING_LITERAL, "".join(result), start_pos)

    def _try_read_compound_operator(self) -> Optional[Token]:
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

        valid_operator = options.get(None)
        if valid_operator is None:
            raise InvalidCharacterError(first, pos)

        return Token(valid_operator, None, pos)

    def _try_read_single_char_token(self) -> Optional[Token]:
        """Sprawdza czy to pojedynczy znak i go czyta, lub zwraca None"""
        if token_type := SINGLE_CHAR_TOKENS.get(self.current_char):
            pos = self.reader.position()
            self.advance()
            return Token(token_type, None, pos)
        return None

    def _try_read_EOF(self) -> Optional[Token]:
        if self.current_char == EOF:
            return Token(TokenType.EOF, None, self.reader.position())

    def get_next_token(self) -> Token:
        self.skip_whitespace()

        for try_read in self.token_strategies:
            token = try_read()
            if token is not None:
                return token

        pos = self.reader.position()
        char = self.current_char
        self.advance()
        raise InvalidCharacterError(char, pos)


def tokens_generator(lexer: Lexer) -> Generator[Token, None, None]:
    while (token := lexer.get_next_token()).type != TokenType.EOF:
        yield token

    yield token
