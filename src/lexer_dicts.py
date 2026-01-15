from .token_type import TokenType

KEYWORDS = {
    "fun": TokenType.FUN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "return": TokenType.RETURN,
    "var": TokenType.VAR,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "match": TokenType.MATCH,
    "as": TokenType.AS,
    "case": TokenType.CASE,
    "default": TokenType.DEFAULT,
    "is": TokenType.IS,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "int": TokenType.TYPE_INT,
    "string": TokenType.TYPE_STR,
    "float": TokenType.TYPE_FLT,
    "bool": TokenType.TYPE_BOOL,
    "AND": TokenType.AND_PATTERN,
    "_": TokenType.WILDCARD,
    "and": TokenType.AND,
    "or": TokenType.OR,
}


SINGLE_CHAR_TOKENS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MULTIPLY,
    "/": TokenType.DIVIDE,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    ",": TokenType.COMMA,
    ";": TokenType.SEMICOLON,
}

DOUBLE_CHAR_TOKENS = {
    "=": {"=": TokenType.EQUAL, ">": TokenType.ARROW, None: TokenType.ASSIGN},
    "!": {"=": TokenType.NOT_EQUAL, None: TokenType.NOT},
    "<": {"=": TokenType.LESS_EQ, None: TokenType.LESS},
    ">": {"=": TokenType.GREATER_EQ, None: TokenType.GREATER},
}
