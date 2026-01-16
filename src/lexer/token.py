from typing import Any
from src.common.position import Position
from src.lexer.token_type import TokenType


class Token:
    def __init__(self, type: TokenType, value: Any, position: Position) -> None:
        self.type = type
        self.value = value  # to tylko dla literałów
        self.position = position

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return False

        if self.type != other.type:
            return False

        if self.value != other.value:
            return False

        if self.position != other.position:
            return False

        return True

    def __repr__(self) -> str:
        type_name = self.type.name

        if self.value is not None:
            return type_name + "(" + str(self.value) + ") at " + str(self.position)
        else:
            return type_name + " at " + str(self.position)
