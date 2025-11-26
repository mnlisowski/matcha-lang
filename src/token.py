from src.token_type import TokenType
from src.position import Position


class Token:
    def __init__(self, type, value, position):
        self.type = type
        self.value = value  #  to tylko dla literałów
        self.position = position

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False

        if self.type != other.type:
            return False

        if self.value != other.value:
            return False

        if self.position != other.position:
            return False

        return True

    def __repr__(self):

        type_name = self.type.name

        if self.value is not None:
            return type_name + "(" + str(self.value) + ") at " + str(self.position)
        else:
            return type_name + " at " + str(self.position)
