from dataclasses import dataclass
from typing import List, Optional, Any

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

#wyrażenia
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
class Literal(Expression):
    value: Any        
    type_name: str
    location: SourceLocation

@dataclass
class Variable(Expression):
    name: str
    location: SourceLocation

#statementy

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
class FunctionDefinition(Statement):
    name: str
    params: List[str]     
    body: Block          
    location: SourceLocation


@dataclass
class Program(ASTNode):
    functions: List[FunctionDefinition]
    location: SourceLocation