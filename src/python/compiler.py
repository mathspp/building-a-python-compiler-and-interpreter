from dataclasses import dataclass
from enum import auto, StrEnum
from typing import Any, Generator

from .parser import BinOp


class BytecodeType(StrEnum):
    BINOP = auto()
    PUSH = auto()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


@dataclass
class Bytecode:
    type: BytecodeType
    value: Any = None


class Compiler:
    def __init__(self, tree: BinOp) -> None:
        self.tree = tree

    def compile(self) -> Generator[Bytecode, None, None]:
        left = self.tree.left
        yield Bytecode(BytecodeType.PUSH, left.value)

        right = self.tree.right
        yield Bytecode(BytecodeType.PUSH, right.value)

        yield Bytecode(BytecodeType.BINOP, self.tree.op)


if __name__ == "__main__":
    from .tokenizer import Tokenizer
    from .parser import Parser

    compiler = Compiler(Parser(list(Tokenizer("3 + 5"))).parse())
    for bc in compiler.compile():
        print(bc)
