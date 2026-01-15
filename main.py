#!/usr/bin/env python3


import sys
import io

from src.lexer.reader import CharReader
from src.lexer.lexer import Lexer
from src.parser.parser import Parser, ParserError
from src.interpreter.interpreter import Interpreter, RuntimeError
# from src.ast_nodes import FunctionCall, SourceLocation


def run(stream):
    errors = []

    def error_handler(error):
        errors.append(error)

    reader = CharReader(stream)
    lexer = Lexer(reader)
    parser = Parser(lexer, error_handler)
    program = parser.parse_program()

    if errors:
        for err in errors:
            print(f"Błąd parsowania: {err}", file=sys.stderr)
        return False

    interpreter = Interpreter()

    try:
        interpreter.load(program)
        interpreter.invoke("main")

    except RuntimeError as e:
        print(f"Błąd wykonania: {e}", file=sys.stderr)
        return False

    return True


def main():
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
