import operator
from typing import Any

from .compiler import Bytecode


BINOPS_TO_OPERATOR = {
    "**": operator.pow,
    "%": operator.mod,
    "/": operator.truediv,
    "*": operator.mul,
    "+": operator.add,
    "-": operator.sub,
}


class Stack:
    def __init__(self) -> None:
        self.stack: list[int] = []

    def push(self, item: int) -> None:
        self.stack.append(item)

    def pop(self) -> int:
        return self.stack.pop()

    def peek(self) -> int:
        return self.stack[-1]

    def __repr__(self) -> str:
        return f"Stack({self.stack})"


class Interpreter:
    def __init__(self, bytecode: list[Bytecode]) -> None:
        self.stack = Stack()
        self.bytecode = bytecode
        self.ptr: int = 0
        self.last_value_popped: Any = None

    def interpret(self) -> None:
        for bc in self.bytecode:
            bc_name = bc.type.value
            interpret_method = getattr(self, f"interpret_{bc_name}", None)
            if interpret_method is None:
                raise RuntimeError(f"Can't interpret {bc_name}.")
            interpret_method(bc)

        print("Done!")
        print(self.last_value_popped)

    def interpret_push(self, bc: Bytecode) -> None:
        self.stack.push(bc.value)

    def interpret_pop(self, bc: Bytecode) -> None:
        self.last_value_popped = self.stack.pop()

    def interpret_binop(self, bc: Bytecode) -> None:
        right = self.stack.pop()
        left = self.stack.pop()
        op = BINOPS_TO_OPERATOR.get(bc.value, None)
        if op is not None:
            result = op(left, right)
        else:
            raise RuntimeError(f"Unknown operator {bc.value}.")
        self.stack.push(result)

    def interpret_unaryop(self, bc: Bytecode) -> None:
        result = self.stack.pop()
        if bc.value == "+":
            pass
        elif bc.value == "-":
            result = -result
        else:
            raise RuntimeError(f"Unknown operator {bc.value}.")
        self.stack.push(result)


if __name__ == "__main__":
    import sys

    from .tokenizer import Tokenizer
    from .parser import Parser
    from .compiler import Compiler

    code = sys.argv[1]
    tokens = list(Tokenizer(code))
    tree = Parser(tokens).parse()
    bytecode = list(Compiler(tree).compile())
    Interpreter(bytecode).interpret()
