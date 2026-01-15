from typing import Optional

from .token_type import TokenType
from .token import Token
from .lexer import Lexer

from .ast_nodes import *

class ParserError(Exception):
    def __init__(self, message: str, location: SourceLocation):
        self.message = message
        self.location = location
        super().__init__(f"Parser error at line {location.line}, col {location.column}: {message}")


class UnexpectedTokenError(ParserError):
    pass


class MissingTokenError(ParserError):
    pass


class DuplicateDefinitionError(ParserError):
    pass


class InvalidSyntaxError(ParserError):
    pass


class MissingExpressionError(ParserError):
    pass


class MissingStatementError(ParserError):
    pass

class Parser:
    def __init__(self, lexer: Lexer, error_handler):
        self.lexer = lexer
        self.error_handler = error_handler
        self.current_token = None
        
        self.advance()


    def advance(self) -> None:
        self.current_token = self.lexer.get_next_token()
        while self.match(TokenType.COMMENT):
            self.current_token = self.lexer.get_next_token()

    def _report_error(self, error: ParserError) -> None:
        self.error_handler(error)

    def consume(self, expected_type: TokenType, error_message: str, strategy: str = "ABORT") -> bool:
        if self.current_token.type == expected_type:
            self.advance()
            return True
        else:
            error = MissingTokenError(
                f"{error_message} (found: {self.current_token.type.name})",
                self._loc()
            )

            self._report_error(error)

            if strategy == "ABORT":
                raise error
            
        
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
                raise DuplicateDefinitionError(
                f"Function '{func_def.name}' is already defined",
                func_def.location  
            )

            functions[func_def.name] = func_def

        if self.match(TokenType.EOF):
            return Program(list(functions.values()), start_loc)

        raise UnexpectedTokenError(
                f"Unexpected token after function definitions: {self.current_token.type}",
                self._loc()
            )

    def try_parse_break(self) -> Optional[Statement]:

        if not self.match(TokenType.BREAK):
            return None
        loc = self._loc()
        self.advance()
       
        self.consume(TokenType.SEMICOLON, "expected semicolon after Break", strategy="CONTINUE")

        return BreakStatement(loc)
    
    def try_parse_continue(self) -> Optional[Statement]:
        if not self.match(TokenType.CONTINUE):
            return None
        loc = self._loc()
        self.advance()

        self.consume(TokenType.SEMICOLON, "expected semicolon after continue", strategy="CONTINUE")

        return ContinueStatement(loc)

    def try_parse_statement(self) -> Optional[Statement]:
        parsers = [
            self.try_parse_if_statement,
            self.try_parse_while_statement,
            self.try_parse_return_statement,
            self.try_parse_match_statement,
            self.try_parse_block,
            self.try_parse_break,
            self.try_parse_continue,
            self.try_parse_assign_or_call_statement,
        ]
        
        for parser in parsers:
            if (stmt := parser()):
                return stmt
        return None

    def try_parse_block(self) -> Optional[Statement]:
        if not self.match(TokenType.LBRACE):
            return None
        
        loc = self._loc() 
        self.advance() 

        stmts = []
        while (stmt:= self.try_parse_statement()):
            stmts.append(stmt)

        self.consume(TokenType.RBRACE, "Expected '}' after block")
        return Block(stmts, loc) 

    def try_parse_if_statement(self) -> Optional[Statement]:
        if not self.match(TokenType.IF):
            return None
        
        loc = self._loc() 
        self.advance()

        self.consume(TokenType.LPAREN, "Expected '(' after 'if'")

        if (condition:= self.try_parse_expression()) is None:
            raise MissingExpressionError("Expected condition in if statement", self._loc())

        self.consume(TokenType.RPAREN, "Expected ')' after condition")

        then_branch = self.try_parse_block()

        if then_branch is None:
            raise MissingStatementError("Expected block after 'if' condition", self._loc())

        else_branch = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_branch = self.try_parse_block()
            if else_branch is None:
                raise MissingStatementError("Expected block after 'else'", self._loc())
    
        return IfStatement(condition, then_branch, else_branch, loc) 

    def try_parse_while_statement(self) -> Optional[Statement]:
        if not self.match(TokenType.WHILE):
            return None
        
        loc = self._loc() 
        self.advance()

        self.consume(TokenType.LPAREN, "Expected '(' after while")

        if (condition:= self.try_parse_expression()) is None:
            raise MissingExpressionError("Expected condition in while statement", self._loc())
        self.consume(TokenType.RPAREN, "need ')' after condition")
        
        body = self.try_parse_block()

        if body is None:
            raise MissingStatementError("Expected block after 'while' condition", self._loc())

        return WhileStatement(condition, body, loc) 

    def try_parse_return_statement(self) -> Optional[Statement]:
        if not self.match(TokenType.RETURN):
            return None
        
        loc = self._loc() 
        self.advance()

        expr = None
        if not self.match(TokenType.SEMICOLON):
            expr = self.try_parse_expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after return", strategy="CONTINUE")
        return ReturnStatement(expr, loc) 

    def try_parse_function_definition(self) -> Optional[FunctionDefinition]:
        
        if not self.match(TokenType.FUN):
            return None


        loc = self._loc() 
        self.advance() 

        if self.match(TokenType.IDENTIFIER):
            name = self.current_token.value 
            self.advance()
        else:
            raise MissingTokenError("Expected function name after 'fun'", self._loc())
    
        self.consume(TokenType.LPAREN, "Expected '(' after function name")
        params = self._parse_parameter_list()
        self.consume(TokenType.RPAREN, "Expected ')' after parameters")

        if (body := self.try_parse_block()) is None:
             raise MissingStatementError(f"Expected body for function '{name}'", self._loc())
        
        return FunctionDefinition(name, params, body, loc) 

    def _parse_parameter(self) -> str:
        if self.match(TokenType.IDENTIFIER):
                parameter = self.current_token.value
                self.advance()
                return parameter


    def _parse_parameter_list(self) -> list[str]:
        params = []
        seen = set()
        if (parameter := self._parse_parameter()):
            params.append(parameter)
        else:
            return params
        
        while self.match(TokenType.COMMA):
                self.advance()
                if parameter := self._parse_parameter():
                    if parameter in seen:
                        raise DuplicateDefinitionError("Duplicate parameter name '{param}'", self._loc())
                    params.append(parameter)
                    seen.add(parameter)
                else:
                    raise MissingTokenError("Expected parameter name after comma", self._loc())
        return params


   

    def try_parse_logic_or(self) -> Optional[Expression]:
        left = self.try_parse_logic_and()
        if left is None: return None

        while self.match(TokenType.OR):
            loc = self._loc() 
            self.advance()
            right = self.try_parse_logic_and()
            if right is None:
                raise MissingExpressionError("Expected expression after 'or'", loc)
                
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
                raise MissingExpressionError("Expected expression after 'and'", loc)
           
            left = AndExpression(left, right, loc)
        return left

    def try_parse_equality(self) -> Optional[Expression]:

        EQUALITY_OPS = {
        TokenType.EQUAL: EqualExpression,
        TokenType.NOT_EQUAL: NotEqualExpression,
        }
        
        left = self.try_parse_comparison()
        if left is None: return None

        while self.current_token.type in EQUALITY_OPS:
            op_type = self.current_token.type 
            loc = self._loc()
            self.advance()

            right = self.try_parse_comparison()
            if right is None:
                raise MissingExpressionError("Expected expression after equality operator", loc)
            
            constructor = EQUALITY_OPS[op_type]
            left = constructor(left, right, loc)

        return left

    def try_parse_comparison(self) -> Optional[Expression]:
        COMPARISON_OPS = {
        TokenType.LESS: LessExpression,
        TokenType.LESS_EQ: LessEqualExpression,
        TokenType.GREATER: GreaterExpression,
        TokenType.GREATER_EQ: GreaterEqualExpression,
        }

        left = self.try_parse_term()
        if left is None: return None
            
        while self.current_token.type in COMPARISON_OPS:
            op_type = self.current_token.type
            loc = self._loc()
            self.advance()

            right = self.try_parse_term()
            if right is None:
                raise MissingExpressionError("Expected expression after comparison operator", loc)
            
            constructor = COMPARISON_OPS[op_type]
            left = constructor(left, right, loc)
        return left

    def try_parse_term(self) -> Optional[Expression]:
        TERM_OPS = {
        TokenType.PLUS: AddExpression,
        TokenType.MINUS: SubtractExpression,
        }

        left = self.try_parse_factor()
        if left is None: return None

        while self.current_token.type in TERM_OPS:
            op_type = self.current_token.type
            loc = self._loc()
            self.advance()
            right = self.try_parse_factor()
            if right is None:
                raise MissingExpressionError("Expected expression after '+' or '-'", loc)
            
            constructor = TERM_OPS[op_type]
            left = constructor(left, right, loc)
        return left

    def try_parse_factor(self) -> Optional[Expression]:
        FACTOR_OPS = {
        TokenType.MULTIPLY: MultiplyExpression,
        TokenType.DIVIDE: DivideExpression,
        }

        left = self.try_parse_unary()
        if left is None: return None

        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            op_type = self.current_token.type
            loc = self._loc()
            self.advance()

            right = self.try_parse_unary()
            if right is None:
                raise MissingExpressionError("Expected expression after '*' or '/'", loc)
            
            constructor = FACTOR_OPS[op_type]
            left = constructor(left, right, loc)
        return left

    def try_parse_unary(self) -> Optional[Expression]:
        if self.match(TokenType.NOT):
            loc = self._loc()
            self.advance()
            
            operand = self.try_parse_primary()
            if operand is None:
                raise MissingExpressionError("Expected expression after '!'", loc)
            
            return NotExpression(operand, loc)

        if self.match(TokenType.MINUS):
            loc = self._loc()
            self.advance()
            
            operand = self.try_parse_primary()
            if operand is None:
                raise MissingExpressionError("Expected expression after '-'", loc)
            
            return UnaryMinusExpression(operand, loc)

        return self.try_parse_primary()


    def try_parse_primary(self) -> Optional[Expression]:
        if (expr := self.parse_call_or_identifier_expression()):
            return expr
        
        if(expr := self.try_parse_parenthesized_expression()):
            return expr
        
        return self._try_parse_literal()
        
    
    def _try_parse_literal(self) -> Optional[Expression]:
        LITERALS = {
            TokenType.INT_LITERAL:    lambda t, loc: IntLiteral(t.value, loc),
            TokenType.FLOAT_LITERAL:  lambda t, loc: FloatLiteral(t.value, loc),
            TokenType.STRING_LITERAL: lambda t, loc: StringLiteral(t.value, loc),
            TokenType.TRUE:           lambda t, loc: BoolLiteral(True, loc),
            TokenType.FALSE:          lambda t, loc: BoolLiteral(False, loc),
        }

        tt = self.current_token.type

        if tt not in LITERALS:
            return None

        loc = self._loc()
        factory = LITERALS[tt]
        
        token = self.current_token
        self.advance()

        return factory(token, loc)

    def try_parse_assign_or_call_statement(self) -> Optional[Statement]:
        loc = self._loc() 

        if (left := self.parse_call_or_identifier_expression()) is None:
            return None
        
        if self.match(TokenType.ASSIGN):
            self.advance()

            if isinstance(left, FunctionCall):
                    raise InvalidSyntaxError("Cannot assign to a function call", loc)

            if(expr := self.try_parse_expression()) is None:
                raise MissingExpressionError("Expected expression after '='", self._loc())

            self.consume(TokenType.SEMICOLON, "Expected ';' after assignment")
            
            return AssignmentStatement(left.name, expr, loc) 
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after statement")
    
        if isinstance(left, FunctionCall):
            
            return FunctionCallStatement(left.name, left.arguments, loc) 
        
        raise InvalidSyntaxError("Statement has no effect (variable without assignment)", loc)

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
                    raise MissingExpressionError("Expected expression after comma", self._loc())
        return args
    
    def try_parse_match_statement(self) -> Optional[Statement]:
        if not self.match(TokenType.MATCH):
            return None
        
        loc = self._loc()
        self.advance() 

        subjects = self.try_parse_match_header()
        
        self.consume(TokenType.LBRACE, "Expected '{' after match header")

        cases = []
        default_case = None

        while (case_branch := self.try_parse_case_branch()):

            if case_branch.is_default:
                if default_case is not None:
                    raise DuplicateDefinitionError(
                        "Multiple default cases in match statement",
                        case_branch.location
                    )
                default_case = case_branch
            else:
                cases.append(case_branch)

        self.consume(TokenType.RBRACE, "Expected '}' after match cases")

        return MatchStatement(subjects, cases, default_case, loc)

    def try_parse_case_branch(self) -> Optional[MatchCase]:
        if (condition_result := self.try_parse_case_condition()) is None:
            return None

        loc = self._loc()
        condition, is_default = condition_result

        self.consume(TokenType.ARROW, "Expected '=>' after case condition")

        if (body := self.try_parse_block()) is None:
            raise MissingStatementError("Expected block in match case body", self._loc())

        if self.match(TokenType.COMMA):
            self.advance()

        return MatchCase(condition, body, loc, is_default)
    
    def try_parse_match_header(self):
        subjects = []
        aliases_seen = set()

        if self.match(TokenType.LBRACE):
            return subjects  

        first_expr = self.try_parse_expression()
        if not first_expr:
            raise MissingExpressionError("Expected expression or '{' after 'match'", self._loc())

        alias = None
        if self.match(TokenType.AS):
            self.advance()
            if self.match(TokenType.IDENTIFIER):
                alias = self.current_token.value
                if alias in aliases_seen:
                    raise DuplicateDefinitionError(
                f"Duplicate alias '{alias}' in match header",
                self._loc()
            )
                aliases_seen.add(alias)
                self.advance()
            else:
                raise MissingTokenError("Expected identifier after 'as'", self._loc())
        
        subjects.append((first_expr, alias))

        while self.match(TokenType.COMMA):
            self.advance()
            
            expr = self.try_parse_expression()
            if not expr:
                raise MissingExpressionError("Expected expression after comma in match header", self._loc())
            
            alias = None
            if self.match(TokenType.AS):
                self.advance()
                if self.match(TokenType.IDENTIFIER):
                    alias = self.current_token.value
                    if alias in aliases_seen:
                        raise DuplicateDefinitionError(f"Duplicate alias '{alias}' in match header",self._loc())
                    aliases_seen.add(alias)
                    self.advance()
                else:
                    raise MissingTokenError("Expected identifier after 'as'", self._loc())
            
            subjects.append((expr, alias))
            
        return subjects

    def try_parse_case_condition(self):
       
        if (pattern := self.try_parse_positional_pattern()):
            return pattern, False
       
        if (expr := self.try_parse_expression()):
            return expr, False
       
        if self.match(TokenType.DEFAULT):
            self.advance()
            return None, True 
        
        return None
      
        
    def try_parse_positional_pattern(self):
        if not self.match(TokenType.LBRACKET):
            return None
        
        loc = self._loc()
        self.advance() 

        patterns = []
        
        if not self.match(TokenType.RBRACKET):
            patterns = self.try_parse_pattern_list()

        self.consume(TokenType.RBRACKET, "Expected ']' after pattern list")
        
        return PositionalPattern(patterns, loc)
    
    def try_parse_pattern_list(self):
        patterns = []
        
        if first := self.try_parse_and_pattern():
            patterns.append(first)
        else:
            raise InvalidSyntaxError("Expected pattern in pattern list", self._loc())
        
        while self.match(TokenType.COMMA):
            self.advance()
            if nxt:= self.try_parse_and_pattern():
                patterns.append(nxt)
            else:
                raise InvalidSyntaxError("Expected pattern after comma", self._loc())
        
        return patterns
    
    def try_parse_and_pattern(self):
        left = self.try_parse_single_pattern()
        if not left:
            return None
   
        while self.match(TokenType.AND_PATTERN): 
            loc = self._loc()
            self.advance()
            right = self.try_parse_single_pattern()
            if not right:
                raise InvalidSyntaxError("Expected pattern after 'AND'", loc)
            
            left = AndPattern(left, right, loc)
            
        return left
   
    def try_parse_single_pattern(self) -> Optional[Pattern]:
        # Wildcard (_)
        if (pat := self.try_parse_wildcard_pattern()):
            return pat

        # Type Pattern (is int)
        if (pat := self.try_parse_type_pattern()):
            return pat

        # Relational Pattern (> 5)
        if (pat := self.try_parse_relational_pattern()):
            return pat

        # Constant Pattern (10, "hello")
        if (pat := self.try_parse_constant_pattern()):
            return pat
            
        return None
    
    
    def try_parse_wildcard_pattern(self):
        if not self.match(TokenType.WILDCARD):
            return None
            
        loc = self._loc()
        self.advance()
        return WildcardPattern(loc)

    def try_parse_type_pattern(self) -> Optional[TypePattern]:

        if not self.match(TokenType.IS):
            return None
        
        loc = self._loc()
        self.advance() 

        TYPE_NAMES = {
        TokenType.TYPE_INT: "int",
        TokenType.TYPE_FLT: "float",
        TokenType.TYPE_STR: "string",
        TokenType.TYPE_BOOL: "bool",
        }
    
        
        if self.current_token.type not in TYPE_NAMES:
            raise InvalidSyntaxError("Expected type name after 'is'", self._loc())

        type_name = TYPE_NAMES[self.current_token.type]
        self.advance()
        
        return TypePattern(type_name, loc)

    def try_parse_relational_pattern(self)-> Optional[RelationalPattern]:
        OP_MAP = {
            TokenType.GREATER: ">",
            TokenType.LESS: "<",
            TokenType.GREATER_EQ: ">=",
            TokenType.LESS_EQ: "<=",
            TokenType.EQUAL: "==",
            TokenType.NOT_EQUAL: "!="
        }

        if self.current_token.type not in OP_MAP:
            return None

        loc = self._loc()
        op_str = OP_MAP[self.current_token.type] 
        
        self.advance() 

        if (expr := self.try_parse_expression()) is None:
            raise MissingExpressionError("Expected expression in relational pattern", loc)
            
        return RelationalPattern(op_str, expr, loc)

    def try_parse_constant_pattern(self):
    
        literal = self._try_parse_literal()
        if literal is None:
            return None

        return ConstantPattern(literal, literal.location)
    
   