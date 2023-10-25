from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any


class TokenType(StrEnum):
    INT = auto()
    PLUS = auto()
    MINUS = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: Any = None
