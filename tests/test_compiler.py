from python.compiler import Bytecode, BytecodeType, Compiler
from python.parser import (
    Assignment,
    BinOp,
    Body,
    Conditional,
    ExprStatement,
    Float,
    Int,
    Program,
    UnaryOp,
    Variable,
)


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


def test_compile_multiplication():
    tree = BinOp(
        "*",
        Int(3),
        Float(3.14),
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
        Int(1),
        Int(2),
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
        Float(0.1),
        Float(3.14),
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
        Int(-3),
        Float(-5.6),
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
            ExprStatement(Int(1)),
            ExprStatement(Float(2.0)),
            ExprStatement(BinOp("+", Float(3.0), Float(4.0))),
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
        Int(3),
    )
    bytecode = list(Compiler(tree).compile())
    assert bytecode == [
        Bytecode(BytecodeType.PUSH, 3),
        Bytecode(BytecodeType.SAVE, "_123"),
    ]


def test_compile_program_with_assignments():
    tree = Program(
        [
            Assignment([Variable("a")], Int(3)),
            ExprStatement(BinOp("**", Int(4), Int(5))),
            Assignment([Variable("b")], Int(7)),
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
                    Int(3),
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
                Int(3),
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
                            value=Int(1),
                        ),
                    ],
                ),
            ),
            Assignment(
                targets=[
                    Variable("done"),
                ],
                value=Int(1),
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
                            value=Int(2),
                        ),
                        Conditional(
                            condition=Variable("three"),
                            body=Body(
                                statements=[
                                    Assignment(
                                        targets=[
                                            Variable("four"),
                                        ],
                                        value=Int(4),
                                    ),
                                    Assignment(
                                        targets=[
                                            Variable("five"),
                                        ],
                                        value=Int(5),
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
                                        value=Int(7),
                                    ),
                                ],
                            ),
                        ),
                        Assignment(
                            targets=[
                                Variable("eight"),
                            ],
                            value=Int(8),
                        ),
                        Conditional(
                            condition=Variable("nine"),
                            body=Body(
                                statements=[
                                    Assignment(
                                        targets=[
                                            Variable("ten"),
                                        ],
                                        value=Int(10),
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
                value=Int(11),
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
