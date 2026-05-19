# Matcha

Matcha to interpreter języka programowania napisany w Pythonie.
Projekt zawiera czytnik znaków, lekser, parser budujący AST oraz interpreter.
Program jest uruchamiany od funkcji `main`.

## Wymagania

- Python 3.10+
- `pytest` do uruchamiania testów

## Funkcje języka

- typy: `int`, `float`, `string`, `bool`
- silne, dynamiczne typowanie bez automatycznej promocji `int`/`float`
- zmienne tworzone przez przypisanie, np. `x = 10;`
- zakresy blokowe dla funkcji, pętli, warunków i `match`
- operatory arytmetyczne: `+`, `-`, `*`, `/`
- operatory porównania: `==`, `!=`, `<`, `<=`, `>`, `>=`
- operatory logiczne: `and`, `or`, `!`
- instrukcje `if`, `else`, `while`
- `return`, `break`, `continue`
- funkcje definiowane przez `fun`
- rekurencja
- komentarze jednoliniowe `//`
- funkcje wbudowane: `print`, `println`, `input`, `typeof`
- instrukcja `match` z aliasami, warunkami logicznymi i wzorcami pozycyjnymi
- wzorce w `match`: `_`, stałe, relacje, `is typ`, złożenia `AND`
- `match` wykonuje wszystkie pasujące gałęzie; `default` działa tylko przy braku dopasowania

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
dokumentacja_koncowa.md     dokumentacja końcowa
```

## Dokumentacja

- [Dokumentacja końcowa](dokumentacja_koncowa.md)
- [Projekt wstępny](docs/projekt_wstepny.md)
