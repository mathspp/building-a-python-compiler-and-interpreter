from dataclasses import dataclass
from enum import auto, StrEnum
from typing import Any, Generator

from .parser import BinOp, Float, Int, TreeNode


class BytecodeType(StrEnum):
    BINOP = auto()
    PUSH = auto()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


@dataclass
class Bytecode:
    type: BytecodeType
    value: Any = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.type!r}, {self.value!r})"


type BytecodeGenerator = Generator[Bytecode, None, None]


class Compiler:
    def __init__(self, tree: TreeNode) -> None:
        self.tree = tree

    def compile(self) -> BytecodeGenerator:
        yield from self._compile(self.tree)

    def _compile(self, tree: TreeNode) -> BytecodeGenerator:
        node_name = tree.__class__.__name__
        compile_method = getattr(self, f"compile_{node_name}", None)
        if compile_method is None:
            raise RuntimeError(f"Can't compile {node_name}.")
        yield from compile_method(tree)

    def compile_BinOp(self, tree: BinOp) -> BytecodeGenerator:
        yield from self._compile(tree.left)
        yield from self._compile(tree.right)
        yield Bytecode(BytecodeType.BINOP, tree.op)

    def compile_Int(self, tree: Int) -> BytecodeGenerator:
        yield Bytecode(BytecodeType.PUSH, tree.value)

    def compile_Float(self, tree: Float) -> BytecodeGenerator:
        yield Bytecode(BytecodeType.PUSH, tree.value)


if __name__ == "__main__":
    from .tokenizer import Tokenizer
    from .parser import Parser

    compiler = Compiler(Parser(list(Tokenizer("3 + 5 - 7 + 1.2 + 2.4 - 3.6"))).parse())
    for bc in compiler.compile():
        print(bc)
