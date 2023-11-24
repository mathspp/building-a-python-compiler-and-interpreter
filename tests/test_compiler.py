import pytest

from python.compiler import Bytecode, BytecodeType, Compiler
from python.parser import (
    Assignment,
    BinOp,
    Body,
    BoolOp,
    Conditional,
    Constant,
    ExprStatement,
    Program,
    UnaryOp,
    Variable,
)


def test_compile_addition():
    tree = BinOp(
        "+",
        Constant(3),
        Constant(5),
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
        Constant(5),
        Constant(2),
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
                        Constant(3),
                        Constant(5),
                    ),
                    Constant(7),
                ),
                Constant(1.2),
            ),
            Constant(2.4),
        ),
        Constant(3.6),
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
    tree = UnaryOp("-", Constant(3))
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 3),
        Bytecode(BytecodeType.UNARYOP, "-"),
    ]


def test_compile_unary_plus():
    tree = UnaryOp("+", Constant(3))
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
                    Constant(3.5),
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


def test_compile_multiplication():
    tree = BinOp(
        "*",
        Constant(3),
        Constant(3.14),
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 3),
        Bytecode(BytecodeType.PUSH, 3.14),
        Bytecode(BytecodeType.BINOP, "*"),
    ]


def test_compile_division():
    tree = BinOp(
        "/",
        Constant(1),
        Constant(2),
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 1),
        Bytecode(BytecodeType.PUSH, 2),
        Bytecode(BytecodeType.BINOP, "/"),
    ]


def test_compile_exponentiation():
    tree = BinOp(
        "**",
        Constant(0.1),
        Constant(3.14),
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 0.1),
        Bytecode(BytecodeType.PUSH, 3.14),
        Bytecode(BytecodeType.BINOP, "**"),
    ]


def test_compile_modulo():
    tree = BinOp(
        "%",
        Constant(-3),
        Constant(-5.6),
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, -3),
        Bytecode(BytecodeType.PUSH, -5.6),
        Bytecode(BytecodeType.BINOP, "%"),
    ]


def test_compile_program_and_expr_statement():
    tree = Program(
        [
            ExprStatement(Constant(1)),
            ExprStatement(Constant(2.0)),
            ExprStatement(BinOp("+", Constant(3.0), Constant(4.0))),
        ]
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 1),
        Bytecode(BytecodeType.POP),
        Bytecode(BytecodeType.PUSH, 2.0),
        Bytecode(BytecodeType.POP),
        Bytecode(BytecodeType.PUSH, 3.0),
        Bytecode(BytecodeType.PUSH, 4.0),
        Bytecode(BytecodeType.BINOP, "+"),
        Bytecode(BytecodeType.POP),
    ]


def test_compile_assignment():
    tree = Assignment(
        [Variable("_123")],
        Constant(3),
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 3),
        Bytecode(BytecodeType.SAVE, "_123"),
    ]


def test_compile_program_with_assignments():
    tree = Program(
        [
            Assignment([Variable("a")], Constant(3)),
            ExprStatement(BinOp("**", Constant(4), Constant(5))),
            Assignment([Variable("b")], Constant(7)),
        ]
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 3),
        Bytecode(BytecodeType.SAVE, "a"),
        Bytecode(BytecodeType.PUSH, 4),
        Bytecode(BytecodeType.PUSH, 5),
        Bytecode(BytecodeType.BINOP, "**"),
        Bytecode(BytecodeType.POP, None),
        Bytecode(BytecodeType.PUSH, 7),
        Bytecode(BytecodeType.SAVE, "b"),
    ]


def test_compile_variable_reference():
    tree = Program(
        [
            Assignment(
                [Variable("a")],
                BinOp(
                    "+",
                    Variable("b"),
                    Constant(3),
                ),
            ),
        ]
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.LOAD, "b"),
        Bytecode(BytecodeType.PUSH, 3),
        Bytecode(BytecodeType.BINOP, "+"),
        Bytecode(BytecodeType.SAVE, "a"),
    ]


def test_compile_consecutive_assignments():
    tree = Program(
        [
            Assignment(
                [
                    Variable("a"),
                    Variable("b"),
                    Variable("c"),
                ],
                Constant(3),
            ),
        ]
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 3),
        Bytecode(BytecodeType.COPY),
        Bytecode(BytecodeType.SAVE, "a"),
        Bytecode(BytecodeType.COPY),
        Bytecode(BytecodeType.SAVE, "b"),
        Bytecode(BytecodeType.SAVE, "c"),
    ]


def test_single_conditional():
    tree = Program(
        statements=[
            Conditional(
                condition=Variable("cond"),
                body=Body(
                    statements=[
                        Assignment(
                            targets=[
                                Variable("visited"),
                            ],
                            value=Constant(1),
                        ),
                    ],
                ),
            ),
            Assignment(
                targets=[
                    Variable("done"),
                ],
                value=Constant(1),
            ),
        ],
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.LOAD, "cond"),
        Bytecode(BytecodeType.POP_JUMP_IF_FALSE, 3),
        Bytecode(BytecodeType.PUSH, 1),
        Bytecode(BytecodeType.SAVE, "visited"),
        Bytecode(BytecodeType.PUSH, 1),
        Bytecode(BytecodeType.SAVE, "done"),
    ]


def test_multiple_conditionals():
    """Tests multiple nested conditionals:

    if one:
        two = 2
        if three:
            four = 4
            five = 5

        if six:
            seven = 7

        eight = 8
        if nine:
            ten = 10
    eleven = 11
    """
    tree = Program(
        statements=[
            Conditional(
                condition=Variable("one"),
                body=Body(
                    statements=[
                        Assignment(
                            targets=[
                                Variable("two"),
                            ],
                            value=Constant(2),
                        ),
                        Conditional(
                            condition=Variable("three"),
                            body=Body(
                                statements=[
                                    Assignment(
                                        targets=[
                                            Variable("four"),
                                        ],
                                        value=Constant(4),
                                    ),
                                    Assignment(
                                        targets=[
                                            Variable("five"),
                                        ],
                                        value=Constant(5),
                                    ),
                                ],
                            ),
                        ),
                        Conditional(
                            condition=Variable("six"),
                            body=Body(
                                statements=[
                                    Assignment(
                                        targets=[
                                            Variable("seven"),
                                        ],
                                        value=Constant(7),
                                    ),
                                ],
                            ),
                        ),
                        Assignment(
                            targets=[
                                Variable("eight"),
                            ],
                            value=Constant(8),
                        ),
                        Conditional(
                            condition=Variable("nine"),
                            body=Body(
                                statements=[
                                    Assignment(
                                        targets=[
                                            Variable("ten"),
                                        ],
                                        value=Constant(10),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
            Assignment(
                targets=[
                    Variable("eleven"),
                ],
                value=Constant(11),
            ),
        ],
    )

    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.LOAD, "one"),
        Bytecode(BytecodeType.POP_JUMP_IF_FALSE, 19),
        Bytecode(BytecodeType.PUSH, 2),
        Bytecode(BytecodeType.SAVE, "two"),
        Bytecode(BytecodeType.LOAD, "three"),
        Bytecode(BytecodeType.POP_JUMP_IF_FALSE, 5),
        Bytecode(BytecodeType.PUSH, 4),
        Bytecode(BytecodeType.SAVE, "four"),
        Bytecode(BytecodeType.PUSH, 5),
        Bytecode(BytecodeType.SAVE, "five"),
        Bytecode(BytecodeType.LOAD, "six"),
        Bytecode(BytecodeType.POP_JUMP_IF_FALSE, 3),
        Bytecode(BytecodeType.PUSH, 7),
        Bytecode(BytecodeType.SAVE, "seven"),
        Bytecode(BytecodeType.PUSH, 8),
        Bytecode(BytecodeType.SAVE, "eight"),
        Bytecode(BytecodeType.LOAD, "nine"),
        Bytecode(BytecodeType.POP_JUMP_IF_FALSE, 3),
        Bytecode(BytecodeType.PUSH, 10),
        Bytecode(BytecodeType.SAVE, "ten"),
        Bytecode(BytecodeType.PUSH, 11),
        Bytecode(BytecodeType.SAVE, "eleven"),
    ]


def test_compile_booleans():
    tree = Program(
        statements=[
            Assignment(
                targets=[
                    Variable("a"),
                ],
                value=Constant(True),
            ),
            Assignment(
                targets=[
                    Variable("b"),
                ],
                value=Constant(False),
            ),
        ],
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, True),
        Bytecode(BytecodeType.SAVE, "a"),
        Bytecode(BytecodeType.PUSH, False),
        Bytecode(BytecodeType.SAVE, "b"),
    ]


@pytest.mark.parametrize(
    ["op", "jump_type"],
    [
        ("and", BytecodeType.POP_JUMP_IF_FALSE),
        ("or", BytecodeType.POP_JUMP_IF_TRUE),
    ],
)
def test_compile_and_short_circuiting(op: str, jump_type: BytecodeType):
    tree = Program(
        statements=[
            ExprStatement(
                BoolOp(
                    op=op,
                    values=[
                        BinOp(
                            op="+",
                            left=Constant(1),
                            right=Constant(2),
                        ),
                        Variable("c"),
                        BinOp(
                            op="+",
                            left=Constant(3),
                            right=Constant(5),
                        ),
                    ],
                )
            )
        ]
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 1),
        Bytecode(BytecodeType.PUSH, 2),
        Bytecode(BytecodeType.BINOP, "+"),
        Bytecode(BytecodeType.COPY),
        Bytecode(jump_type, 9),
        Bytecode(BytecodeType.POP),
        Bytecode(BytecodeType.LOAD, "c"),
        Bytecode(BytecodeType.COPY),
        Bytecode(jump_type, 5),
        Bytecode(BytecodeType.POP),
        Bytecode(BytecodeType.PUSH, 3),
        Bytecode(BytecodeType.PUSH, 5),
        Bytecode(BytecodeType.BINOP, "+"),
        Bytecode(BytecodeType.POP),
    ]
