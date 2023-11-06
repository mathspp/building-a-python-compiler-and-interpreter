from python.compiler import Bytecode, BytecodeType, Compiler
from python.parser import BinOp, Float, Int, UnaryOp


def test_compile_addition():
    tree = BinOp(
        "+",
        Int(3),
        Int(5),
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 3),
        Bytecode(BytecodeType.PUSH, 5),
        Bytecode(BytecodeType.BINOP, "+"),
    ]


def test_compile_subtraction():
    tree = BinOp(
        "-",
        Int(5),
        Int(2),
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 5),
        Bytecode(BytecodeType.PUSH, 2),
        Bytecode(BytecodeType.BINOP, "-"),
    ]


def test_compile_nested_additions_and_subtractions():
    tree = BinOp(
        "-",
        BinOp(
            "+",
            BinOp(
                "+",
                BinOp(
                    "-",
                    BinOp(
                        "+",
                        Int(3),
                        Int(5),
                    ),
                    Int(7),
                ),
                Float(1.2),
            ),
            Float(2.4),
        ),
        Float(3.6),
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 3),
        Bytecode(BytecodeType.PUSH, 5),
        Bytecode(BytecodeType.BINOP, "+"),
        Bytecode(BytecodeType.PUSH, 7),
        Bytecode(BytecodeType.BINOP, "-"),
        Bytecode(BytecodeType.PUSH, 1.2),
        Bytecode(BytecodeType.BINOP, "+"),
        Bytecode(BytecodeType.PUSH, 2.4),
        Bytecode(BytecodeType.BINOP, "+"),
        Bytecode(BytecodeType.PUSH, 3.6),
        Bytecode(BytecodeType.BINOP, "-"),
    ]


def test_compile_unary_minus():
    tree = UnaryOp("-", Int(3))
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 3),
        Bytecode(BytecodeType.UNARYOP, "-"),
    ]


def test_compile_unary_plus():
    tree = UnaryOp("+", Int(3))
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 3),
        Bytecode(BytecodeType.UNARYOP, "+"),
    ]


def test_compile_unary_operations():
    tree = UnaryOp(
        "-",
        UnaryOp(
            "-",
            UnaryOp(
                "+",
                UnaryOp(
                    "+",
                    Float(3.5),
                ),
            ),
        ),
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 3.5),
        Bytecode(BytecodeType.UNARYOP, "+"),
        Bytecode(BytecodeType.UNARYOP, "+"),
        Bytecode(BytecodeType.UNARYOP, "-"),
        Bytecode(BytecodeType.UNARYOP, "-"),
    ]
