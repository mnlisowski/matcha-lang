from typing import Any, Optional

class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.values = {}
        self.parent = parent

    def define(self, name: str, value: any):
        self.values[name] = value

    def get(self, name: str):
        if name in self.values:
            return self.values[name]
        
        if self.parent is not None:
            return self.parent.get(name)
        
        raise RuntimeError(f"variable `{name}` not defined")

    def assign(self, name: str, value: Any) -> bool:
        if name in self.values:
            self.values[name] = value
            return True
        
        if self.parent is not None:
            return self.parent.assign(name, value)
        
        return False #