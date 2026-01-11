# Projekt wstepny: Język "Matcha" 

## 1. Wstęp

Matcha jest językiem programowania ogólnego przeznaczenia. Został zaprojektowany jako język **silnie i dynamicznie typowany**, z **mutowalnymi zmiennymi**.

Język wspiera:
- Podstawowe typy danych: `int`, `float`, `str`, `bool`
- Standardowe operacje matematyczne i logiczne
- Komentarze
- Struktury  wymagane przez projekt:
  - Instrukcje warunkowe (`if`)
  - Pętle (`while`)
  - Definiowanie i wywoływanie funkcji (`fun`) z obsługą rekursji

###  Instrukcja `match`

 instrukcja `match`:

1. **Nagłówek Obliczeniowy**: Oblicza wyrażenia i binduje ich wyniki do tymczasowych aliasów:
```bash
`match 1 + 2 as zmienna_1, silnia(2) as zmienna_2
{
}
```
2. **Dwa tryby case**:
   - **Wzorce Pozycyjne** (`case [>10, is int] =>`) - unikalna składnia, wykrywająca w kolejności zbindowane w nagłówku argumenty, ten tryb jest aktywowany po wykryciu po symbolu case nawiasu kwadratowego
   - **Wyrażenia Warunkowe** (`case zmienna1 > 10 and zmienna 2 is int => `) - standardowa składnia

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

### 2.3 Zmienne

- **Deklaracja**: Zmienne są tworzone przy pierwszym przypisaniu. Użycie `var` jest opcjonalne:
  ```sc
  var x = 10;  // lub
  x = 10;
  ```
- **Mutowalność**: Zmienne są mutowalne, można nadpisywać ich wartość 
- **Zasięg**:  Zmienne zadeklarowane w bloku `{...}` (np. w `if`, `while`, `fun` lub `match`) nie są widoczne na zewnątrz

### 2.4 Operatory (od najwyższego priorytetu)

| Operator |
|----------|
| `!` (logiczne NOT) |
| `-` (unarny) | 
| `*`, `/` | 
| `+`, `-` (binarny) | 
| `>`, `>=`, `<`, `<=` | 
| `==`, `!=` | 3 | 
| `&&` (logiczne AND) | 
| `OR` (logiczne OR) | 
### 2.5 Komentarze
Komentarzezaczynają się od `//` i trwają do końca linii.

### 2.6 Instrukcje Warunkowe
`if (wyrażenie) { ... } else { ... }`

### 2.7 Instrukcja Pętli
 `while (wyrażenie) { ... }`

### 2.8 Funkcje

- Definiowane przez `fun nazwa(arg1, arg2) { ... }`
- Argumenty przekazywane przez wartość
- Wspierana rekursja

### 2.9 Funkcje Wbudowane

- `print(...)` i `println(...)` 
- `input()` - pobiera `str` ze standardowego wejścia
- `typeof(zmienna)` - zwraca typ jako `str`

### 2.10 Konwersje Typów (Silne Typowanie)

- Operacje arytmetyczne (`+`, `-`, `*`, `/`) są dozwolone tylko między `int` i `float` (chyba bez promocji `int` do `float`)
- Konkatenacja (`+`) jest dozwolona tylko dla `string + string`
- Operatory logiczne (`&&`, `||`) działają tylko na `bool`
- Każda inna kombinacja (np. `int + string`, `bool * int`) jest błędem wykonania 

---

## 3. Przypadki Użycia Języka (Use Cases)

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
    var i = 0;
    // Pętla 'while' 
    while (i <= 5) {
        var wynik = silnia(i);
        // Instrukcja warunkowa if
        if (wynik > 10) {
            println(i, "!", " = ", wynik, " - Ta silnia jest duża");
        } else {
            println(i, "!", " = ", wynik, " - Ta silnia jest mała");
        }
        i = i + 1; // Mutowalność zmiennych 
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
    case v1 > 5 => { println("OK"); }
}

# println(v1); // tu już nie ma zasięgu, będzie błąd
```

### c) match - Tryb Wyrażeń Warunkowych (tryb B)

`case`  działa podobno do zwykłego ifa, używając bindów z nagłówka. Obsługuje  logikę z AND, OR i nawiasy `()`.

```sc
match 10 as x, 20 as y {
    case (x > 5 && y < 100) || (x < 0) => {
        println("Warunek złożony spełniony");
    }
}
// Oczekiwane wyjście: "Warunek złożony spełniony"
```

### d) match - Tryb Wzorców Pozycyjnych (tryb A)

 `case` potrafi używać specjalnej składni `[...]` do  dopasowania wzorców dla odpowiednich w kolejności bindów z nagłówka.

**trudność**: Parser musi poprawnie jakoś przetłumaczyć te wzorce na zwykłe wyrażenia.

```sc
match 10 as v1, "hello" as v2 {
 
    case [> 5, is string] => {    // Parser tłumaczy to wewnętrznie na: (v1 > 5) AND (typeof(v2) == "string")
        println("Wzorzec pozycyjny pasuje");
    }
}
// Oczekiwane wyjście: "Wzorzec pozycyjny pasuje"
```

### e) match - Wzorzec Złożony AND (wewnątrz [])

Parser potrafi przetłumaczyć wiele wzorców dla jednej pozycji, łącząc je operatorem AND.

```sc
match 15 as v1 {
    
    case [> 10 AND < 20] => { // Parser tłumaczy to na: (v1 > 10) AND (v1 < 20)
        println("wiek w zadanym przedziale");
    }
}
// Oczekiwane wyjście: "Liczba jest nastolatkiem"
```

### f) match - Logika "Wykonaj Wszystkie Pasujące"

należy przetestować WSZYSTKIE gałęzie `case` i wykonać kod dla każdej, która jest prawdziwa.

```sc
match 10 as x {
    // 1. Ten warunek jest Prawdziwy -> wykona się
    case x > 5 => {
        println("Gałąź 1 (x > 5)");
    },
    // 2. Ten warunek też jest Prawdziwy -> wykona się
    case x == 10 => {
        println("Gałąź 2 (x == 10)");
    },
    // 3. Ten warunek jest Fałszywy -> pomijamy
    case x < 0 => {
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
    case x < 0 => { /* pominięte */ },
    case x == 5 => { /* pominięte */ },
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
    case x > 5 => { println("OK"); }, // Coś pasowało
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
    // Tłumaczenie: (true) && (typeof(v2) == "string")
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
    case > 10 => { ... }
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

## 4. Obsługa Błędów

Każdy błąd wstrzymuje wykonanie programu. Komunikaty o błędach będą zawierać typ błędu, lokalizację oraz  wiadomość co poszło nie tak.

**Format**: ` BŁĄD [<linia>:<kolumna>] (<Moduł>): <Wiadomość>`

### Przykłady Błędów

**Błąd Leksykalny:**
```
 BŁĄD [5:10] (Lekser): Niezamknięty literał string: "Hello...
```

**Błąd Składni:**
```
 BŁĄD [8:5] (Parser): Oczekiwano '=>' po warunku 'case', znaleziono ';'
```

**Błąd Składni:**
```
 BŁĄD [10:8] (Parser): Niezgodność liczby wzorców. Nagłówek 'match' zdefiniował 2 aliasy, ale wzorzec pozycyjny ma ich 3.
```

**Błąd Semantyczny:**
```
BŁĄD [12:9] : Użycie niezdefiniowanej zmiennej 'zmienna3'. Dostępne aliasy w tym 'match' to: 'zmienna1', 'zmienna2'.
```

**Błąd Wykonania:**
```
 BŁĄD [15:12] (Runtime): Nie można wykonać operatora '+' na typach 'int' i 'string'.
```

---

## 5. Notacja EBNF

Gramatyka jest podzielona na część leksykalną  i składniową

### 5.1 Część Leksykalna (Symbole Terminalne)

```ebnf
#  Słowa Kluczowe
FUN               ::= "fun"
BREAK             ::= "break"
RETURN            ::= "return"
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
program             ::== {function_definition}

statement           ::== match_statement
                     |   if_statement
                     |   while_statement
                     |   return_statement
                     |   expression_statement
                     |   block_statement
                     |   assign_or_call_statement
                     |   break_statement
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

---

# Struktura Projektu

Projekt będzie składał się z modułów:

## 6.1 Czytnik

 Moduł ten bedzie działał na pliku lub ciągu znaków. Jego zadaniem jest podawanie pojedynczych znaków do Leksera i śledzenie pozycji [linia:kolumna] 
 Jest "pytany"  przez Lekser o następny znak.

### Interfejs:

- `next()`: Zwraca następny znak ze źródła i przesuwa wskaźnik.
- `current() : Zwraca aktualny znak.
- `position()`: Zwraca bieżącą pozycję (linia, kolumna).

## 6.2 Lekser

 Jest leniwy, czyli generuje jeden token tylko na żądanie Parsera.

###  Wymagania:

- Od razu konwertuje literały (np. "123") na wartości wewnętrzne (np. int(123)).
- wykrywa specyficzne błędy (np. niezamknięty string) i raportuje je do do modułu obsługi błędów

**Komunikacja:** Pobiera znaki z CharReader. Jest pytany przez Parser o następny token.

### Proponowany Interfejs:

- `next(): Pobiera znaki z czytnika, buduje token i go zwraca do parsera.
- `current(): Zwraca ostatnio wyprodukowany token

## 6.3 Parser (Parser)

 jako Parser Zejściowy Rekurencyjny (Recursive Descent). Jego zadaniem jest 'konsumowanie 'tokenów z Leksera i budowanie z nich Drzewa AST. 

### Wymaganie dla naszego matcha:

- dla wyrażenia pozycyjnego, musi działać jako "sprytny tłumacz", od razu budując AST zwykłego wyrażenia logicznego, aby uprościć pracę Interpretera. czyli `case [_, is int]` musi zostać od razu 
zamienione na `case (true and typeof(zmienna2) == "int")`

**Komunikacja:** Pobiera tokeny z Lexer. Zwraca kompletne drzewo AST do Interpretera.

### Proponowany Interfejs:

- `parse() -> ASTNode`: Uruchamia proces parsowania, zwraca korzeń drzewa AST.

## 6.4 Interpreter (jeszcze nie wiem)

**Cel:** Przechodzi po drzewie AST  i wykonuje kod. 

### Kluczowe Wymagania:

- Tworzy tymczasowy zasięg dla aliasów, oblicza nagłówek, a następnie iteruje po caseach. musi obsłużyć logikę  `did_anything_match` dla default, czyli gdy żadna poprzednia gałąź nie została wykonana.
- Wszystkie casey  są już wcześniej przetłumaczone przez parser na zwykłe wyrażenia
- Funkcje wbudowane są traktowane tak samo jak funkcje użytkownika.

**Komunikacja:** Otrzymuje korzeń drzewa od Parsera, po czym wykonuje logikę.

### Proponowany Interfejs:

- `interpret(tree: ASTNode)`: Wykonuje program reprezentowany przez tree.
- `evaluate(expression_node: ASTNode) -> Value`: Wewnętrzna funkcja do obliczania wartości dowolnego wyrażenia.

## 6.5 Moduł Obsługi Błędów 

**Cel:** Moduł który zbiera błędy ze wszystkich innych etapów (Lekser, Parser, Interpreter).

**Komunikacja:** Wszystkie moduły mogą wypychać  błędy do tego modułu. 

### Proponowany Interfejs:

- `report_error(position, message, module_name)`: Metoda wywoływana przez Lekser, Parser, itp.
- `has_errors() -> bool`: Sprawdza, czy wystąpiły jakiekolwiek błędy.
- `print_diagnostics()`: Wypisuje wszystkie zebrane błędy w ustandaryzowanym formacie.

---

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
