from src.reader import CharReader
from src.lexer import Lexer
from src.token_type import TokenType

def main():
    
    source_code = """
    // To jest komentarz
    fun main() {
        var x = 123;
        var y = 45.67; ^
        var text = "Hello\\nWorld";
        
        if (x >= 100) {
            print(text);
        }

        match x as v1 {
            case [> 10, is int] => {
                return v1 + 1;
            }
        }
    }
    """

    
    # tabela
    print(f"{'TYP TOKENU':<20} {'WARTOŚĆ':<20} {'POZYCJA'}")
    print("-" * 60)

    reader = CharReader(source_code)
    lexer = Lexer(reader)
    
    while True:
        token = lexer.get_next_token()
        

        print(f"{token.type.name:<20} {str(token.value):<20} {token.position}")
        
        if token.type == TokenType.EOF:
            print("\n koniec pliku")
            break
            
        if token.type == TokenType.UNKNOWN:
            print(f"\nNapotkano nieznany token.")
            break

if __name__ == "__main__":
    main()