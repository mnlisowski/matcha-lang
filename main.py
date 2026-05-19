#!/usr/bin/env python3

import io
import sys
from typing import TextIO

from src.lexer.reader import CharReader
from src.lexer.lexer import Lexer, LexerError
from src.parser.parser import Parser, ParserError
from src.interpreter.interpreter import Interpreter, RuntimeError


USAGE = """Użycie:
  python3 main.py <plik.matcha>
  python3 main.py -c '<kod>'

Opcje:
  -c <kod>       uruchamia kod przekazany w linii poleceń
  -h, --help     wyświetla pomoc
"""


def run(stream: TextIO) -> bool:
    errors = []

    reader = CharReader(stream)
    lexer = Lexer(reader, errors.append)
    parser = Parser(lexer, errors.append)

    try:
        program = parser.parse_program()
    except ParserError as err:
        errors.append(err)
        program = None

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

    try:
        interpreter.load(program)
        interpreter.invoke("main")

    except RuntimeError as e:
        print(f"Błąd wykonania: {e}", file=sys.stderr)
        return False

    return True


def main() -> int:
    args = sys.argv[1:]

    if not args:
        print(USAGE, end="", file=sys.stderr)
        return 1

    if args[0] in ("-h", "--help"):
        print(USAGE, end="")
        return 0

    try:
        if args[0] == "-c":
            if len(args) != 2:
                print(
                    "Błąd: opcja -c wymaga dokładnie jednego argumentu z kodem",
                    file=sys.stderr,
                )
                print(USAGE, end="", file=sys.stderr)
                return 1

            return 0 if run(io.StringIO(args[1])) else 1

        if len(args) != 1:
            print("Błąd: podano za dużo argumentów", file=sys.stderr)
            print(USAGE, end="", file=sys.stderr)
            return 1

        filename = args[0]
        with open(filename, "r", encoding="utf-8") as f:
            return 0 if run(f) else 1

    except FileNotFoundError:
        print(f"Błąd: plik '{args[0]}' nie istnieje", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"Błąd wykonania: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
