from typing import Optional, Any
from src.visitor import Visitor
from src.ast_nodes import *
from .environment import Environment

class BreakException(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value: Any):
        self.value = value
        

class RuntimeError(Exception):
    def __init__(self, message: str, location: Optional[SourceLocation]):
        self.message = message
        self.location = location
        if location:
            super().__init__(
                f"Runtime Error - line {location.line}, col {location.column}: {message}"
            )
        else:
            super().__init__(f"Runtime error: {message}")

class TypeError(RuntimeError):
    """niezgodnosc typów"""
    pass


class NameError(RuntimeError):
    """niezdefiniowane nazwy"""
    pass


class ValueError(RuntimeError):
    pass


class ArgumentError(RuntimeError):
    """liczba/typ argumentów"""
    pass

# Interpreter

class Interpreter(Visitor):

    def __init__(self):
        self.globals = Environment() #przydatne przy wywołaniach funkcji gdzie nie chcemy przesłaniać zmiennych
        self.builtins = {}
        self.build_builtins()

        self.environment = self.globals
        self.current_subject = None

    def build_builtins(self):
        self.builtins["print"] = self._builtin_print
        self.builtins["println"] = self._builtin_println
        self.builtins["input"] = self._builtin_input
        self.builtins["typeof"] = self._builtin_typeof

    def _builtin_print(self, *args):
        print(*args, end='')
        return None
    
    def _builtin_println(self, *args):
        print(*args)
        return None
    
    def _builtin_input(self):
        return input()
    
    def _builtin_typeof(self, value):
        if isinstance(value, bool): #isinstance(True,int) zwraca true, wiec przed
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        else:
            return "unknown"
    
    def interpret(self, node: ASTNode):

        try:
            return node.accept(self)
        except (RuntimeError, BreakException, ReturnException) as e:
            if isinstance(e, BreakException):
                raise RuntimeError("Break should not escape the scope", None)
            elif isinstance(e, ReturnException):
                raise RuntimeError("Return should not escape the scope", None)
            else:
                raise 

    def visit_Program(self, node: Program):
        for func_def in node.functions:
            func_def.accept(self)
        return None
    
    def visit_FunctionDefinition(self, node: FunctionDefinition):
        self.globals.define(node.name, node)

    def visit_FunctionCall(self, node: FunctionCall):
        # sprawdzam builtiny
        if node.name in self.builtins:
            args = []
            for arg in node.arguments:
                args.append(arg.accept(self))
            return self.builtins[node.name](*args)
        #pobieram funkcje z globals
        try:
            function_def = self.globals.get(node.name)
        except Exception: #konflikt nazw, runtimeerror nie bylo przesloniete w environment
            raise NameError(f"Undefined function '{node.name}'", node.location)
        
        # sprawdzam czy nie jest zmienną
        if not isinstance(function_def, FunctionDefinition):
            raise TypeError(
                f"'{node.name}' is not a function",
                node.location
            )
        # l. argumentów
        if len(node.arguments) != len(function_def.params):
            raise ArgumentError(
                f"Function '{node.name}' expects {len(function_def.params)} "
                f"arguments, got {len(node.arguments)}",
                node.location
            )
        # bierzemy wartosci argumentow z aktualnego scopu
        args = []
        for arg in node.arguments:
            args.append(arg.accept(self))

        # nowy scope. parentem jest globals a nie self.parent, bo nie chcemy przeslaniac zmiennych przy wywolywaniu funkcji
        func_env = Environment(parent=self.globals)

        # zmienne lokalne na podstawie argumentow funkcji
        for arg_name, arg_value in zip(function_def.params,args):
            func_env.define(arg_name, arg_value)

        # wykonuje funkcje w nowym environment
        old_env = self.environment
        self.environment = func_env

        try:
            function_def.body.accept(self)
            # Jeśli nie było wyjatku return, zwróć None
            return None
        except ReturnException as e:
            return e.value
        finally:
            # zawsze przywracam stare srodowisko
            self.environment = old_env
        
    def visit_FunctionCallStatement(self, node: FunctionCallStatement):
        # nie obchodzi mnie co zwraca
        call_node = FunctionCall(node.name, node.arguments, node.location)
        self.visit_FunctionCall(call_node)
        return None
    
    def visit_ReturnStatement(self, node: ReturnStatement):
        value = None
        if node.expression:
            value = node.expression.accept(self)
        raise ReturnException(value)


    def visit_Literal(self, node: Literal):
        return node.value
    
    def visit_Variable(self, node: Variable):
        try:
            return self.environment.get(node.name)
        except Exception: #tak samo jak visitcall, w environment runtimeerror nie jest przesloniety
            raise NameError(f"Undefined variable '{node.name}", node.location)

    def visit_AssignmentStatement(self, node:AssignmentStatement):
        value = node.expression.accept(self)
        # wpierw aktualizujemy istniejaca, jak nie ma to nowa w scope

        if not self.environment.assign(node.variable_name, value):
            self.environment.define(node.variable_name, value)

        return None
    
    def visit_AddExpression(self, node: AddExpression):
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        if type(left) != type(right):
            raise TypeError(
                f"Cannot perform '+' on {type(left).__name__} and {type(right).__name__}. "
                f"Types must match exactly",
                node.location
            )
        
         # konkatenacja
        if isinstance(left, str):
            return left + right
        
        if isinstance(left, (int, float)):
            return left + right
        
        # Wszystkie inne 
        raise TypeError(
            f"Operator '+' not supported for type {type(left).__name__}",
            node.location
        )
    
    def visit_SubtractExpression(self, node: SubtractExpression):
        
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        if type(left) != type(right):
            raise TypeError(
                f"Cannot perform '-' on {type(left).__name__} and {type(right).__name__}. "
                f"Requires same types",
                node.location
            )
        
        if isinstance(left, (int, float)):
            return left - right
        
        raise TypeError(
            f"Operator '-' not supported for type {type(left).__name__}",
            node.location
        )
    
    def visit_MultiplyExpression(self, node: MultiplyExpression):
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        if type(left) != type(right):
            raise TypeError(
                f"Cannot perform '*' on {type(left).__name__} and {type(right).__name__}. "
                f"Types must match exactly",
                node.location
            )
        
        if isinstance(left, (int, float)):
            return left * right
        
        raise TypeError(
            f"Operator '*' requires numeric types, got {type(left).__name__}",
            node.location
        )
    
    
    def visit_DivideExpression(self, node: DivideExpression):
        
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        if type(left) != type(right):
            raise TypeError(
                f"Cannot perform '/' on {type(left).__name__} and {type(right).__name__}. "
                f"Types must match exactly",
                node.location
            )
        
        if not isinstance(left, (int, float)):
            raise TypeError(
                f"Operator '/' requires numeric types, got {type(left).__name__}",
                node.location
            )
        
        # przez zero
        if right == 0:
            raise ValueError(
                "Division by zero",
                node.location
            )
        
        return left / right
    
    def visit_UnaryMinusExpression(self, node: UnaryMinusExpression):
        value = node.operand.accept(self)
        
        if not isinstance(value, (int, float)):
            raise TypeError(
                f"Unary '-' requires numeric type, got {type(value).__name__}",
                node.location
            )
        
        return -value
    
    def visit_EqualExpression(self, node: EqualExpression):
        
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        if type(left) != type(right):
            raise TypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__} with '=='. "
                f"Need same types",
                node.location
            )
        
        return left == right
    
    def visit_NotEqualExpression(self, node: NotEqualExpression):
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        if type(left) != type(right):
            raise TypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__} with '!='. "
                f"Need same types",
                node.location
            )
        
        return left != right
    
    def visit_LessExpression(self, node: LessExpression):
        """Operator '<' - mniejsze (tylko liczby)."""
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        if type(left) != type(right):
            raise TypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__} with '<'. "
                f"Need same types",
                node.location
            )
        
        if not isinstance(left, (int, float)):
            raise TypeError(
                f"Operator '<' requires numeric types, got {type(left).__name__}",
                node.location
            )
        
        return left < right
    
    def visit_LessEqualExpression(self, node: LessEqualExpression):
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        if type(left) != type(right):
            raise TypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__} with '<='. "
                f"Need same types",
                node.location
            )
        
        if not isinstance(left, (int, float)):
            raise TypeError(
                f"Operator '<=' requires numeric types, got {type(left).__name__}",
                node.location
            )
        
        return left <= right
    
    def visit_GreaterExpression(self, node: GreaterExpression):
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        if type(left) != type(right):
            raise TypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__} with '>'. "
                f"Need same types",
                node.location
            )
        
        if not isinstance(left, (int, float)):
            raise TypeError(
                f"Operator '>' requires numeric types, got {type(left).__name__}",
                node.location
            )
        
        return left > right
    
    def visit_GreaterEqualExpression(self, node: GreaterEqualExpression):
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        if type(left) != type(right):
            raise TypeError(
                f"Cannot compare {type(left).__name__} and {type(right).__name__} with '>='. "
                f"Need same types",
                node.location
            )
        
        if not isinstance(left, (int, float)):
            raise TypeError(
                f"Operator '>=' requires numeric types, got {type(left).__name__}",
                node.location
            )
        
        return left >= right
    
    # operatory logiczne

    def visit_AndExpression(self, node: AndExpression):

        left= node.left.accept(self)

        if not isinstance(left, bool):
            raise TypeError(f"Operator 'AND' requires bool, got {type(left).__name__} on left side", node.location)
        
        if not left:
            return False
        
        right = node.right.accept(self)

        if not isinstance(right, bool):
            raise TypeError(
                f"Operator 'AND' requires bool, got {type(right).__name__} on right side",
                node.location
            )
        
        return right
    
    def visit_OrExpression(self, node: OrExpression):

        left = node.left.accept(self)

        if not isinstance(left, bool):
             raise TypeError(
             f"Operator 'OR' requires bool, got {type(left).__name__} on left side", node.location)
        
        if left:
            return True
        
        right = node.right.accept(self)
        
        if not isinstance(right, bool):
            raise TypeError(
                f"Operator '||' requires bool, got {type(right).__name__} on right side",
                node.location
            )
        
        return right
        
    def visit_NotExpression(self, node: NotExpression):
        value = node.operand.accept(self)
        
        if not isinstance(value, bool):
            raise TypeError(
                f"Operator '!' requires bool, got {type(value).__name__}",
                node.location
            )
        
        return not value
    
    def visit_Block(self, node: Block):
        old_env = self.environment
        self.environment = Environment(parent=old_env)

        # dajemy traja zeby przywrócić stary scope w wypadku wyjatku
        try:
            for statement in node.statements:
                statement.accept(self)
        finally:
            self.environment = old_env

        return None
    
    def visit_IfStatement(self, node: IfStatement):
        
        condition = node.condition.accept(self)

        if not isinstance(condition, bool):
            raise TypeError(
                 f"If condition must be bool, got {type(condition).__name__}",
                node.location
            )
        
        if condition:
            node.then_branch.accept(self)
        elif node.else_branch:
            node.else_branch.accept(self)

        return None
    
    def visit_WhileStatement(self, node: WhileStatement):

        while True:
            condition = node.condition.accept(self)

            if not isinstance(condition, bool):
                raise TypeError(
                    f"While condition must be bool, got {type(condition).__name__}",
                    node.location
                )

            if not condition:
                break
            try:
                node.body.accept(self)
            except BreakException:
                break

        return None
    
    def visit_BreakStatement(self, node: BreakStatement):
        raise BreakException()
    
    def visit_MatchStatement(self, node: MatchStatement):
        previous_env = self.environment
        
        # 1. Tworzymy scope dla aliasów
        match_env = Environment(parent=previous_env)
        
        values = []
        for expr, alias in node.subjects:
            val = expr.accept(self)
            values.append(val)
            if alias:
                match_env.define(alias, val)
        
        
        
        # Zapisujemy scope (bo zagniezdzenia matchy)
        match_env.define("$match_targets", values)

        self.environment = match_env
        
        try:
            matched_any = False
            default_case = None
            
            # iteruje po kejsach bez default
            for case in node.cases:
                if case.is_default:
                    default_case = case
                    continue 
                
                # Sprawdzam dopasowanie
                is_match = case.accept(self)
                
                if is_match:
                    matched_any = True
                    case.body.accept(self)

            
            if not matched_any and default_case:
                default_case.body.accept(self)
            
        finally:
            self.environment = previous_env

        return None

    def visit_MatchCase(self, node: MatchCase):
        if node.is_default:
            return True 
                        
        if node.condition is None:
             return True
        
        if isinstance(node.condition, Pattern):
            return node.condition.accept(self)
        
        elif isinstance(node.condition, Expression):
            result = node.condition.accept(self)
            if not isinstance(result, bool):
                 raise TypeError(f"Match condition must be bool, got {type(result).__name__}", node.location)
            return result
            
        return False

  
    def visit_PositionalPattern(self, node: PositionalPattern):

        match_values = self.environment.get("$match_targets")
        
        if len(node.patterns) != len(match_values):
            raise RuntimeError(
                f"Pattern count not matching. Expected {len(self.match_values)}, "
                f"got {len(node.patterns)}",
                node.location
            )
        
        for pattern, value in zip(node.patterns, match_values):
            
            self.environment.define("$current_subject", value)
            # Jeśli którykolwiek wzorzec nie pasuje, to calosc nie pasuje
            if not pattern.accept(self):
                return False
                
        return True

    def visit_RelationalPattern(self, node: RelationalPattern):
        val = self.environment.get("$current_subject")
        
        comp_val = node.expression.accept(self) 
        if type(val) != type(comp_val):
           #albo false albo rzucamy wyjatek
             return False 

        if node.op == ">": return val > comp_val
        if node.op == "<": return val < comp_val
        if node.op == ">=": return val >= comp_val
        if node.op == "<=": return val <= comp_val
        if node.op == "==": return val == comp_val
        if node.op == "!=": return val != comp_val
        
        return False

    def visit_TypePattern(self, node: TypePattern):
        val = self.environment.get("$current_subject")
        t = node.type_name
        
    
        t = str(t)

        if t == "int": 
            return isinstance(val, int) and not isinstance(val, bool)
        if t == "float": 
            return isinstance(val, float)
        if t == "string": 
            return isinstance(val, str)
        if t == "bool": 
            return isinstance(val, bool)
            
        return False

    def visit_ConstantPattern(self, node: ConstantPattern):
        val = self.environment.get("$current_subject")
        pattern_val = node.value.accept(self)
        return val == pattern_val

    def visit_WildcardPattern(self, node: WildcardPattern):
        return True

    def visit_AndPattern(self, node: AndPattern):
        return node.left.accept(self) and node.right.accept(self)