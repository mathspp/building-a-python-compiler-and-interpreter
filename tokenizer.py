from dataclasses import dataclass
from enum import StrEnum, auto
from string import digits
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


class Tokenizer:
    def __init__(self, code: str) -> None:
        self.code = code
        self.ptr: int = 0

    def next_token(self) -> Token:
        while self.ptr < len(self.code) and self.code[self.ptr] == " ":
            self.ptr += 1

        if self.ptr == len(self.code):
            return Token(TokenType.EOF)

        char = self.code[self.ptr]
        self.ptr += 1
        if char == "+":
            return Token(TokenType.PLUS)
        elif char == "-":
            return Token(TokenType.MINUS)
        elif char in digits:
            return Token(TokenType.INT, int(char))
        else:
            raise RuntimeError(f"Can't tokenize {char!r}.")


if __name__ == "__main__":
    code = "1 + 2 + 3 + 4 - 5 - 6 + 7 - 8"
    tok = Tokenizer(code)
    for _ in range(20):
        print(tok.next_token())
