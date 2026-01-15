from enum import Enum, auto


class TokenType(Enum):
    # Słowa Kluczowe
    FUN = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    VAR = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    MATCH = auto()
    AS = auto()
    CASE = auto()
    DEFAULT = auto()
    IS = auto()
    TRUE = auto()
    FALSE = auto()
    TYPE_INT = auto()
    TYPE_STR = auto()
    TYPE_FLT = auto()
    TYPE_BOOL = auto()

    # Literały
    IDENTIFIER = auto()
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()

    # Operatory
    PLUS = auto()  # +
    MINUS = auto()  # -
    MULTIPLY = auto()  # *
    DIVIDE = auto()  # /
    NOT = auto()  # !
    ASSIGN = auto()  # =
    ARROW = auto()  # =>

    EQUAL = auto()  # ==
    NOT_EQUAL = auto()  # !=
    LESS = auto()  # <
    LESS_EQ = auto()  # <=
    GREATER = auto()  # >
    GREATER_EQ = auto()  # >=

    AND = auto()  # and
    OR = auto()  # or
    AND_PATTERN = auto()  # AND (do wzorców w matchu

    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    COMMA = auto()  # ,
    SEMICOLON = auto()  # ;
    WILDCARD = auto()  # _
    COMMENT = auto()

    # inne
    EOF = auto()  # Koniec pliku
    UNKNOWN = auto()
