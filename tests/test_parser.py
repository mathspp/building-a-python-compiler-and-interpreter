from python.parser import Parser
from python.parser import (
    Assignment,
    BinOp,
    Body,
    Conditional,
    Constant,
    ExprStatement,
    Program,
    UnaryOp,
    Variable,
)
from python.tokenizer import Token, Tokenizer, TokenType

import pytest


def test_parsing_addition():
    tokens = [
        Token(TokenType.INT, 3),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 5),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == BinOp(
        "+",
        Constant(3),
        Constant(5),
    )


def test_parsing_subtraction():
    tokens = [
        Token(TokenType.INT, 5),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 2),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == BinOp(
        "-",
        Constant(5),
        Constant(2),
    )


def test_parsing_addition_with_floats():
    tokens = [
        Token(TokenType.FLOAT, 0.5),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 5),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == BinOp(
        "+",
        Constant(0.5),
        Constant(5),
    )


def test_parsing_subtraction_with_floats():
    tokens = [
        Token(TokenType.FLOAT, 5.0),
        Token(TokenType.MINUS),
        Token(TokenType.FLOAT, 0.2),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == BinOp(
        "-",
        Constant(5.0),
        Constant(0.2),
    )


def test_parsing_single_integer():
    tokens = [
        Token(TokenType.INT, 3),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == Constant(3)


def test_parsing_single_float():
    tokens = [
        Token(TokenType.FLOAT, 3.0),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == Constant(3.0)


def test_parsing_addition_then_subtraction():
    tokens = [
        Token(TokenType.INT, 3),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 5),
        Token(TokenType.MINUS),
        Token(TokenType.FLOAT, 0.2),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == BinOp(
        "-",
        BinOp(
            "+",
            Constant(3),
            Constant(5),
        ),
        Constant(0.2),
    )


def test_parsing_subtraction_then_addition():
    tokens = [
        Token(TokenType.INT, 3),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 5),
        Token(TokenType.PLUS),
        Token(TokenType.FLOAT, 0.2),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == BinOp(
        "+",
        BinOp(
            "-",
            Constant(3),
            Constant(5),
        ),
        Constant(0.2),
    )


def test_parsing_many_additions_and_subtractions():
    # 3 + 5 - 7 + 1.2 + 2.4 - 3.6
    tokens = [
        Token(TokenType.INT, 3),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 5),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 7),
        Token(TokenType.PLUS),
        Token(TokenType.FLOAT, 1.2),
        Token(TokenType.PLUS),
        Token(TokenType.FLOAT, 2.4),
        Token(TokenType.MINUS),
        Token(TokenType.FLOAT, 3.6),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == BinOp(
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


def test_parsing_unary_minus():
    tokens = [
        Token(TokenType.MINUS),
        Token(TokenType.INT, 3),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == UnaryOp("-", Constant(3))


def test_parsing_unary_plus():
    tokens = [
        Token(TokenType.PLUS),
        Token(TokenType.FLOAT, 3.0),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == UnaryOp("+", Constant(3))


def test_parsing_unary_operators():
    # --++3.5 - 2
    tokens = [
        Token(TokenType.MINUS),
        Token(TokenType.MINUS),
        Token(TokenType.PLUS),
        Token(TokenType.PLUS),
        Token(TokenType.FLOAT, 3.5),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 2),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == BinOp(
        "-",
        UnaryOp(
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
        ),
        Constant(2),
    )


def test_parsing_parentheses():
    # 1 + ( 2 + 3 )
    tokens = [
        Token(TokenType.INT, 1),
        Token(TokenType.PLUS),
        Token(TokenType.LPAREN),
        Token(TokenType.INT, 2),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 3),
        Token(TokenType.RPAREN),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == BinOp(
        "+",
        Constant(1),
        BinOp(
            "+",
            Constant(2),
            Constant(3),
        ),
    )


def test_parsing_parentheses_around_single_number():
    # ( ( ( 1 ) ) ) + ( 2 + ( 3 ) )
    tokens = [
        Token(TokenType.LPAREN),
        Token(TokenType.LPAREN),
        Token(TokenType.LPAREN),
        Token(TokenType.INT, 1),
        Token(TokenType.RPAREN),
        Token(TokenType.RPAREN),
        Token(TokenType.RPAREN),
        Token(TokenType.PLUS),
        Token(TokenType.LPAREN),
        Token(TokenType.INT, 2),
        Token(TokenType.PLUS),
        Token(TokenType.LPAREN),
        Token(TokenType.INT, 3),
        Token(TokenType.RPAREN),
        Token(TokenType.RPAREN),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == BinOp(
        "+",
        Constant(1),
        BinOp(
            "+",
            Constant(2),
            Constant(3),
        ),
    )


@pytest.mark.parametrize(
    "code",
    [
        "(1\n",
        "()\n",
        ") 1 + 2\n",
        "1 + 2)\n",
        "1 (+) 2\n",
        "1 + )2(\n",
    ],
)
def test_unbalanced_parentheses(code: str):
    tokens = list(Tokenizer(code))
    with pytest.raises(RuntimeError):
        Parser(tokens).parse_expr_statement()


def test_parsing_more_operators():
    # "1 % -2 ** -3 / 5 * 2 + 2 ** 3"
    tokens = [
        Token(TokenType.INT, 1),
        Token(TokenType.MOD),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 2),
        Token(TokenType.EXP),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 3),
        Token(TokenType.DIV),
        Token(TokenType.INT, 5),
        Token(TokenType.MUL),
        Token(TokenType.INT, 2),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 2),
        Token(TokenType.EXP),
        Token(TokenType.INT, 3),
    ]
    tree = Parser(tokens).parse_computation()
    assert tree == BinOp(
        "+",
        BinOp(
            "*",
            BinOp(
                "/",
                BinOp(
                    "%",
                    Constant(1),
                    UnaryOp(
                        "-",
                        BinOp(
                            "**",
                            Constant(2),
                            UnaryOp(
                                "-",
                                Constant(3),
                            ),
                        ),
                    ),
                ),
                Constant(5),
            ),
            Constant(2),
        ),
        BinOp(
            "**",
            Constant(2),
            Constant(3),
        ),
    )


def test_parsing_multiple_statements():
    code = "1 % -2\n5 ** -3 / 5\n1 * 2 + 2 ** 3\n"
    tree = Parser(list(Tokenizer(code))).parse()
    assert tree == Program(
        [
            ExprStatement(
                BinOp(
                    "%",
                    Constant(1),
                    UnaryOp(
                        "-",
                        Constant(2),
                    ),
                ),
            ),
            ExprStatement(
                BinOp(
                    "/",
                    BinOp(
                        "**",
                        Constant(5),
                        UnaryOp(
                            "-",
                            Constant(3),
                        ),
                    ),
                    Constant(5),
                ),
            ),
            ExprStatement(
                BinOp(
                    "+",
                    BinOp(
                        "*",
                        Constant(1),
                        Constant(2),
                    ),
                    BinOp(
                        "**",
                        Constant(2),
                        Constant(3),
                    ),
                ),
            ),
        ]
    )


def test_parsing_simple_assignment():
    tokens = [
        Token(TokenType.NAME, "a"),
        Token(TokenType.ASSIGN),
        Token(TokenType.INT, 5),
        Token(TokenType.NEWLINE),
    ]
    tree = Parser(tokens).parse_assignment()
    assert tree == Assignment(
        [Variable("a")],
        Constant(5),
    )


def test_program_with_assignments():
    code = "a = 3\nb = 7\nd = 2 ** 2 % 4"
    tree = Parser(list(Tokenizer(code))).parse()
    assert tree == Program(
        [
            Assignment(
                [Variable("a")],
                Constant(3),
            ),
            Assignment(
                [Variable("b")],
                Constant(7),
            ),
            Assignment(
                [Variable("d")],
                BinOp(
                    "%",
                    BinOp(
                        "**",
                        Constant(2),
                        Constant(2),
                    ),
                    Constant(4),
                ),
            ),
        ]
    )


def test_parse_variable_references():
    code = "a = b + 3"
    tree = Parser(list(Tokenizer(code))).parse()
    assert tree == Program(
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


def test_consecutive_assignments():
    code = "a = b = c = 3"
    tree = Parser(list(Tokenizer(code))).parse()
    assert tree == Program(
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


def test_conditional():
    code = "if 3 ** 4 - 80:\n    a = 3\n    b = 5"
    tree = Parser(list(Tokenizer(code))).parse()
    assert tree == Program(
        [
            Conditional(
                BinOp(
                    "-",
                    BinOp(
                        "**",
                        Constant(3),
                        Constant(4),
                    ),
                    Constant(80),
                ),
                Body(
                    [
                        Assignment(
                            [
                                Variable("a"),
                            ],
                            Constant(3),
                        ),
                        Assignment(
                            [
                                Variable("b"),
                            ],
                            Constant(5),
                        ),
                    ]
                ),
            ),
        ]
    )


def test_nested_conditionals():
    code = "if 1:\n\ta = 3\n\tb = a\n\tif 2:\n\t\tc = 3".expandtabs(tabsize=4)
    tree = Parser(list(Tokenizer(code))).parse()
    assert tree == Program(
        [
            Conditional(
                Constant(1),
                Body(
                    [
                        Assignment(
                            [
                                Variable("a"),
                            ],
                            Constant(3),
                        ),
                        Assignment(
                            [
                                Variable("b"),
                            ],
                            Variable("a"),
                        ),
                        Conditional(
                            Constant(2),
                            Body(
                                [
                                    Assignment(
                                        [
                                            Variable("c"),
                                        ],
                                        Constant(3),
                                    ),
                                ]
                            ),
                        ),
                    ]
                ),
            ),
        ]
    )
