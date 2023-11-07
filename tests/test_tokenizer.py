import pytest

from python.tokenizer import Token, Tokenizer, TokenType


@pytest.mark.parametrize(
    ["code", "token"],
    [
        ("+", Token(TokenType.PLUS)),
        ("-", Token(TokenType.MINUS)),
        ("3", Token(TokenType.INT, 3)),
        ("61", Token(TokenType.INT, 61)),
        ("72345", Token(TokenType.INT, 72345)),
        ("9142351643", Token(TokenType.INT, 9142351643)),
        ("642357413455672", Token(TokenType.INT, 642357413455672)),
        ("1.2", Token(TokenType.FLOAT, 1.2)),
        (".12", Token(TokenType.FLOAT, 0.12)),
        ("73.", Token(TokenType.FLOAT, 73.0)),
        ("0.005", Token(TokenType.FLOAT, 0.005)),
        ("123.456", Token(TokenType.FLOAT, 123.456)),
        ("(", Token(TokenType.LPAREN)),
        (")", Token(TokenType.RPAREN)),
        ("*", Token(TokenType.MUL)),
        ("**", Token(TokenType.EXP)),
        ("/", Token(TokenType.DIV)),
        ("%", Token(TokenType.MOD)),
    ],
)
def test_tokenizer_recognises_each_token(code: str, token: Token):
    tokens = list(Tokenizer(code))
    assert tokens == [token, Token(TokenType.EOF)]


@pytest.mark.parametrize(
    ["code", "token"],
    [
        (" 61      ", Token(TokenType.INT, 61)),
        ("    72345    ", Token(TokenType.INT, 72345)),
        ("9142351643", Token(TokenType.INT, 9142351643)),
        ("     642357413455672", Token(TokenType.INT, 642357413455672)),
    ],
)
def test_tokenizer_long_integers(code: str, token: Token):
    tokens = list(Tokenizer(code))
    assert tokens == [token, Token(TokenType.EOF)]


def test_tokenizer_addition():
    tokens = list(Tokenizer("3 + 5"))
    assert tokens == [
        Token(TokenType.INT, 3),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 5),
        Token(TokenType.EOF),
    ]


def test_tokenizer_subtraction():
    tokens = list(Tokenizer("3 - 6"))
    assert tokens == [
        Token(TokenType.INT, 3),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 6),
        Token(TokenType.EOF),
    ]


def test_tokenizer_additions_and_subtractions():
    tokens = list(Tokenizer("1 + 2 + 3 + 4 - 5 - 6 + 7 - 8"))
    assert tokens == [
        Token(TokenType.INT, 1),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 2),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 3),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 4),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 5),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 6),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 7),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 8),
        Token(TokenType.EOF),
    ]


def test_tokenizer_additions_and_subtractions_with_whitespace():
    tokens = list(Tokenizer("     1+       2   +3+4-5  -   6 + 7  - 8        "))
    assert tokens == [
        Token(TokenType.INT, 1),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 2),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 3),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 4),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 5),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 6),
        Token(TokenType.PLUS),
        Token(TokenType.INT, 7),
        Token(TokenType.MINUS),
        Token(TokenType.INT, 8),
        Token(TokenType.EOF),
    ]


def test_tokenizer_raises_error_on_garbage():
    with pytest.raises(RuntimeError):
        list(Tokenizer("$"))


def test_tokenizer_lone_period_is_error():
    # Make sure we don't get a float out of a single period `.`.
    with pytest.raises(RuntimeError):
        list(Tokenizer("  .  "))


def test_tokenizer_parentheses_in_code():
    tokens = list(Tokenizer("( 1 ( 2 ) 3 ( ) 4"))
    assert tokens == [
        Token(TokenType.LPAREN),
        Token(TokenType.INT, 1),
        Token(TokenType.LPAREN),
        Token(TokenType.INT, 2),
        Token(TokenType.RPAREN),
        Token(TokenType.INT, 3),
        Token(TokenType.LPAREN),
        Token(TokenType.RPAREN),
        Token(TokenType.INT, 4),
        Token(TokenType.EOF),
    ]


def test_tokenizer_distinguishes_mul_and_exp():
    tokens = list(Tokenizer("1 * 2 ** 3 * 4 ** 5"))
    assert tokens == [
        Token(TokenType.INT, 1),
        Token(TokenType.MUL),
        Token(TokenType.INT, 2),
        Token(TokenType.EXP),
        Token(TokenType.INT, 3),
        Token(TokenType.MUL),
        Token(TokenType.INT, 4),
        Token(TokenType.EXP),
        Token(TokenType.INT, 5),
        Token(TokenType.EOF),
    ]
