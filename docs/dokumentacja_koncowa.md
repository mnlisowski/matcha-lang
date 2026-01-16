# Dokumentacja projektu: Język "Matcha" 

## 1. Wstęp

Matcha jest językiem programowania ogólnego przeznaczenia. Został zaprojektowany jako język **silnie i dynamicznie typowany**, z **mutowalnymi zmiennymi**, bez automatycznej promocji typów.

Cechy języka:
- Podstawowe typy danych: `int`, `float`, `str`, `bool`
- Standardowe operacje matematyczne i logiczne
- Komentarze jednoliniowe (`//`)
- Instrukcje warunkowe (`if`)
- Pętle (`while`)
- Definiowanie i wywoływanie funkcji (`fun`) z obsługą rekursji
- instrukcja match z pattern matchingiem

###  Instrukcja `match`

 instrukcja `match`:

1. **Nagłówek Obliczeniowy**: Oblicza wyrażenia i binduje ich wyniki do tymczasowych aliasów:
```bash
`match 1 + 2 as zmienna_1, silnia(2) as zmienna_2
{
}
```
2. **Dwa tryby case**:
   - **Wzorce Pozycyjne** (`[>10, is int] =>`) - unikalna składnia, wykrywająca w kolejności zbindowane w nagłówku argumenty, ten tryb jest aktywowany po wykryciu po symbolu case nawiasu kwadratowego
   - **Wyrażenia Warunkowe** (`zmienna1 > 10 and zmienna 2 is int => `) - standardowa składnia

Instrukcja `match` nie zwraca wartości (jest instrukcją) i działa w logice **"Wykonaj Wszystkie Pasujące gałęzie"**.

---

## 2. Zasady Działania Języka

### 2.1 Typy Danych
- `bool` - wartość logiczna
- `str` - łańcuch znaków
- `int` - liczba całkowita
- `float` - liczba zmiennoprzecinkowa

### 2.2 Typowanie

**Dynamiczne**: Typy są sprawdzane w czasie wykonania (runtime). Zmienne nie mają stałego typu; typ jest powiązany z wartością.

**Silne**: Operacje między niekompatybilnymi typami są zabronione.
Nie ma automatycznej konwersji między int a float.

### 2.3 Zmienne

- **Deklaracja**: Zmienne są tworzone przy pierwszym przypisaniu.
  ```sc
  x = 10;
  ```
- **Mutowalność**: Zmienne są mutowalne, można nadpisywać ich wartość oraz typ.
- **Zasięg**:  Zmienne zadeklarowane w bloku `{...}` (np. w `if`, `while`, `fun` lub `match`) nie są widoczne na zewnątrz. Wewnętrzne bloki mają dostęp do zmiennych zewnętrznych.

### 2.4 Operatory (od najwyższego priorytetu)

| Operator |
|----------|
| `!` (logiczne NOT) |
| `-` (unarny) | 
| `*`, `/` | 
| `+`, `-` (binarny) | 
| `>`, `>=`, `<`, `<=` | 
| `==`, `!=` | 3 | 
| `and` (logiczne AND) | 
| `or` (logiczne OR) | 
### 2.5 Komentarze
Komentarze zaczynają się od `//` i trwają do końca linii.

**Dzielenie ``/`` zawsze zwraca float**, nawet dla int / int.

### 2.6 Instrukcje Warunkowe
`if (wyrażenie) { ... } else { ... }`

### 2.7 Instrukcja Pętli
 `while (wyrażenie) { ... }`

### 2.8 Funkcje

Definiowanie funkcji:
```matcha
fun nazwa(param1, param2) {
    // ciało funkcji
    return wartość;
}
```

Cechy funkcji:
- Argumenty przekazywane przez wartość
- Wspierana rekurencja (limit głębokości: 1000)
- Funkcja bez `return` zwraca `None`
- Program rozpoczyna się od wywołania funkcji `main()`

### 2.9 Funkcje Wbudowane

| Funkcja | Opis | Przykład |
|---------|------|----------|
| `print(...)` | Wypisuje bez nowej linii | `print("Hello")` |
| `println(...)` | Wypisuje z nową linią | `println("Hello")` |
| `input()` | Pobiera string ze stdin | `x = input()` |
| `typeof(x)` | Zwraca typ jako string | `typeof(42)`  `"int"` |

### 2.10 Zasady typowania 

| Operacja | Dozwolone typy | Wynik |
|----------|----------------|-------|
| `+`, `-`, `*` | `int` z `int` | `int` |
| `+`, `-`, `*` | `float` z `float` | `float` |
| `/` | `int` z `int` lub `float` z `float` | `float` |
| `+` (konkatenacja) | `string` z `string` | `string` |
| `and`, `or`, `!` | tylko `bool` | `bool` |
| `==`, `!=` | te same typy | `bool` |
| `<`, `>`, `<=`, `>=` | `int` z `int` lub `float` z `float` | `bool` |

---
**Niedozwolone**:
- Mieszanie `int` i `float` w operacjach arytmetycznych
- Operacje arytmetyczne na `string` poza konkatenacją
- Operacje logiczne na typach innych niż `bool`

## 3. Instrukcja Match - Szczegóły

### 3.1 Składnia 

```matcha
match wyrażenie as alias {
    warunek1 => { kod1 },
    warunek2 => { kod2 },
    default => { kod_domyślny }
}
```

### 3.2 Wiele Subjects

```matcha
match expr1 as a, expr2 as b, expr3 as c {
    [wzorzec1, wzorzec2, wzorzec3] => { ... }
}
```

### 3.3 Tryb Wyrażeń Warunkowych

Używa wyrażeń logicznych z aliasami:

```matcha
match 10 as x, 20 as y {
    x > 5 and y < 100 => { println("Warunek spełniony"); },
    x == 10 or y == 20 => { println("Równość"); }
}
```

### 3.4 Tryb Wzorców Pozycyjnych

Specjalna składnia `[...]` dla pattern matchingu:

| Wzorzec | Opis | Przykład |
|---------|------|----------|
| `wartość` | Równość | `[5]` |
| `== wartość` | Równość | `[== 5]` |
| `!= wartość` | Nierówność | `[!= 0]` |
| `> wartość` | Większe | `[> 10]` |
| `< wartość` | Mniejsze | `[< 100]` |
| `>= wartość` | Większe lub równe | `[>= 0]` |
| `<= wartość` | Mniejsze lub równe | `[<= 50]` |
| `is typ` | Sprawdzenie typu | `[is int]` |
| `_` | Wildcard (zawsze pasuje) | `[_, > 5]` |
| `wartość` | Stała | `[42]` |

### 3.5 Wzorzec AND

Łączenie warunków dla jednej pozycji:

```matcha
match 15 as x {
    [> 10 AND < 20] => { println("W zakres od 11 do 19"); }
}
```

### Wykonanie matcha

1. Obliczane są wyrażenia w nagłówku
2. Sprawdzane są i wykonywane są po kolei wszystkie pasujące gałęzie `case` oprócz default
4. `default` wykonuje się tylko gdy NIC nie pasowało

```
match 10 as x {
    x > 5 => { println("A"); },   // Wykona się
    x == 10 => { println("B"); }, // Wykona się
    x < 0 => { println("C"); },   // NIE wykona się
    default => { println("D"); }  // NIE wykona się (bo A i B pasowały)
}
// Wyjście: A B
```

### 3.7 Match z Pustym Nagłówkiem

Działa jak wielokrotny if:

```matcha
match {
    x > 5 => { println("A"); },
    y < 10 => { println("B"); }
}
```


## 4. Przypadki Użycia Języka (Use Cases)

### a) Podstawy Języka

 Demonstracja implementacji standardowych struktur kontrolnych i podstaw języka.

```sc
// Definicja funkcji rekurencyjnej 
fun silnia(n) {
    if (n < 2) {
        return 1;
    }
    return n * silnia(n - 1);
}

fun main() {
    i = 0;
    // Pętla 'while' 
    while (i <= 5) {
        wynik = silnia(i);
        // Instrukcja warunkowa if
        if (wynik > 10) {
            println(i, "!", " = ", wynik, " - Ta silnia jest duża");
        } else {
            println(i, "!", " = ", wynik, " - Ta silnia jest mała");
        }
        i = i + 1; 
    }
}

main(); // Wywołanie funkcji
```

### b) match - Nagłówek Obliczeniowy i Zasięg Aliasów

`match` poprawnie oblicza wyrażenia w nagłówku (w tym wywołania funkcji) i tworzy dla nich scope

```sc
var x = 5;
match 
    x * 2 as v1, // v1 = 10
    silnia(x) as v2 // v2 = 120
{
    v1 > 5 => { println("OK"); }
}

# println(v1); // tu już nie ma zasięgu, będzie błąd
```

### c) match - Tryb Wyrażeń Warunkowych (tryb B)

`case`  działa podobno do zwykłego ifa, używając bindów z nagłówka. Obsługuje  logikę z AND, OR i nawiasy `()`.

```sc
match 10 as x, 20 as y {
    (x > 5 && y < 100) || (x < 0) => {
        println("Warunek złożony spełniony");
    }
}
// Oczekiwane wyjście: "Warunek złożony spełniony"
```

### d) match - Tryb Wzorców Pozycyjnych (tryb A)

 `case` potrafi używać specjalnej składni `[...]` do  dopasowania wzorców dla odpowiednich w kolejności bindów z nagłówka.


```sc
match 10 as v1, "hello" as v2 {
 
    [> 5, is string] => {   
        println("Wzorzec pozycyjny pasuje");
    }
}
// Oczekiwane wyjście: "Wzorzec pozycyjny pasuje"
```

### e) match - Wzorzec Złożony AND (wewnątrz [])


```sc
match 15 as v1 {
    
    [> 10 AND < 20] => { 
        println("wiek w zadanym przedziale");
    }
}
// Oczekiwane wyjście: "wiek jest w przedziale 10-20"
```

### f) match - Logika "Wykonaj Wszystkie Pasujące"

należy przetestować WSZYSTKIE gałęzie matcha, i wykonać kod dla każdej, która jest prawdziwa.

```sc
match 10 as x {
    // 1. Ten warunek jest Prawdziwy -> wykona się
    x > 5 => {
        println("Gałąź 1 (x > 5)");
    },
    // 2. Ten warunek też jest Prawdziwy -> wykona się
    x == 10 => {
        println("Gałąź 2 (x == 10)");
    },
    // 3. Ten warunek jest Fałszywy -> pomijamy
    x < 0 => {
        println("Gałąź 3 (x < 0)");
    }
}
// Oczekiwane wyjście:
// Gałąź 1 (x > 5)
// Gałąź 2 (x == 10)
```

### g) match - Gałąź default (Wykonanie)

Gałąź `default` wykonuje się tylko wtedy, gdy żadna inna gałąź `case` nie pasowała.


```sc
match 10 as x {
    x < 0 => { /* pominięte */ },
    x == 5 => { /* pominięte */ },
    default => {
        println("Domyślne");
    }
}
// na wyjściu będzie: "Domyślne"
```

### h) match - Gałąź default (Pominięcie)

Gałąź `default` nie wykonuje się, jeśli cokolwiek innego pasowało 

```sc
match 10 as x {
        x > 5 => { println("OK"); }, // Coś pasowało
    default => { println("ZŁY"); } // Musi być pominięte
}
// Oczekiwane wyjście: "OK"
```

### i) (Przypadek Brzegowy): match - Pusty Nagłówek

`match` jest dopuszczalny bez aliasów, działa jak zwykły if/else if

```sc
match {
    case 10 > 5 => { println("A"); }, // Wykona się
    case "a" == "a" => { println("B"); }  // Wykona się
}
// Oczekiwane wyjście: A, B
```

### j)  match - Wzorzec Pozycyjny - pomijanie argumentów dla `_`

należy pominać sprawdzanie pierwszego aliasu, i przejść od razu do drugiego

```sc
match 10 as v1, "hello" as v2 {
    case [_, is string] => { println("OK"); }
}
// Oczekiwane wyjście: "OK"
```

### k)  match - Pusty Wzorzec Pozycyjny

Sprawdzenie, jak interpreter obsługuje pusty nagłówek i pusty wzorzec.

```sc
match {
    // Tłumaczenie: (True)
    case [] => { println("OK"); }
}
// Oczekiwane wyjście: "OK" 
```

### l) (Test Negatywny) Zła liczba wzorców

 Parser musi wykryć, że liczba wzorców w `[...]` nie zgadza się z liczbą aliasów w nagłówku.

```sc
match 10 as v1, 20 as v2 {
    case [is int] => { ... } 
}
// Oczekiwany Błąd:  Niezgodność liczby wzorców. Oczekiwano 2, znaleziono 1.
```

### m) (Test Negatywny): Wzorzec zamiast Wyrażenia

 Parser musi wykryć, że  składnia wzorca (`> 10`) nie jest dozwolona w trybie "Wyrażenia Warunkowego".

```sc
match 10 as v1 {
    // BŁĄD: To nie jest wyrażenie. Brakuje aliasu 'v1'
    > 10 => { ... }
}
// Oczekiwany Błąd:  Nieoczekiwany token '>'. Oczekiwano '[', lub oczekiwano wyrażenia (np. 'v1')
```


### n)(Test Negatywny): Użycie Złego Aliasu

**Cel**: Interpreter musi wykryć próbę użycia aliasu, który nie został zdefiniowany w nagłówku.

```sc
match 10 as v1 {
    case v2 == 10 => { ... } // v2 nie istnieje
}
// Oczekiwany Błąd: Niezdefiniowana zmienna 'v2'.
```

---

## 5. Obsługa Błędów

### 5.1 Kategorie Błędów

| Kategoria | Moduł | Opis |
|-----------|-------|------|
| Leksykalny | Lexer | Nieprawidłowe tokeny |
| Składniowy | Parser | Nieprawidłowa struktura kodu |
| Wykonania | Interpreter | Błędy w czasie działania |

### 5.2 Format Komunikatów

```
[Typ błędu] - line X, col Y: Opis błędu
```

### 5.3 Błędy Leksykalne

| Błąd | Opis |
|------|------|
| `InvalidCharacterError` | Nieoczekiwany znak |
| `UnterminatedStringError` | Niezamknięty string |
| `HardLimitError` | Przekroczony limit (np. długość identyfikatora), przerwanie analizy leksykalnej |
| `IntegerOverflowError` | Przepełnienie liczby całkowitej |
| `UnterminatedStringError` | Niezakończony string |
| `SoftLimitError` | Przekroczony limit (np. długość identyfikatora), analiza była kontynuowana|

Przykład:
```
Błąd leksykalny [5:10]: Unterminated string literal
```

### 5.4 Błędy Składniowe

| Błąd | Opis |
|------|------|
| `MissingTokenError` | Brak oczekiwanego tokenu |
| `UnexpectedTokenError` | Nieoczekiwany token |
| `DuplicateDefinitionError` | Zduplikowana definicja |
| `InvalidSyntaxError` | Nieprawidłowa składnia |
|`MissingStatementError` | Brakująca instrukcja |
|`MissingExpressionError` | Brakujące wyrażenie |

Przykład:
```
Parser error at line 8, col 5: Expected '=>' after case condition
```

### 5.5 Błędy Wykonania

| Błąd | Opis |
|------|------|
| `TypeError` | Niezgodność typów |
| `NameError` | Niezdefiniowana nazwa |
| `ValueError` | Nieprawidłowa wartość (np. dzielenie przez 0) |
| `ArgumentError` | Nieprawidłowa liczba argumentów |
| `LimitError` | Przekroczony limit (rekurencji) |
| `RuntimeError` | Ogólny błąd wykonania |

Przykłady:
```
Runtime Error - line 15, col 12: Cannot perform '+' on int and string. Types must match exactly
Runtime Error - line 8, col 5: Division by zero
Runtime Error - line 3, col 1: 'break' outside of loop
Runtime Error: Maximum recursion depth exceeded (1000)
```
## 5. Notacja EBNF

Gramatyka jest podzielona na część leksykalną  i składniową

### 5.1 Część Leksykalna (Symbole Terminalne)

```ebnf
#  Słowa Kluczowe
FUN               ::= "fun"
BREAK             ::= "break"
RETURN            ::= "return"
CONTINUE         ::= "continue"
VAR               ::= "var"
IF                ::= "if"
ELSE              ::= "else"
WHILE             ::= "while"
MATCH             ::= "match"
AS                ::= "as"
CASE              ::= "case"
DEFAULT           ::= "default"
IS                ::= "is"
TRUE              ::= "true"
FALSE             ::= "false"
TYPE_INT          ::= "int"
TYPE_STR          ::= "string"
TYPE_FLT          ::= "float"
TYPE_BOOL         ::= "bool"

# Literały 
IDENTIFIER        ::= [a-zA-Z_][a-zA-Z0-9_]*
INT_LITERAL       ::= [0-9]+
FLOAT_LITERAL     ::= [0-9]+ "." [0-9]+
STRING_LITERAL    ::= '"' ( [^"] | '\"' )* '"'

# Operatory 
PLUS              ::= "+"
MINUS             ::= "-"
MULTIPLY          ::= "*"
DIVIDE            ::= "/"
NOT               ::= "!"
ASSIGN            ::= "="
ARROW             ::= "=>"

EQUAL             ::= "=="
NOT_EQUAL         ::= "!="
LESS              ::= "<"
LESS_EQ           ::= "<="
GREATER           ::= ">"
GREATER_EQ        ::= ">="

AND               ::= "&&"
OR                ::= "||"
# AND dla wzorców jest oddzielnym tokenem, tu nie jestem pewien
AND_PATTERN       ::= "AND"

LPAREN            ::= "("
RPAREN            ::= ")"
LBRACE            ::= "{"
RBRACE            ::= "}"
LBRACKET          ::= "["
RBRACKET          ::= "]"
COMMA             ::= ","
SEMICOLON         ::= ";"
WILDCARD          ::= "_"
```

### 5.2 Część Składniowa

```ebnf
program             ::== {function_definition} | {global_variable}

statement           ::== match_statement
                     |   if_statement
                     |   while_statement
                     |   return_statement
                     |   expression_statement
                     |   block_statement
                     |   assign_or_call_statement
                     |   break_statement
                     |   continue_statement
                     ;

block_statement     ::== LBRACE { statement } RBRACE

function_definition ::== FUN IDENTIFIER LPAREN param_list RPAREN block_statement
param_list          ::== [ IDENTIFIER { COMMA IDENTIFIER } ]

if_statement        ::== IF LPAREN expression RPAREN block_statement
                         [ ELSE block_statement ]
while_statement     ::== WHILE LPAREN expression RPAREN block_statement
return_statement    ::== RETURN [ expression ] SEMICOLON
assign_or_call_statement ::== call_or_identifier [ ASSIGN expression ] SEMICOLON 
expression_statement::== expression SEMICOLON
break_statement     ::== BREAK SEMICOLON
continue_statement  ::== CONTINUE

#  Instrukcja 'match'
match_statement     ::== MATCH match_header LBRACE { case_branch } RBRACE
match_header        ::== [ expression [AS IDENTIFIER] { COMMA expression [AS IDENTIFIER] } ] 



case_branch         ::== case_condition ARROW block_statement [ COMMA ]

# Parser decyduje na podstawie pierwszego tokenu:
case_condition      ::== positional_pattern     # Jeśli token to LBRACKET '['
                     |   DEFAULT                # Jeśli token to DEFAULT
                     |   expression             # W innym przypadku
                     ;

# Gramatyka dla wzorców (np. case [_, >10]):

positional_pattern  ::== LBRACKET [ pattern_list ] RBRACKET 
pattern_list        ::== and_pattern { COMMA and_pattern }
and_pattern         ::== single_pattern { AND_PATTERN single_pattern } # Tylko AND, jeszcze pomyślę na ORami
single_pattern      ::== constant_pattern | relational_pattern | type_pattern | wildcard_pattern
wildcard_pattern    ::== WILDCARD
type_pattern        ::== IS type
relational_pattern  ::== (GREATER | LESS | GREATER_EQ | LESS_EQ | EQUAL | NOT_EQUAL) expression
constant_pattern    ::== literal

# Gramatyka Wyrażeń:

expression          ::== logic_or
logic_or            ::== logic_and { OR logic_and }
logic_and           ::== equality { AND equality }
equality            ::== comparison { (EQUAL | NOT_EQUAL) comparison }
comparison          ::== term { (GREATER | GREATER_EQ | LESS | LESS_EQ) term }
term                ::== factor { (PLUS | MINUS) factor }
factor              ::== unary { (MULTIPLY | DIVIDE) unary }
unary               ::= [ NOT | MINUS ] primary
primary             ::== literal
                     |   LPAREN expression RPAREN
                     |   call_or_identifier
                     ;

call_or_identifier  ::== IDENTIFIER [ LPAREN argument_list RPAREN ]
argument_list       ::== [ expression { COMMA expression } ]
literal             ::== INT_LITERAL | FLOAT_LITERAL | STRING_LITERAL | TRUE | FALSE
type                ::== TYPE_INT | TYPE_STR | TYPE_FLT | TYPE_BOOL
```



# Struktura Projektu

### 7.1 Moduł Reader (CharReader)

**Cel**: Dostarczanie znaków do leksera.

**Interfejs**:
- `current()` - zwraca aktualny znak
- `advance()` - przesuwa do następnego znaku
- `position()` - zwraca pozycję (linia, kolumna)
- `check_next()` - podgląd następnego znaku bez przesuwania

### 7.2 Moduł Lexer

**Cel**: TWorzenie tokenów z  kodu źródłowego.

**Cechy**:
- Leniwa tokenizacja
- Obsługa limitów (soft i hard) dla identyfikatorów, stringów, liczb
- Walidacja escape sequences w stringach

**Interfejs**:
- `get_next_token()` - zwraca następny token

**Limity**:
- Maksymalna długość identyfikatora: 64 (soft), 640 (hard)
- Maksymalna długość stringa: 1024 (soft), 10240 (hard)
- Maksymalna wartość int: 2147483647

### 7.3 Moduł Parser

**Cel**: Budowanie drzewa AST z tokenów.

**Cechy**:
- Parser RD
- Wykrywanie duplikatów (funkcje, parametry, aliasy)
- Obsługa dwóch trybów case w match
- Strategia obsługi błędów: ABORT(przerywamy parsowanie) lub CONTINUE(kontynuujemy)

**Interfejs**:
- `parse_program()` - parsuje cały program, zwraca AST

### 7.4 Moduł Interpreter

**Cel**: Wykonanie programu na podstawie AST.

**Cechy**:
- Wzorzec Visitor do przechodzenia AST
- Zarządzanie środowiskiem (Environment) z zakresami
- Obsługa rekurencji z limitem głębokości (1000)

**Interfejs**:
- `load(program)` - ładuje program (rejestruje funkcje)
- `invoke(function_name, args)` - wywołuje funkcję, domyślnie main

### 7.6 Moduł Environment

**Cel**: Zarządzanie stanem wykonania.

**Komponenty**:
- `Scope` - pojedynczy zakres zmiennych
- `MatchScope` - specjalny zakres dla match z aliasami
- `CallContext` - kontekst wywołania funkcji
- `Environment` - przechowuje listę callcontextów

**Cechy**:
- Flagi sterujące: break, continue, return
- Śledzenie głębokości pętli
- Zarządzanie funkcjami globalnymi


# 7. Testy


## 7.1 Testy Jednostkowe


### Lekser:

- Testy pozytywne dla każdego tokenu .
- Testy dla błędów (np. niezamknięty string, nieznany znak).
- **Wejście:** Ciąg znaków; **Wyjście:** Lista tokenów.

### Parser:

- Testy dla każdej produkcji (np. function_definition).
- Testy dla każdej alternatywy (np. kluczowy test `case [...]` vs `case ...`).
- Testy negatywne dla niepoprawnych sekwencji tokenów (np. brak `=>`).
- **Wejście:** Lista tokenów; **Wyjście:** Struktura AST.

### Interpreter:

- Testy logiki if, while
- Testy dla każdego przypadku użycia match 
- **Wejście:**  zbudowane drzewo AST; **Wyjście:** Oczekiwany wynik lub błąd.

## 7.2 Testy Integracyjne 

 Mają na celu sprawdzenie czy moduły poprawnie ze sobą współpracują.
### Logika:

-  ciągi znaków będą przepuszczane przez cały potok.
- Ich wyjście na konsolę będzie porównywane z oczekiwanym rezultatem.
- Zestaw testów będzie zawierał  Przykłady Użycia Języka z Sekcji 3.
- testy pozytywne jak i negatywne będą równie ważne
---

## 8. Testowanie

Testy interpretra w pytest, tes
### 8.1 Struktura Testów

```
tests/
├── conftest.py              # Fixtures i helpery
├── test_lexer.py            # Testy leksera (unittest)
├── test_parser.py           # Testy parsera (unittest)
├── test_interpreter_programs.py    # testy programów (pytest)
└── test_interpreter_edge_cases.py  # testy przypadków brzegowych (pytest)
└──

```

### 8.2 Kategorie Testów

**Testy jednostkowe**:
- Lexer: tokenizacja, limity
- Parser: każde produkcje, błędy składniowe
- Reader: odczytywnie sekwencji znaków, znaku końca linii, 
    testy podglądania kolejnego znaku

**Testy integracyjne**:
- Pełne programy przez cały pipeline
- Algorytmy (silnia, Fibonacci, NWD)
- Zagnieżdżone struktury

**Testy negatywne**:
- Błędy typów
- Niezdefiniowane zmienne/funkcje
- Break/continue poza pętlą
- Przekroczenie limitów

### 8.3 Uruchamianie Testów

```bash
# Wszystkie testy interpretera
pytest tests/ -v
```
```bash
# wszystkie testy parsera, lexera i readera
python3 unittest discover
```

---

## Uruchamianie Programu

Z poziomu katalogu głównego projektu:

### Z pliku źródłowego
```bash
python3 main.py nazwa_pliku.matcha
```

### Z kodu podanego bezpośrednio w linii poleceń
```bash
python3 main.py -c "fun main() { print("Hello") }"
```

### Przykład
