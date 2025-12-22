from typing import Optional

from src.token_type import TokenType
from src.token import Token
from src.lexer import Lexer
from src.ast_nodes import (
    Program, Statement, Expression,
    BinaryExpression, UnaryExpression, Literal, Variable, FunctionCall,
    Block, IfStatement, WhileStatement, ReturnStatement, 
    FunctionDefinition, MatchStatement, FunctionCallStatement, CaseBranch, AssignmentStatement,
)

class Parser:
    def __init__(self, lexer: Lexer, error_handler):
        self.lexer = lexer
        self.error_handler = error_handler
        self.current_token = None
        
        self.advance()

    def advance(self):
        self.current_token = self.lexer.get_next_token()

    def error(self, message: str):
     
        if self.current_token:
            pos = self.current_token.position
            val = self.current_token.value if self.current_token.value is not None else self.current_token.type
            self.error_handler(f"Error at {pos} ('{val}'): {message}")
        else:
            self.error_handler(f"Error at Unknown: {message}")

    def consume(self, expected_type: TokenType, error_message: str) -> bool:
      
        if self.current_token.type == expected_type:
            self.advance()
            return True
        else:
            self.error(f"{error_message} (Found: {self.current_token.type.name})")
            return False
            
    def match(self, *types: TokenType) -> bool:
        # czy obecny token type jest jednym z podanych typów

        return self.current_token.type in types


    def parse_program(self) -> Program:
        statements: list[Statement] = []
        #wywalic statementy, zamaist tego slownik definicji funkcji
        while (stmt := self.try_parse_statement()):
        
            statements.append(stmt)

        return Program(statements)

    
    def try_parse_statement(self) -> Optional[Statement]:

        if (stmt := self.try_parse_if_statement()): return stmt
        if (stmt := self.try_parse_while_statement()): return stmt
        if (stmt := self.try_parse_return_statement()): return stmt
        if (stmt := self.try_parse_match_statement()): return stmt
        if (stmt := self.try_parse_function_definition()): return stmt
        if (stmt := self.try_parse_block()): return stmt
        

        # zmiana - assign lub call jak na wykladzie
        if (stmt := self.try_parse_assign_or_call_statement()): return stmt

        return None

    # statements
    def try_parse_block(self) -> Optional[Statement]:

        if not self.match(TokenType.LBRACE):
            return None
        self.advance() 

        stmts = []
        while (stmt:= self.try_parse_statement()):
            stmts.append(stmt)
            self.advance() 

        self.consume(TokenType.RBRACE, "Expected '}' after block")
        return Block(stmts)

    def try_parse_if_statement(self) -> Optional[Statement]:
        if not self.match(TokenType.IF):
            return None
        self.advance()

        self.consume(TokenType.LPAREN, "Expected '(' after 'if'")
        if (condition:= self.try_parse_expression()) is None:
            self.error("expression needed in if statement")
        self.consume(TokenType.RPAREN, "Expected ')' after condition")

        then_branch = self.try_parse_statement()
        # sprawdzamy czy istnieje then_branch
        else_branch = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_branch = self.try_parse_statement()
            #sprawdzamy czy else_branch jest nullem
    

        return IfStatement(condition, then_branch, else_branch)

    def try_parse_while_statement(self) -> Optional[Statement]:
        
        if not self.match(TokenType.WHILE):
            return None
        self.advance()

        self.consume(TokenType.LPAREN, "Expected '(' after while")
        if (condition:= self.try_parse_expression()) is None:
            self.error("Expected block in while loop")
        self.consume(TokenType.RPAREN, "need ')'")
        # musimy sprawdzic czy body istnieje

        body = self.try_parse_block()
        # musi byc parse statement, i trzeba umiescic w gramatyce
        return WhileStatement(condition, body)

    def try_parse_return_statement(self) -> Optional[Statement]:
        if not self.match(TokenType.RETURN):
            return None
        self.advance()

        expr = None
        # parsujemy wyrażenie gdy nie ma średnika od razu
        if not self.match(TokenType.SEMICOLON):
            expr = self.try_parse_expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after return")
        return ReturnStatement(expr)

    def try_parse_function_definition(self) -> Optional[Expression]:

        if not self.match(TokenType.FUN):
            return None
        self.advance() 

        # Nazwa funkcji 
        if self.match(TokenType.IDENTIFIER):
            name = self.current_token.value 
            self.advance()
        else:
            self.error("Expected function name")
            # rzucamy wyjatek, name = error jest bez sensu, konczymy parsowanie
            # zastanowic kiedy kontynuujemy parsownaie a kiedy konczymy 
            name = "error"

        self.consume(TokenType.LPAREN, "Expected '('")
        
        params = self._parse_parameter_list()
        
        self.consume(TokenType.RPAREN, "Expected ')' after parameters")

        body = self.try_parse_block()
        # trzeba sprawdzic czy blok został rzeczywiscie stworzony
        # obiekt tworzony w fdefinition fajnie by bylo jakby mial pozycje
        return FunctionDefinition(name, params, body)

    def _parse_parameter(self) -> str:
        if self.match(TokenType.IDENTIFIER):
                parameter = self.current_token.value
                self.advance()
                return parameter

    def _parse_parameter_list(self) -> list[str]:

        params = []

        if (parameter := self.parse_parameter()):
            params.append(parameter)
        else:
            return params
        
        while self.match(TokenType.COMMA):
                self.advance()
                if parameter := self._parse_parameter():
                    params.append(parameter)

                else:
                    self.error("Expected parameter name after coma")
        return params

            

    def try_parse_match_statement(self) -> Optional[Statement]:
        pass

    def _parse_case_condition(self):
        pass


    def try_parse_assign_or_call_statement(self) -> Optional[Statement]:
        if not self.match(TokenType.IDENTIFIER):
            return None

        name = self.current_token.value
        self.advance() 

        # assign
        # 
        if self.match(TokenType.ASSIGN):
            self.advance()
            expr = self.try_parse_expression()
            if expr is None:
                self.error("Expected expression after assignment")
            self.consume(TokenType.SEMICOLON, "Expected ';'")
            return AssignmentStatement(name, expr)
        # powinno byc w osobnej metodzie
        # call
        elif self.match(TokenType.LPAREN):
            self.advance()
            args = self.parse_argument_list()
            self.consume(TokenType.RPAREN, "Expected ')'")
            self.consume(TokenType.SEMICOLON, "Expected ';'")
            return FunctionCallStatement(FunctionCall(name, args))

        else:
            self.error("Expected  '=' or  '(' after identifier")
            return None


    def try_parse_expression(self) -> Optional[Expression]:
        return self.try_parse_logic_or()

    def try_parse_logic_or(self) -> Optional[Expression]:
        left = self.try_parse_logic_and()
        if left is None: return None

# tokeny nie powinny sie pojawiac w drzewie, 
# zrobic klase or_expression i tak dalej, 
        while self.match(TokenType.OR):
            op = self.current_token
            self.advance()
            right = self.try_parse_logic_and()
            if right is None:
                self.error("need logic_and after 'or'")
                return left
            left = BinaryExpression(left, op, right)
        return left

    def try_parse_logic_and(self) -> Optional[Expression]:
        left = self.try_parse_equality()
        if left is None: return None

        while self.match(TokenType.AND):
            op = self.current_token
            self.advance()
            right = self.try_parse_equality()
            if right is None:
                self.error("need equality after 'and'")
                return left
            left = BinaryExpression(left, op, right)
        return left

    def try_parse_equality(self) -> Optional[Expression]:
        left = self.try_parse_comparison()
        if left is None: return None

        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op = self.current_token
            self.advance()
            right = self.try_parse_comparison()
            if right is None:
                self.error("Expected comparison after equality operator")
                return left
            left = BinaryExpression(left, op, right)
        return left

    def try_parse_comparison(self) -> Optional[Expression]:
        left = self.try_parse_term()
        if left is None: return None
# mapowanie typu tokenu operatora na konstruktor obiektu odpowiedniej klasy
# pytać getem o konstruktor
        while self.match(TokenType.GREATER, TokenType.GREATER_EQ, TokenType.LESS, TokenType.LESS_EQ):
            op = self.current_token
            self.advance()
            right = self.try_parse_term()
            if right is None:
                self.error("Expected term after comparison")
                return left
            left = BinaryExpression(left, op, right)
        return left

# ebnf - niefortunne nazwy wewnatrz expression (term/factor)
    def try_parse_term(self) -> Optional[Expression]:
        left = self.try_parse_factor()
        if left is None: return None

        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.current_token
            self.advance()
            right = self.try_parse_factor()
            if right is None:
                self.error("Expected term after + or -")
                return left
            left = BinaryExpression(left, op, right)
        return left

    def try_parse_factor(self) -> Optional[Expression]:
        left = self.try_parse_unary()
        if left is None: return None

        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            op = self.current_token
            self.advance()
            right = self.try_parse_unary()
            if right is None:
                self.error("Expected unary after * or /")
                return left
            left = BinaryExpression(left, op, right)
        return left

# w ebnfie wywolujemy primary tylko raz, a w kodzie 2
    def try_parse_unary(self) -> Optional[Expression]:
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.current_token
            self.advance()
            operand = self.try_parse_primary() 
            if operand is None:
                self.error("Expected expression after not or '-'")
                return None
            return UnaryExpression(op, operand)
        
        return self.try_parse_primary()


    def try_parse_primary(self) -> Optional[Expression]:
        tt = self.current_token.type

        if tt == TokenType.INT_LITERAL:
            val = self.current_token.value
            self.advance()
            return Literal(val, "int")
        elif tt == TokenType.FLOAT_LITERAL:
            val = self.current_token.value
            self.advance()
            return Literal(val, "float")
        elif tt == TokenType.STRING_LITERAL:
            val = self.current_token.value
            self.advance()
            return Literal(val, "string")
        elif tt == TokenType.TRUE:
            self.advance()
            return Literal(True, "bool")
        elif tt == TokenType.FALSE:
            self.advance()
            return Literal(False, "bool")
        #355 do 361 powinno byc try parse
        elif tt == TokenType.LPAREN:
            self.advance()
            expr = self.try_parse_expression()
            if expr is None:
                self.error("Expected expression inside")
            self.consume(TokenType.RPAREN, "Expected ')'")
            return expr
        #identifier powinien byc sprawdzany w 30, w call or id expression
        elif tt == TokenType.IDENTIFIER:
            return self.parse_call_or_identifier_expression()

        return None


    def parse_call_or_identifier_expression(self) -> Expression:
        #srp, nie sprawdzamy w parse primary, tylko tutaj
        name = self.current_token.value
        self.advance()
        # zrobic funkcje parsujace do lparen, i moze zwroci none
        if self.match(TokenType.LPAREN):
            self.advance()
            args = self.parse_argument_list()
            #tu sprwadzamy rparen przed argument list
            self.consume(TokenType.RPAREN, "Expected ')'")
            return FunctionCall(name, args)
        else:
            return Variable(name)

    def parse_argument_list(self) -> list[Expression]:
        args = []
        if arg := self.try_parse_expression():

            args.append(arg)
            while self.match(TokenType.COMMA):
                self.advance()
                next_arg = self.try_parse_expression()
                if next_arg:
                    args.append(next_arg)
                else:
                    self.error("Expected expression after comma")
        return args