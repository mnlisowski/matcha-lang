import io

from src.reader import CharReader
from src.lexer import Lexer, tokens_generator
from src.token_type import TokenType


def analyze_source(input_stream):
    print(f"{'TYP TOKENU':<25} {'WARTOŚĆ':<25} {'POZYCJA'}")
    print("-" * 70)

    reader = CharReader(input_stream)
    lexer = Lexer(reader)
    for token in tokens_generator(lexer):
        val_str = str(token.value)
        print(f"{token.type.name:<25} {val_str:<25} {token.position}")

        if token.type == TokenType.UNKNOWN:
            print(f"Nieznany token: '{token.value}'")

            break

# argumenty wywolania
def main():
    # Czytanie z tekstu
    source_code_text = """
    fun main() {
        var text = "jakis tekst"";
        print(text);
    }
    """
    analyze_source(io.StringIO(source_code_text))

    # Czytanie z pliku
    filename = "test_file.txt"

    try:
        with open(filename, "r", encoding="utf-8") as f:
            analyze_source(f)

    except FileNotFoundError:
        print(f"File not found {filename}")


if __name__ == "__main__":
    main()
