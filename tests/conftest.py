import pytest
import io
import sys
from typing import Any

from src.lexer.reader import CharReader
from src.lexer.lexer import Lexer, LexerError
from src.parser.parser import Parser, ParserError
from src.interpreter.interpreter import Interpreter


def run_code(source: str, entry_point: str = "main") -> Any:
    errors = []

    reader = CharReader(io.StringIO(source))
    lexer = Lexer(reader)
    parser = Parser(lexer, errors.append)
    program = parser.parse_program()

    if errors:
        for err in errors:
            if isinstance(err, LexerError):
                print(f"Błąd leksykalny: {err}", file=sys.stderr)
            elif isinstance(err, ParserError):
                print(f"Błąd parsowania: {err}", file=sys.stderr)
            else:
                print(f"Błąd: {err}", file=sys.stderr)
        return False

    interpreter = Interpreter()
    interpreter.load(program)
    return interpreter.invoke(entry_point)


@pytest.fixture
def run():
   
    return run_code
