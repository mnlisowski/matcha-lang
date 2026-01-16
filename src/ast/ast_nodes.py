from dataclasses import dataclass
from typing import List, Optional, Any, Union, Tuple


@dataclass
class SourceLocation:
    line: int
    column: int

    def __repr__(self):
        return f"(L:{self.line}, C:{self.column})"


class ASTNode:
    def accept(self, visitor):
        raise NotImplementedError()


class Statement(ASTNode):
    pass


class Expression(ASTNode):
    pass


# WYRAŻENIA


@dataclass
class IntLiteral(Expression):
    value: int
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_IntLiteral(self)


@dataclass
class FloatLiteral(Expression):
    value: float
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_FloatLiteral(self)


@dataclass
class StringLiteral(Expression):
    value: str
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_StringLiteral(self)


@dataclass
class BoolLiteral(Expression):
    value: bool
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_BoolLiteral(self)


@dataclass
class Variable(Expression):
    name: str
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_Variable(self)


@dataclass
class FunctionCall(Expression):
    name: str
    arguments: List[Expression]
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_FunctionCall(self)


@dataclass
class AddExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_AddExpression(self)


@dataclass
class SubtractExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_SubtractExpression(self)


@dataclass
class MultiplyExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_MultiplyExpression(self)


@dataclass
class DivideExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_DivideExpression(self)


@dataclass
class OrExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_OrExpression(self)


@dataclass
class AndExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_AndExpression(self)


@dataclass
class EqualExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_EqualExpression(self)


@dataclass
class NotEqualExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_NotEqualExpression(self)


@dataclass
class LessExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_LessExpression(self)


@dataclass
class LessEqualExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_LessEqualExpression(self)


@dataclass
class GreaterExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_GreaterExpression(self)


@dataclass
class GreaterEqualExpression(Expression):
    left: Expression
    right: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_GreaterEqualExpression(self)


@dataclass
class UnaryMinusExpression(Expression):
    operand: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_UnaryMinusExpression(self)


@dataclass
class NotExpression(Expression):
    operand: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_NotExpression(self)


# INSTRUKCJE


@dataclass
class Block(Statement):
    statements: List[Statement]
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_Block(self)


@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: Statement
    else_branch: Optional[Statement]
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_IfStatement(self)


@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: Statement
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_WhileStatement(self)


@dataclass
class ReturnStatement(Statement):
    expression: Optional[Expression]
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_ReturnStatement(self)


@dataclass
class BreakStatement(Statement):
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_BreakStatement(self)


@dataclass
class ContinueStatement(Statement):
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_ContinueStatement(self)


@dataclass
class AssignmentStatement(Statement):
    variable_name: str
    expression: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_AssignmentStatement(self)


@dataclass
class FunctionCallStatement(Statement):
    name: str
    arguments: List[Expression]
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_FunctionCallStatement(self)


class Pattern(ASTNode):
    pass


@dataclass
class WildcardPattern(Pattern):
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_WildcardPattern(self)


@dataclass
class ConstantPattern(Pattern):
    value: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_ConstantPattern(self)


@dataclass
class TypePattern(Pattern):
    type_name: str
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_TypePattern(self)


@dataclass
class RelationalPattern(Pattern):
    op: str
    expression: Expression
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_RelationalPattern(self)


@dataclass
class AndPattern(Pattern):
    left: Pattern
    right: Pattern
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_AndPattern(self)


@dataclass
class PositionalPattern(Pattern):
    patterns: List[Pattern]
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_PositionalPattern(self)


@dataclass
class MatchCase(ASTNode):
    condition: Union[Pattern, Expression, None]
    body: Statement
    location: SourceLocation
    is_default: bool = False

    def accept(self, visitor):
        visitor.visit_MatchCase(self)


@dataclass
class MatchStatement(Statement):
    subjects: List[Tuple[Expression, Optional[str]]]
    cases: List[MatchCase]
    default_case: Optional[MatchCase]
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_MatchStatement(self)


@dataclass
class FunctionDefinition(Statement):
    name: str
    params: List[str]
    body: Block
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_FunctionDefinition(self)


@dataclass
class Program(ASTNode):
    functions: List[FunctionDefinition]
    location: SourceLocation

    def accept(self, visitor):
        visitor.visit_Program(self)


@dataclass
class BuiltinFunction(Statement):
    name: str
    call: Any

    def accept(self, visitor):
        visitor.visit_BuiltinFunction(self)
