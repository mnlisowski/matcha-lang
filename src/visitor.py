from abc import ABC, abstractmethod

class Visitor(ABC):

    @abstractmethod
    def visit_Program(self, node): pass
    @abstractmethod
    def visit_FunctionDefinition(self, node): pass
    @abstractmethod
    def visit_Block(self, node): pass
    
    @abstractmethod
    def visit_IfStatement(self, node): pass
    @abstractmethod
    def visit_WhileStatement(self, node): pass
    @abstractmethod
    def visit_ReturnStatement(self, node): pass
    @abstractmethod
    def visit_BreakStatement(self, node): pass
    @abstractmethod
    def visit_AssignmentStatement(self, node): pass
    @abstractmethod
    def visit_FunctionCallStatement(self, node): pass
    @abstractmethod
    def visit_MatchStatement(self, node): pass
    @abstractmethod
    def visit_MatchCase(self, node): pass
    
    @abstractmethod
    def visit_Literal(self, node): pass
    @abstractmethod
    def visit_Variable(self, node): pass
    @abstractmethod
    def visit_FunctionCall(self, node): pass
    @abstractmethod
    def visit_AddExpression(self, node): pass
    @abstractmethod
    def visit_SubtractExpression(self, node): pass
    @abstractmethod
    def visit_MultiplyExpression(self, node): pass
    @abstractmethod
    def visit_DivideExpression(self, node): pass
    @abstractmethod
    def visit_OrExpression(self, node): pass
    @abstractmethod
    def visit_AndExpression(self, node): pass
    @abstractmethod
    def visit_EqualExpression(self, node): pass
    @abstractmethod
    def visit_NotEqualExpression(self, node): pass
    @abstractmethod
    def visit_LessExpression(self, node): pass
    @abstractmethod
    def visit_LessEqualExpression(self, node): pass
    @abstractmethod
    def visit_GreaterExpression(self, node): pass
    @abstractmethod
    def visit_GreaterEqualExpression(self, node): pass
    @abstractmethod
    def visit_UnaryMinusExpression(self, node): pass
    @abstractmethod
    def visit_NotExpression(self, node): pass
    
    @abstractmethod
    def visit_WildcardPattern(self, node): pass
    @abstractmethod
    def visit_ConstantPattern(self, node): pass
    @abstractmethod
    def visit_TypePattern(self, node): pass
    @abstractmethod
    def visit_RelationalPattern(self, node): pass
    @abstractmethod
    def visit_AndPattern(self, node): pass
    @abstractmethod
    def visit_PositionalPattern(self, node): pass