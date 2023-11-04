from dataclasses import dataclass
from enum import StrEnum, auto
from string import digits
from typing import Any, Generator


class TokenType(StrEnum):
    INT = auto()
    FLOAT = auto()
    PLUS = auto()
    MINUS = auto()
    EOF = auto()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


@dataclass
class Token:
    type: TokenType
    value: Any = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.type!r}, {self.value!r})"


class Tokenizer:
    def __init__(self, code: str) -> None:
        self.code = code
        self.ptr: int = 0

    def consume_int(self) -> int:
        """Reads an integer from the source code."""
        start = self.ptr
        while self.ptr < len(self.code) and self.code[self.ptr] in digits:
            self.ptr += 1
        return int(self.code[start : self.ptr])

    def consume_decimal(self) -> float:
        """Reads a decimal part that starts with a . and returns it as a float."""
        start = self.ptr
        self.ptr += 1
        while self.ptr < len(self.code) and self.code[self.ptr] in digits:
            self.ptr += 1
        # Did we actually read _any_ digits or did we only manage to read the `.`?
        float_str = self.code[start : self.ptr] if self.ptr - start > 1 else ".0"
        return float(float_str)

    def next_token(self) -> Token:
        while self.ptr < len(self.code) and self.code[self.ptr] == " ":
            self.ptr += 1

        if self.ptr == len(self.code):
            return Token(TokenType.EOF)

        char = self.code[self.ptr]
        if char == "+":
            self.ptr += 1
            return Token(TokenType.PLUS)
        elif char == "-":
            self.ptr += 1
            return Token(TokenType.MINUS)
        elif char in digits:
            integer = self.consume_int()
            # Is the integer followed by a decimal part?
            if self.ptr < len(self.code) and self.code[self.ptr] == ".":
                decimal = self.consume_decimal()
                return Token(TokenType.FLOAT, integer + decimal)
            return Token(TokenType.INT, integer)
        elif (  # Make sure we don't read a lone full stop `.`.
            char == "."
            and self.ptr + 1 < len(self.code)
            and self.code[self.ptr + 1] in digits
        ):
            decimal = self.consume_decimal()
            return Token(TokenType.FLOAT, decimal)
        else:
            raise RuntimeError(f"Can't tokenize {char!r}.")

    def __iter__(self) -> Generator[Token, None, None]:
        while (token := self.next_token()).type != TokenType.EOF:
            yield token
        yield token  # Yield the EOF token too.


if __name__ == "__main__":
    code = "1 + 2 + 3 + 4 - 5 - 6 + 7 - 8"
    tokenizer = Tokenizer(code)
    print(code)
    for tok in tokenizer:
        print(f"\t{tok.type}, {tok.value}")
