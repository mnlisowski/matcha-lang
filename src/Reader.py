from src.Position import Position

EOF = '\0'


class CharReader:
    def __init(self, source):
        self.source = source
        self.length = len(source)

        self.pos = -1
        self.line = 1
        self.col = 0

        self.current_char = ""
        self.advance()

    def advance(self):
        self.pos += 1

        if self.pos >= self.length:
            self.current_char = EOF
            return EOF

        self.current_char = self.source[self.pos]

        if self.current_char == "\n":
            self.line += 1
            self.col = 0
        else:
            self.col += 1

        return self.current_char

    def current(self):
        return self.current_char

    def check_next(self):
        next_pos = self.pos + 1

        if next_pos >= self.length:
            return EOF
        return self.source[next_pos]

    def position(self):
        return Position(self.line, self.col)
