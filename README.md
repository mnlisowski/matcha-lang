# Matcha

Matcha to interpreter  języka programowania napisany w Pythonie.
Projekt zawiera czytnik znaków, lekser, parser budujący AST oraz interpreter.

## Funkcje języka

- typy: `int`, `float`, `string`, `bool`
- zmienne tworzone przez przypisanie, np. `x = 10;`
- instrukcje `if`, `else`, `while`
- funkcje definiowane przez `fun`
- `return`, `break`, `continue`
- komentarze jednoliniowe `//`
- funkcje wbudowane: `print`, `println`, `input`, `typeof`
- instrukcja `match` z warunkami i wzorcami pozycyjnymi

## Uruchamianie

Z pliku:

```bash
python3 main.py program.matcha
```

Z kodu przekazanego bezpośrednio:

```bash
python3 main.py -c 'fun main() { println("Hello, Matcha"); }'
```

Pomoc:

```bash
python3 main.py --help
```

## Przykład

```matcha
fun factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

fun main() {
    result = factorial(5);

    match result as value {
        [> 100] => { println("duza wartosc: ", value); },
        [== 120] => { println("dokladnie 120"); },
        default => { println("inna wartosc"); }
    }
}
```

`match` wykonuje wszystkie pasujące gałęzie. W powyższym przykładzie pasują
zarówno `[> 100]`, jak i `[== 120]`.

Większy przykładowy program znajduje się w `examples/demo.matcha`:

```bash
python3 main.py examples/demo.matcha
```

## Testy

```bash
pytest tests/ -v
```

## Struktura projektu

```text
main.py                     interfejs uruchomieniowy
src/lexer/                  lekser, tokeny i czytnik znaków
src/parser/                 parser
src/ast/                    węzły AST i visitor
src/interpreter/            interpreter i środowisko wykonania
tests/                      testy
docs/projekt_wstepny.md     dokumentacja wstępna
DOKUMENTACJA_KONCOWA.md     dokumentacja końcowa
```

## Dokumentacja

- [Dokumentacja końcowa](DOKUMENTACJA_KONCOWA.md)
- [Projekt wstępny](docs/projekt_wstepny.md)
