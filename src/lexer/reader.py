from typing import TextIO
from src.common.position import Position

EOF = "\4"


class CharReader:
    def __init__(self, stream: TextIO) -> None:
        self.stream = stream
        self.line = 1
        self.col = 0

        self._next_char = self.stream.read(1)
        if not self._next_char:
            self._next_char = EOF

        self.current_char = ""

        self.advance()

    def _next_line(self) -> None:
        self.line += 1
        self.col = 1

    def _next_column(self) -> None:
        self.col += 1

    def current(self) -> str:
        return self.current_char

    def check_next(self) -> str:
        return self._next_char

    def position(self) -> Position:
        return Position(self.line, self.col)

    def advance(self) -> str:
        if self.current_char == EOF:
            return EOF
        if self.current_char == "\n":
            self._next_line()
        else:
            self._next_column()

        self.current_char = self._next_char

        if self.current_char != EOF:
            new_char = self.stream.read(1)
            self._next_char = new_char if new_char else EOF
        else:
            return EOF

        return self.current_char
