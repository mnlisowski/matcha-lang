from dataclasses import dataclass
from typing import List, Optional, Any
from src.token import Token 

class ASTNode:
    pass

class Statement(ASTNode):
    pass


@dataclass
class Program(ASTNode):
    statements: list[Statement]
    

class Expression(ASTNode):
    pass

# statementy
@dataclass
class Block(Statement):
    statements: List[Statement]


@dataclass
class AssignmentStatement(Statement):
    target_name: str
    expression: Expression

@dataclass
class ReturnStatement(Statement):

    expression: Optional[Expression]

@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: Statement
    else_branch: Optional[Statement] = None

@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: Statement

@dataclass
class FunctionDefinition(Statement):
    name: str
    params: List[str]
    body: Statement

@dataclass
class FunctionCallStatement(Statement):
    name: str
    arguments: List[Expression]

@dataclass
class MatchStatement(Statement):
    pass


# wyrażenia

@dataclass
class BinaryExpression(Expression):
    left: Expression
    operator: Token
    right: Expression

@dataclass
class UnaryExpression(Expression):
    operator: Token
    operand: Expression

@dataclass
class Literal(Expression):
    value: Any
    type_name: str  

@dataclass
class Variable(Expression):
    name: str

@dataclass
class FunctionCall(Expression):
    name: str
    arguments: List[Expression]


# class MatchCaseCondition(ASTNode):
#     pass

# @dataclass
# class DefaultMatchCondition(MatchCaseCondition):
#     pass

# @dataclass
# class ExprMatchCondition(MatchCaseCondition):
#     pass

# @dataclass
# class PatternMatchCondition(MatchCaseCondition):
#     pass

# @dataclass
# class CaseBranch(ASTNode):
#     pass

