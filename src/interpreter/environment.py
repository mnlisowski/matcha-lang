from typing import Any, Optional, Dict, List
from src.ast.ast_nodes import SourceLocation


class RuntimeError(Exception):
    def __init__(self, message: str, location: Optional[SourceLocation]) -> None:
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
    def __init__(self) -> None:
        self.variables: Dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self.variables[name] = value

    def has(self, name: str) -> bool:
        return name in self.variables

    def get(self, name: str) -> Any:
        return self.variables[name]

    def set(self, name: str, value: Any) -> None:
        self.variables[name] = value


class MatchScope(Scope):
    def __init__(self, subjects_with_aliases: List[Any]) -> None:
        super().__init__()
        self.match_targets: List[Any] = []
        for value, alias in subjects_with_aliases:
            self.match_targets.append(value)
            if alias:
                self.define(alias, value)
        self.current_index = 0

    def set_index(self, index: int) -> None:
        self.current_index = index

    def get_match_targets(self) -> List[Any]:
        return self.match_targets

    def get_match_target(self) -> Any:
        return self.match_targets[self.current_index]


class CallContext:
    def __init__(
        self, args: List[Any], name: str, call_location: Optional[SourceLocation]
    ) -> None:
        self.scopes: List[Scope] = [Scope()]  # jakos zaiinicjowac
        self.args = args
        self.name = name
        self.call_location = call_location
        self.loop_depth = 0
        self._break_flag = False
        self._continue_flag = False
        self._return_flag = False
        self._return_value: Any = None

    def push_scope(self) -> None:
        self.scopes.append(Scope())

    def pop_scope(self) -> None:
        if len(self.scopes) > 1:
            self.scopes.pop()

    def push_match_scope(self, subjects_with_aliases: List[Any]) -> None:
        self.scopes.append(MatchScope(subjects_with_aliases))

    def define(self, name: str, value: Any) -> None:
        self.scopes[-1].define(name, value)

    def get(self, name: str) -> Any:
        for scope in reversed(self.scopes):
            if scope.has(name):
                return scope.get(name)
        raise NameError(f"{name} is not defined", None)

    def assign(self, name: str, value: Any) -> bool:
        for scope in reversed(self.scopes):
            if scope.has(name):
                scope.set(name, value)
                return True
        return False

    def define_or_assign(self, name: str, value: Any) -> None:
        if not self.assign(name, value):
            self.define(name, value)

    # petle

    def enter_loop(self) -> None:
        self.loop_depth += 1

    def exit_loop(self) -> None:
        self.loop_depth -= 1
        self._break_flag = False
        self._continue_flag = False

    def is_in_loop(self) -> bool:
        return self.loop_depth > 0

    # flagi

    def on_break(self) -> None:
        self._break_flag = True

    def on_continue(self) -> None:
        self._continue_flag = True

    def on_return(self, value: Any) -> None:
        self._return_flag = True
        self._return_value = value

    def should_break(self) -> bool:
        return self._break_flag

    def should_continue(self) -> bool:
        return self._continue_flag

    def should_return(self) -> bool:
        return self._return_flag

    def should_interrupt(self) -> bool:
        return self._break_flag or self._continue_flag or self._return_flag

    def get_return_value(self) -> Any:
        return self._return_value

    # match

    def set_subject_index(self, index: int) -> None:
        for scope in reversed(self.scopes):
            if isinstance(scope, MatchScope):
                scope.set_index(index)
                return
        raise RuntimeError("Not in match context", None)

    def get_match_targets(self) -> List[Any]:
        for scope in reversed(self.scopes):
            if isinstance(scope, MatchScope):
                return scope.get_match_targets()
        raise RuntimeError("Not in match context", None)

    def get_current_target(self) -> Any:
        for scope in reversed(self.scopes):
            if isinstance(scope, MatchScope):
                return scope.get_match_target()
        raise RuntimeError("Not in match context", None)

    def is_in_match(self) -> bool:
        for scope in self.scopes:
            if isinstance(scope, MatchScope):
                return True
        return False


class Environment:
    max_depth = 1000

    def __init__(self) -> None:
        self._call_contexts: List[CallContext] = []
        self._functions: Dict[str, Any] = {}

    def current_context(self) -> CallContext:
        if not self._call_contexts:
            raise RuntimeError("No active call context", None)
        return self._call_contexts[-1]

    def enter_function(
        self,
        args: Optional[List[Any]] = None,
        name: Optional[str] = None,
        call_location: Optional[SourceLocation] = None,
    ) -> None:
        if args is None:
            args = []
        if len(self._call_contexts) > self.max_depth:
            raise LimitError(
                f"Maximum recursion depth exceeded ({self.max_depth})", call_location
            )

        current_context = CallContext(
            args, name if name else "<anonymous>", call_location
        )

        self._call_contexts.append(current_context)

    def exit_function(self) -> None:
        if self._call_contexts:
            self._call_contexts.pop()

    # bloki
    def enter_block(self) -> None:
        self.current_context().push_scope()

    def exit_block(self) -> None:
        self.current_context().pop_scope()

    # petle
    def enter_loop(self) -> None:
        self.current_context().enter_loop()

    def exit_loop(self) -> None:
        self.current_context().exit_loop()

    def is_in_loop(self) -> bool:
        return self.current_context().is_in_loop()

    # match

    def enter_match(self, subjects_with_aliases: List[Any]) -> None:
        self.current_context().push_match_scope(subjects_with_aliases)

    def exit_match(self) -> None:
        self.current_context().pop_scope()

    def set_subject_index(self, index: int) -> None:
        self.current_context().set_subject_index(index)

    def get_match_targets(self) -> List[Any]:
        return self.current_context().get_match_targets()

    def get_current_target(self) -> Any:
        return self.current_context().get_current_target()

    def is_in_match(self) -> bool:
        return self.current_context().is_in_match()

    # flagi

    def on_break(self) -> None:
        self.current_context().on_break()

    def on_continue(self) -> None:
        self.current_context().on_continue()

    def on_return(self, value: Any = None) -> None:
        self.current_context().on_return(value)

    def should_break(self) -> bool:
        return self.current_context().should_break()

    def should_continue(self) -> bool:
        return self.current_context().should_continue()

    def should_return(self) -> bool:
        return self.current_context().should_return()

    def should_interrupt(self) -> bool:
        return self.current_context().should_interrupt()

    def get_return_value(self) -> Any:
        return self.current_context().get_return_value()

    # zmienne

    def define(self, name: str, value: Any) -> None:
        self.current_context().define(name, value)

    def get(self, name: str) -> Any:
        return self.current_context().get(name)

    def assign(self, name: str, value: Any) -> bool:
        return self.current_context().assign(name, value)

    def define_or_assign(self, name: str, value: Any) -> None:
        self.current_context().define_or_assign(name, value)

    # funkcje globalne

    def define_function(self, name: str, func: Any) -> None:
        self._functions[name] = func

    def get_function(self, name: str) -> Any:
        return self._functions.get(name)

    def has_function(self, name: str) -> bool:
        return name in self._functions

    def get_args(self) -> List[Any]:
        return self.current_context().args

    # info

    def get_function_info(self) -> Dict[str, Any]:
        ctx = self.current_context()
        return {"name": ctx.name, "args": ctx.args, "location": ctx.call_location}

    def depth(self) -> int:
        return len(self._call_contexts)
