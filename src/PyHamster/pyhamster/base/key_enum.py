# Key Enum class

from enum import StrEnum
from typing import Any

class KeyEnum(StrEnum):
    """StrEnum type that always return `.value`."""
    
    def __new__(cls, value:str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other:Any) -> bool:
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)
    
    def __format__(self, format_spec:str) -> str:
        return self.value.__format__(format_spec)