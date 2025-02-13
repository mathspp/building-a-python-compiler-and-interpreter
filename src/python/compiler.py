from dataclasses import dataclass
from enum import auto, StrEnum
from typing import Any, Generator

from .parser import (
    Assignment,
    BinOp,
    Body,
    BoolOp,
    Conditional,
    Constant,
    ExprStatement,
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
    COPY = auto()
    POP_JUMP_IF_FALSE = auto()
    POP_JUMP_IF_TRUE = auto()
    JUMP_FORWARD = auto()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


@dataclass
class Bytecode:
    type: BytecodeType
    value: Any = None

    def __repr__(self) -> str:
        if self.value is not None:
            return f"{self.__class__.__name__}({self.type!r}, {self.value!r})"
        else:
            return f"{self.__class__.__name__}({self.type!r})"


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

    def compile_Conditional(self, conditional: Conditional) -> BytecodeGenerator:
        condition_bytecode = self._compile(conditional.condition)
        body_bytecode = list(self._compile(conditional.body))
        orelse = conditional.orelse
        orelse_bytecode = [] if orelse is None else list(self._compile(orelse))

        # Add a “jump past the else” at the end of the `if` when needed:
        if orelse_bytecode:
            body_bytecode.append(
                Bytecode(BytecodeType.JUMP_FORWARD, len(orelse_bytecode) + 1)
            )

        yield from condition_bytecode
        yield Bytecode(  # If the condition is false, jump past the body of the `if`.
            BytecodeType.POP_JUMP_IF_FALSE, len(body_bytecode) + 1
        )
        yield from body_bytecode
        yield from orelse_bytecode

    def compile_Body(self, body: Body) -> BytecodeGenerator:
        for statement in body.statements:
            yield from self._compile(statement)

    def compile_Assignment(self, assignment: Assignment) -> BytecodeGenerator:
        yield from self._compile(assignment.value)
        # For all but the last, we create a copy before saving.
        for target in assignment.targets[:-1]:
            yield Bytecode(BytecodeType.COPY)
            yield Bytecode(BytecodeType.SAVE, target.name)
        # Last one, we can finally consume the value at the top of the stack.
        yield Bytecode(BytecodeType.SAVE, assignment.targets[-1].name)

    def compile_ExprStatement(self, expression: ExprStatement) -> BytecodeGenerator:
        yield from self._compile(expression.expr)
        yield Bytecode(BytecodeType.POP)

    def compile_BoolOp(self, tree: BoolOp) -> BytecodeGenerator:
        compiled_values = [list(self._compile(value)) for value in tree.values]
        compiled_lengths = [len(bytecode) for bytecode in compiled_values]
        jump_bytecode = (
            BytecodeType.POP_JUMP_IF_FALSE
            if tree.op == "and"
            else BytecodeType.POP_JUMP_IF_TRUE
        )

        for emitted, compiled_value in enumerate(compiled_values[:-1], start=1):
            yield from compiled_value
            jump_segments_missing = len(tree.values) - emitted - 1
            jump_location = (
                sum(compiled_lengths[emitted:]) + jump_segments_missing * 3 + 2
            )
            yield Bytecode(BytecodeType.COPY)
            yield Bytecode(jump_bytecode, jump_location)
            yield Bytecode(BytecodeType.POP)
        yield from compiled_values[-1]

    def compile_UnaryOp(self, tree: UnaryOp) -> BytecodeGenerator:
        yield from self._compile(tree.value)
        yield Bytecode(BytecodeType.UNARYOP, tree.op)

    def compile_BinOp(self, tree: BinOp) -> BytecodeGenerator:
        yield from self._compile(tree.left)
        yield from self._compile(tree.right)
        yield Bytecode(BytecodeType.BINOP, tree.op)

    def compile_Constant(self, constant: Constant) -> BytecodeGenerator:
        yield Bytecode(BytecodeType.PUSH, constant.value)

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
