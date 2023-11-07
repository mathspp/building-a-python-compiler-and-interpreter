from python.parser import Parser
from python.parser import BinOp, Float, Int, UnaryOp
from python.tokenizer import Token, Tokenizer, TokenType

import pytest


def test_parsing_addition():
    tokens = [
        Token(TokenType.INT, 3),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 5),
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
    assert tree == BinOp(
        "+",
        Int(3),
        Int(5),
    )


def test_parsing_subtraction():
    tokens = [
        Token(TokenType.INT, 5),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 2),
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
    assert tree == BinOp(
        "-",
        Int(5),
        Int(2),
    )


def test_parsing_addition_with_floats():
    tokens = [
        Token(TokenType.FLOAT, 0.5),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 5),
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
    assert tree == BinOp(
        "+",
        Float(0.5),
        Int(5),
    )


def test_parsing_subtraction_with_floats():
    tokens = [
        Token(TokenType.FLOAT, 5.0),
        Token(TokenType.MINUS),
        Token(TokenType.FLOAT, 0.2),
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
    assert tree == BinOp(
        "-",
        Float(5.0),
        Float(0.2),
    )


def test_parsing_single_integer():
    tokens = [
        Token(TokenType.INT, 3),
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
    assert tree == Int(3)


def test_parsing_single_float():
    tokens = [
        Token(TokenType.FLOAT, 3.0),
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
    assert tree == Float(3.0)


def test_parsing_addition_then_subtraction():
    tokens = [
        Token(TokenType.INT, 3),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 5),
        Token(TokenType.MINUS),
        Token(TokenType.FLOAT, 0.2),
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
    assert tree == BinOp(
        "-",
        BinOp(
            "+",
            Int(3),
            Int(5),
        ),
        Float(0.2),
    )


def test_parsing_subtraction_then_addition():
    tokens = [
        Token(TokenType.INT, 3),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 5),
        Token(TokenType.PLUS),
        Token(TokenType.FLOAT, 0.2),
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
    assert tree == BinOp(
        "+",
        BinOp(
            "-",
            Int(3),
            Int(5),
        ),
        Float(0.2),
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
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
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


def test_parsing_unary_minus():
    tokens = [
        Token(TokenType.MINUS),
        Token(TokenType.INT, 3),
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
    assert tree == UnaryOp("-", Int(3))


def test_parsing_unary_plus():
    tokens = [
        Token(TokenType.PLUS),
        Token(TokenType.FLOAT, 3.0),
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
    assert tree == UnaryOp("+", Float(3))


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
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
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
                        Float(3.5),
                    ),
                ),
            ),
        ),
        Int(2),
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
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
    assert tree == BinOp(
        "+",
        Int(1),
        BinOp(
            "+",
            Int(2),
            Int(3),
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
        Token(TokenType.EOF),
    ]
    tree = Parser(tokens).parse()
    assert tree == BinOp(
        "+",
        Int(1),
        BinOp(
            "+",
            Int(2),
            Int(3),
        ),
    )


@pytest.mark.parametrize(
    "code",
    [
        "(1",
        "()",
        ") 1 + 2",
        "1 + 2)",
        "1 (+) 2",
        "1 + )2(",
    ],
)
def test_unbalanced_parentheses(code: str):
    tokens = list(Tokenizer(code))
    with pytest.raises(RuntimeError):
        Parser(tokens).parse()
