class Position:
    def __init__(self, line, column):
        self.line = line
        self.column = column

    def copy(self):
        p = Position(self.line, self.column)
        return p

    def __str__(self):
        return "[" + str(self.line) + ":" + str(self.column) + "]"

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False

        if self.line == other.line and self.column == other.column:
            return True
        else:
            return False
