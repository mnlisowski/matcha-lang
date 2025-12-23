from dataclasses import dataclass
from typing import List, Optional, Any, Union, Tuple

@dataclass
class SourceLocation:
    line: int
    column: int
    
    def __repr__(self):
        return f"(L:{self.line}, C:{self.column})"

class ASTNode:
    pass

class Statement(ASTNode):
    pass

class Expression(ASTNode):
    pass


@dataclass
class Literal(Expression):
    value: Any        
    type_name: str 
    location: SourceLocation

@dataclass
class Variable(Expression):
    name: str
    location: SourceLocation

@dataclass
class FunctionCall(Expression):
    name: str
    arguments: List[Expression]
    location: SourceLocation


@dataclass
class AddExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

@dataclass
class SubtractExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

@dataclass
class MultiplyExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

@dataclass
class DivideExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

@dataclass
class OrExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

@dataclass
class AndExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

@dataclass
class EqualExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

@dataclass
class NotEqualExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

@dataclass
class LessExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

@dataclass
class LessEqualExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

@dataclass
class GreaterExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

@dataclass
class GreaterEqualExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

@dataclass
class UnaryMinusExpression(Expression):
    operand: Expression
    location: SourceLocation

@dataclass
class NotExpression(Expression):
    operand: Expression
    location: SourceLocation


@dataclass
class Block(Statement):
    statements: List[Statement]
    location: SourceLocation

@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: Statement
    else_branch: Optional[Statement]
    location: SourceLocation

@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: Statement
    location: SourceLocation

@dataclass
class ReturnStatement(Statement):
    expression: Optional[Expression]
    location: SourceLocation

@dataclass
class AssignmentStatement(Statement):
    variable_name: str
    expression: Expression
    location: SourceLocation

@dataclass
class FunctionCallStatement(Statement):
    name: str
    arguments: List[Expression]
    location: SourceLocation

@dataclass
class FunctionDefinition(Statement):
    name: str
    params: List[str]     
    body: Block          
    location: SourceLocation



@dataclass
class Program(ASTNode):
    functions: List[FunctionDefinition]
    location: SourceLocation