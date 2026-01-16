#!/usr/bin/env python3

import sys
import io
from typing import TextIO

from src.lexer.reader import CharReader
from src.lexer.lexer import Lexer, LexerError
from src.parser.parser import Parser, ParserError
from src.interpreter.interpreter import Interpreter, RuntimeError
# from src.ast_nodes import FunctionCall, SourceLocation


def run(stream: TextIO) -> bool:
    errors = []

    reader = CharReader(stream)
    lexer = Lexer(reader, errors.append)
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


    interpreter = Interpreter()

    try:
        interpreter.load(program)
        interpreter.invoke("main")

    except RuntimeError as e:
        print(f"Błąd wykonania: {e}", file=sys.stderr)
        return False

    return True


def main() -> None:
    if len(sys.argv) < 2:
        print("Użycie:")
        sys.exit(1)

    try:
        if sys.argv[1] == "-c":
            if len(sys.argv) < 3:
                print("brak kodu po -c")
                sys.exit(1)

            source_stream = io.StringIO(sys.argv[2])
            run(source_stream)
        else:
            filename = sys.argv[1]
            with open(filename, "r", encoding="utf-8") as f:
                run(f)

    except FileNotFoundError:
        print(f"Błąd: Plik '{sys.argv[1]}' nie istnieje", file=sys.stderr)
        sys.exit(1)
    except ParserError as e:
        print(f"Błąd składni: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Błąd wykonania: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
