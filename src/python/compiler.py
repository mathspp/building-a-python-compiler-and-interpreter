from dataclasses import dataclass
from enum import auto, StrEnum
from typing import Any, Generator

from .parser import (
    Assignment,
    BinOp,
    ExprStatement,
    Float,
    Int,
    Program,
    TreeNode,
    UnaryOp,
    Variable,
)


class BytecodeType(StrEnum):
    BINOP = auto()
    UNARYOP = auto()
    PUSH = auto()
    POP = auto()
    SAVE = auto()
    LOAD = auto()

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

    def compile_Program(self, program: Program) -> BytecodeGenerator:
        for statement in program.statements:
            yield from self._compile(statement)

    def compile_Assignment(self, assignment: Assignment) -> BytecodeGenerator:
        yield from self._compile(assignment.value)
        yield Bytecode(BytecodeType.SAVE, assignment.target.name)

    def compile_ExprStatement(self, expression: ExprStatement) -> BytecodeGenerator:
        yield from self._compile(expression.expr)
        yield Bytecode(BytecodeType.POP)

    def compile_UnaryOp(self, tree: UnaryOp) -> BytecodeGenerator:
        yield from self._compile(tree.value)
        yield Bytecode(BytecodeType.UNARYOP, tree.op)

    def compile_BinOp(self, tree: BinOp) -> BytecodeGenerator:
        yield from self._compile(tree.left)
        yield from self._compile(tree.right)
        yield Bytecode(BytecodeType.BINOP, tree.op)

    def compile_Int(self, tree: Int) -> BytecodeGenerator:
        yield Bytecode(BytecodeType.PUSH, tree.value)

    def compile_Float(self, tree: Float) -> BytecodeGenerator:
        yield Bytecode(BytecodeType.PUSH, tree.value)

    def compile_Variable(self, var: Variable) -> BytecodeGenerator:
        yield Bytecode(BytecodeType.LOAD, var.name)


if __name__ == "__main__":
    import sys
    from .tokenizer import Tokenizer
    from .parser import Parser

    code = sys.argv[1]
    compiler = Compiler(Parser(list(Tokenizer(code))).parse())
    for bc in compiler.compile():
        print(bc)
