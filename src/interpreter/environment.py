from typing import Any, Optional, Dict
from src.ast.ast_nodes import SourceLocation


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


class LimitError(RuntimeError):
    pass


class Scope:
    def __init__(self):
        self.variables: Dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self.variables[name] = value

    def has(self, name):
        return name in self.variables

    def get(self, name: str) -> Any:
        return self.variables[name]

    def set(self, name, value: Any):
        self.variables[name] = value


class MatchScope(Scope):
    def __init__(self, subjects_with_aliases):
        super().__init__()
        self.match_targets = []
        for value, alias in subjects_with_aliases:
            self.match_targets.append(value)
            if alias:
                self.define(alias, value)
        self.current_index = 0

    def set_index(self, index: int):
        self.current_index = index

    def get_match_targets(self):
        return self.match_targets

    def get_match_target(self):
        return self.match_targets[self.current_index]


class CallContext:
    def __init__(self, args, name, call_location):
        self.scopes = [Scope()]  # jakos zaiinicjowac
        self.args = args
        self.name = name
        self.call_location = call_location
        self.loop_depth = 0
        self._break_flag = False
        self._continue_flag = False
        self._return_flag = False
        self._return_value = None

    def push_scope(self):
        self.scopes.append(Scope())

    def pop_scope(self) -> None:
        if len(self.scopes) > 1:
            self.scopes.pop()

    def push_match_scope(self, subjects_with_aliases):
        self.scopes.append(MatchScope(subjects_with_aliases))

    def define(self, name, value):
        self.scopes[-1].define(name, value)

    def get(self, name):
        for scope in reversed(self.scopes):
            if scope.has(name):
                return scope.get(name)
        raise NameError(f"{name} is not defined")

    def assign(self, name, value) -> bool:
        for scope in reversed(self.scopes):
            if scope.has(name):
                scope.set(name, value)
                return True
        return False

    def define_or_assign(self, name, value) -> None:
        if not self.assign(name, value):
            self.define(name, value)

    # petle

    def enter_loop(self):
        self.loop_depth += 1

    def exit_loop(self):
        self.loop_depth -= 1
        self._break_flag = False
        self._continue_flag = False

    def is_in_loop(self):
        return self.loop_depth > 0

    # flagi

    def on_break(self):
        self._break_flag = True

    def on_continue(self):
        self._continue_flag = True

    def on_return(self, value):
        self._return_flag = True
        self._return_value = value

    def should_break(self):
        return self._break_flag

    def should_continue(self):
        return self._continue_flag

    def should_return(self):
        return self._return_flag

    def should_interrupt(self):
        return self._break_flag or self._continue_flag or self._return_flag

    def get_return_value(self):
        return self._return_value

    # match

    def set_subject_index(self, index):
        for scope in reversed(self.scopes):
            if isinstance(scope, MatchScope):
                scope.set_index(index)
                return
        raise RuntimeError("Not in match context")

    def get_match_targets(self):
        for scope in reversed(self.scopes):
            if isinstance(scope, MatchScope):
                return scope.get_match_targets()
        raise RuntimeError("Not in match context")

    def get_current_target(self):
        for scope in reversed(self.scopes):
            if isinstance(scope, MatchScope):
                return scope.get_match_target()
        raise RuntimeError("Not in match context")

    def is_in_match(self):
        for scope in self.scopes:
            if isinstance(scope, MatchScope):
                return True
        return False


class Environment:
    max_depth = 1000

    def __init__(self):
        self._call_contexts = []
        self._functions = {}

    def current_context(self):
        if not self._call_contexts:
            raise RuntimeError("No active call context")
        return self._call_contexts[-1]

    def enter_function(self, args=None, name=None, call_location=None):
        if len(self._call_contexts) > self.max_depth:
            raise LimitError(f"Maximum recursion depth exceeded ({self.max_depth})")

        current_context = CallContext(args, name, call_location)

        self._call_contexts.append(current_context)

    def exit_function(self):
        if self._call_contexts:
            self._call_contexts.pop()

    # bloki
    def enter_block(self):
        self.current_context().push_scope()

    def exit_block(self):
        self.current_context().pop_scope()

    # petle
    def enter_loop(self):
        self.current_context().enter_loop()

    def exit_loop(self):
        self.current_context().exit_loop()

    def is_in_loop(self):
        return self.current_context().is_in_loop()

    # match

    def enter_match(self, subjects_with_aliases):
        self.current_context().push_match_scope(subjects_with_aliases)

    def exit_match(self):
        self.current_context().pop_scope()

    def set_subject_index(self, index):
        self.current_context().set_subject_index(index)

    def get_match_targets(self):
        return self.current_context().get_match_targets()

    def get_current_target(self):
        return self.current_context().get_current_target()

    def is_in_match(self):
        return self.current_context().is_in_match()

    # flagi

    def on_break(self):
        self.current_context().on_break()

    def on_continue(self):
        self.current_context().on_continue()

    def on_return(self, value=None):
        self.current_context().on_return(value)

    def should_break(self):
        return self.current_context().should_break()

    def should_continue(self):
        return self.current_context().should_continue()

    def should_return(self):
        return self.current_context().should_return()

    def should_interrupt(self):
        return self.current_context().should_interrupt()

    def get_return_value(self):
        return self.current_context().get_return_value()

    # zmienne

    def define(self, name, value):
        self.current_context().define(name, value)

    def get(self, name):
        return self.current_context().get(name)

    def assign(self, name, value):
        return self.current_context().assign(name, value)

    def define_or_assign(self, name, value):
        self.current_context().define_or_assign(name, value)

    # funkcje globalne

    def define_function(self, name, func):
        self._functions[name] = func

    def get_function(self, name):
        return self._functions.get(name)

    def has_function(self, name):
        return name in self._functions

    def get_args(self):
        return self.current_context().args

    # info

    def get_function_info(self):
        ctx = self.current_context()
        return {"name": ctx.name, "args": ctx.args, "location": ctx.call_location}

    def depth(self):
        return len(self._call_contexts)
