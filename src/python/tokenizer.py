from dataclasses import dataclass
from enum import StrEnum, auto
from string import digits, ascii_letters
from typing import Any, Generator


class TokenType(StrEnum):
    INT = auto()  # integers
    FLOAT = auto()  # floats
    PLUS = auto()  # +
    MINUS = auto()  # -
    EOF = auto()  # end of file
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    MUL = auto()  # *
    DIV = auto()  # /
    MOD = auto()  # %
    EXP = auto()  # **
    NEWLINE = auto()  # newline character
    NAME = auto()  # any possible variable name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


CHARS_AS_TOKENS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "*": TokenType.MUL,
    "/": TokenType.DIV,
    "%": TokenType.MOD,
}

LEGAL_NAME_CHARACTERS = ascii_letters + digits + "_"
LEGAL_NAME_START_CHARACTERS = ascii_letters + "_"


@dataclass
class Token:
    type: TokenType
    value: Any = None

    def __repr__(self) -> str:
        if self.value is not None:
            return f"{self.__class__.__name__}({self.type!r}, {self.value!r})"
        else:
            return f"{self.__class__.__name__}({self.type!r})"


class Tokenizer:
    def __init__(self, code: str) -> None:
        self.code = code + "\n"  # Ensure the program ends with a newline.
        self.ptr: int = 0
        self.beginning_of_line = True

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

    def consume_name(self) -> str:
        """Consumes a sequence of characters that could be a variable name."""
        start = self.ptr
        self.ptr += 1
        while (
            self.ptr < len(self.code) and self.code[self.ptr] in LEGAL_NAME_CHARACTERS
        ):
            self.ptr += 1
        return self.code[start : self.ptr]

    def peek(self, length: int = 1) -> str:
        """Returns the substring that will be tokenized next."""
        return self.code[self.ptr : self.ptr + length]

    def next_token(self) -> Token:
        while self.ptr < len(self.code) and self.code[self.ptr] == " ":
            self.ptr += 1

        if self.ptr == len(self.code):
            return Token(TokenType.EOF)

        char = self.code[self.ptr]
        if char == "\n":
            self.ptr += 1
            if not self.beginning_of_line:
                self.beginning_of_line = True
                return Token(TokenType.NEWLINE)
            else:
                return self.next_token()

        self.beginning_of_line = False
        if self.peek(length=2) == "**":
            self.ptr += 2
            return Token(TokenType.EXP)
        elif char in CHARS_AS_TOKENS:
            self.ptr += 1
            return Token(CHARS_AS_TOKENS[char])
        elif char in LEGAL_NAME_START_CHARACTERS:
            name = self.consume_name()
            return Token(TokenType.NAME, name)
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
    import sys

    code = sys.argv[1]
    for token in Tokenizer(code):
        print(token)
