from typing import Optional

from src.token_type import TokenType
from src.token import Token
from src.lexer import Lexer

from src.ast_nodes import (
    Program, Statement, Expression, SourceLocation,
    AddExpression, SubtractExpression, MultiplyExpression, DivideExpression,
    OrExpression, AndExpression, EqualExpression, NotEqualExpression,
    LessExpression, LessEqualExpression, GreaterExpression, GreaterEqualExpression,
    UnaryMinusExpression, NotExpression,
    Literal, Variable, FunctionCall,
    Block, IfStatement, WhileStatement, ReturnStatement, 
    FunctionDefinition, FunctionCallStatement, AssignmentStatement,
)

class ParserError(Exception):
    pass

STRATEGY_CONTINUE = "CONTINUE"
STRATEGY_ABORT = "ABORT"

class Parser:
    def __init__(self, lexer: Lexer, error_handler):
        self.lexer = lexer
        self.error_handler = error_handler
        self.current_token = None
        
        self.advance()

    def advance(self):
        self.current_token = self.lexer.get_next_token()

    def error(self, message: str, strategy: str = "CONTINUE"):
        if self.current_token:
            pos = self.current_token.position
            val = self.current_token.value if self.current_token.value is not None else self.current_token.type
            full_msg = f"Error at {pos} ('{val}'): {message}"
        else:
            full_msg = f"Error at Unknown: {message}"

        self.error_handler(full_msg)

        if strategy == "ABORT":
            raise ParserError(full_msg)

    def consume(self, expected_type: TokenType, error_message: str, strategy: str = "CONTINUE") -> bool:
        if self.current_token.type == expected_type:
            self.advance()
            return True
        else:
            self.error(f"{error_message} (Found: {self.current_token.type.name})", strategy) # poprawilem str na strategy
            return False
        
    def match(self, *types: TokenType) -> bool:
        return self.current_token.type in types

    def _loc(self) -> SourceLocation:
        pos = self.current_token.position
        return SourceLocation(pos.line, pos.column)

    def parse_program(self) -> Program:
        functions = {} 
        start_loc = self._loc() 

        while (func_def := self.try_parse_function_definition()):
            if func_def.name in functions:
                self.error(f"Function '{func_def.name}' is already defined")

            functions[func_def.name] = func_def

        # except ParserError:
        #     return Program(list(functions.values()), start_loc)

        return Program(list(functions.values()), start_loc)

    
    def try_parse_statement(self) -> Optional[Statement]:
        if (stmt := self.try_parse_if_statement()): return stmt
        if (stmt := self.try_parse_while_statement()): return stmt
        if (stmt := self.try_parse_return_statement()): return stmt
        if (stmt := self.try_parse_match_statement()): return stmt
        if (stmt := self.try_parse_block()): return stmt
        
        # zmiana - assign lub call jak na wykladzie
        if (stmt := self.try_parse_assign_or_call_statement()): return stmt

        return None

    # statements
    def try_parse_block(self) -> Optional[Statement]:
        if not self.match(TokenType.LBRACE):
            return None
        
        loc = self._loc() 
        self.advance() 

        stmts = []
        while (stmt:= self.try_parse_statement()):
            stmts.append(stmt)
            # self.advance() 

        self.consume(TokenType.RBRACE, "Expected '}' after block")
        return Block(stmts, loc) 

    def try_parse_if_statement(self) -> Optional[Statement]:
        if not self.match(TokenType.IF):
            return None
        
        loc = self._loc() 
        self.advance()

        self.consume(TokenType.LPAREN, "Expected '(' after 'if'")

        if (condition:= self.try_parse_expression()) is None:
            self.error("expression needed in if statement")

        self.consume(TokenType.RPAREN, "Expected ')' after condition")

        then_branch = self.try_parse_block()

        if then_branch is None:
            self.error("Expected statement after 'if' condition", strategy="ABORT")

        else_branch = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_branch = self.try_parse_block()
            if else_branch is None:
                self.error("Expected block statement after 'else'", strategy="ABORT")
    
        return IfStatement(condition, then_branch, else_branch, loc) 

    def try_parse_while_statement(self) -> Optional[Statement]:
        if not self.match(TokenType.WHILE):
            return None
        
        loc = self._loc() 
        self.advance()

        self.consume(TokenType.LPAREN, "Expected '(' after while")
        if (condition:= self.try_parse_expression()) is None:
            self.error("Expected block in while loop")
        self.consume(TokenType.RPAREN, "need ')'")
        
        body = self.try_parse_block()

        if body is None:
            self.error("Expected block statement after while", strategy="ABORT")

        return WhileStatement(condition, body, loc) 

    def try_parse_return_statement(self) -> Optional[Statement]:
        if not self.match(TokenType.RETURN):
            return None
        
        loc = self._loc() 
        self.advance()

        expr = None
        if not self.match(TokenType.SEMICOLON):
            expr = self.try_parse_expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after return")
        return ReturnStatement(expr, loc) 

    def try_parse_function_definition(self) -> Optional[FunctionDefinition]:
        if self.match(TokenType.EOF):
            return None
        
        if not self.match(TokenType.FUN):
            self.error(f"Expected EOF or definition, found: {self.current_token.type}", strategy="ABORT")

            return None 

        loc = self._loc() 
        self.advance() 

        if self.match(TokenType.IDENTIFIER):
            name = self.current_token.value 
            self.advance()
        else:
            self.error("Expected function name", strategy="ABORT")
    
        self.consume(TokenType.LPAREN, "Expected '('", )
        params = self._parse_parameter_list()
        self.consume(TokenType.RPAREN, "Expected ')' after parameters")

        if (body := self.try_parse_block()) is None:
             self.error(f"Expected body for function '{name}'", strategy="ABORT")
        
        return FunctionDefinition(name, params, body, loc) 

    def _parse_parameter(self) -> str:
        if self.match(TokenType.IDENTIFIER):
                parameter = self.current_token.value
                self.advance()
                return parameter

    def _parse_parameter_list(self) -> list[str]:
        params = []
        if (parameter := self._parse_parameter()):
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

   

    def try_parse_logic_or(self) -> Optional[Expression]:
        left = self.try_parse_logic_and()
        if left is None: return None

        while self.match(TokenType.OR):
            loc = self._loc() 
            self.advance()
            right = self.try_parse_logic_and()
            if right is None:
                self.error("need logic_and after 'or'")
                return left
            
           
            left = OrExpression(left, right, loc) 
        return left

    def try_parse_logic_and(self) -> Optional[Expression]:
        left = self.try_parse_equality()
        if left is None: return None

        while self.match(TokenType.AND):
            loc = self._loc()
            self.advance()
            right = self.try_parse_equality()
            if right is None:
                self.error("need equality after 'and'")
                return left
            
           
            left = AndExpression(left, right, loc)
        return left

    def try_parse_equality(self) -> Optional[Expression]:
        left = self.try_parse_comparison()
        if left is None: return None

        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op_type = self.current_token.type 
            loc = self._loc()
            self.advance()
            right = self.try_parse_comparison()
            if right is None:
                self.error("Expected comparison after equality operator")
                return left
            
            if op_type == TokenType.EQUAL:
                left = EqualExpression(left, right, loc)
            else:
                left = NotEqualExpression(left, right, loc)
        return left

    def try_parse_comparison(self) -> Optional[Expression]:
        left = self.try_parse_term()
        if left is None: return None

        while self.match(TokenType.GREATER, TokenType.GREATER_EQ, TokenType.LESS, TokenType.LESS_EQ):
            op_type = self.current_token.type
            loc = self._loc()
            self.advance()
            right = self.try_parse_term()
            if right is None:
                self.error("Expected term after comparison")
                return left
            
            if op_type == TokenType.LESS:
                left = LessExpression(left, right, loc)
            elif op_type == TokenType.LESS_EQ:
                left = LessEqualExpression(left, right, loc)
            elif op_type == TokenType.GREATER:
                left = GreaterExpression(left, right, loc)
            elif op_type == TokenType.GREATER_EQ:
                left = GreaterEqualExpression(left, right, loc)
        return left

    def try_parse_term(self) -> Optional[Expression]:
        left = self.try_parse_factor()
        if left is None: return None

        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_type = self.current_token.type
            loc = self._loc()
            self.advance()
            right = self.try_parse_factor()
            if right is None:
                self.error("Expected term after + or -")
                return left
            
            if op_type == TokenType.PLUS:
                left = AddExpression(left, right, loc)
            else:
                left = SubtractExpression(left, right, loc)
        return left

    def try_parse_factor(self) -> Optional[Expression]:
        left = self.try_parse_unary()
        if left is None: return None

        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            op_type = self.current_token.type
            loc = self._loc()
            self.advance()
            right = self.try_parse_unary()
            if right is None:
                self.error("Expected unary after * or /")
                return left
            
            if op_type == TokenType.MULTIPLY:
                left = MultiplyExpression(left, right, loc)
            else:
                left = DivideExpression(left, right, loc)
        return left

    def try_parse_unary(self) -> Optional[Expression]:
        op_type = None
        loc = None

        if self.match(TokenType.NOT, TokenType.MINUS):
            op_type = self.current_token.type
            loc = self._loc() 
            self.advance()
        
        operand = self.try_parse_primary() 
        if operand is None:
            if op_type is not None:
                self.error("Expected expression after not or '-'")
            return None
        
        if op_type:
            if op_type == TokenType.MINUS:
                return UnaryMinusExpression(operand, loc)
            else:
                return NotExpression(operand, loc)
                
        return operand


    def try_parse_primary(self) -> Optional[Expression]:
        if (expr := self.parse_call_or_identifier_expression()):
            return expr
        
        if(expr := self.try_parse_parenthesized_expression()):
            return expr
        
        tt = self.current_token.type
        loc = self._loc() 

        if tt == TokenType.INT_LITERAL:
            val = self.current_token.value
            self.advance()
            return Literal(val, "int", loc) 
        elif tt == TokenType.FLOAT_LITERAL:
            val = self.current_token.value
            self.advance()
            return Literal(val, "float", loc) 
        elif tt == TokenType.STRING_LITERAL:
            val = self.current_token.value
            self.advance()
            return Literal(val, "string", loc) 
        elif tt == TokenType.TRUE:
            self.advance()
            return Literal(True, "bool", loc) 
        elif tt == TokenType.FALSE:
            self.advance()
            return Literal(False, "bool", loc)

        return None

    def try_parse_assign_or_call_statement(self) -> Optional[Statement]:
        loc = self._loc() 

        if (left := self.parse_call_or_identifier_expression()) is None:
            return None
        
        if self.match(TokenType.ASSIGN):
            self.advance()

            if isinstance(left, FunctionCall):
                    self.error("Cannot assign value to a function call")

            if(expr := self.try_parse_expression()) is None:
                self.error("Expected expression after assignment")

            self.consume(TokenType.SEMICOLON, "Expected ';' after assignment")

            return AssignmentStatement(left.name, expr, loc) 
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after statement")
    
        if isinstance(left, FunctionCall):
           
            return FunctionCallStatement(left.name, left.arguments, loc) 
        
        self.error("Statement with no effect", strategy="ABORT")
        return None

    def try_parse_expression(self) -> Optional[Expression]:
        return self.try_parse_logic_or()

    def try_parse_parenthesized_expression(self) -> Optional[Expression]:
        if not self.match(TokenType.LPAREN):
            return None
        
        self.advance() 
        expr = self.try_parse_expression()
        if expr is None:
            self.error("Expected expression inside parentheses")
            
        self.consume(TokenType.RPAREN, "Expected ')'")
        return expr 
    
    def parse_call_or_identifier_expression(self) -> Expression:
        if not self.match(TokenType.IDENTIFIER):
            return None
        
        loc = self._loc() 
        name = self.current_token.value
        self.advance()
        
        if self.match(TokenType.LPAREN):
            self.advance()
            args = []
            if not self.match(TokenType.RPAREN):
                args = self.parse_argument_list()
           
            self.consume(TokenType.RPAREN, "Expected ')'")
            return FunctionCall(name, args, loc) 
        else:
            return Variable(name, loc) 

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