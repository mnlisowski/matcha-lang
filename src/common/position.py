class Position:
    def __init__(self, line, column):
        self.line = line
        self.column = column

    def __str__(self):
        return f"[{self.line}:{self.column}]"

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False

        return self.line == other.line and self.column == other.column
