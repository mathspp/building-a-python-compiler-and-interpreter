from python.tokenizer import Tokenizer
from python.parser import Parser
from python.compiler import BytecodeType, Compiler
from python.interpreter import Interpreter

import pytest


def test_all_bytecode_types_can_be_interpreted():
    for bct in BytecodeType:
        name = bct.value
        assert hasattr(Interpreter, f"interpret_{name}")


def run_computation(code: str) -> int:
    tokens = list(Tokenizer(code))
    tree = Parser(tokens).parse()
    bytecode = list(Compiler(tree).compile())
    interpreter = Interpreter(bytecode)
    interpreter.interpret()
    return interpreter.last_value_popped


@pytest.mark.parametrize(
    ["code", "result"],
    [
        ("3 + 5", 8),
        ("5 - 2", 3),
        ("1 + 2", 3),
        ("1 - 9", -8),
    ],
)
def test_simple_arithmetic(code: str, result: int):
    assert run_computation(code) == result


@pytest.mark.parametrize(
    ["code", "result"],
    [
        ("103.6 + 5.4", 109),
        ("5.5 - 2", 3.5),
        ("1 + .2", 1.2),
        ("100.0625 - 9.5", 90.5625),
    ],
)
def test_arithmetic_with_floats(code: str, result: int):
    assert run_computation(code) == result


@pytest.mark.parametrize(
    ["code", "result"],
    [
        ("1 + 2 + 3 + 4 + 5", 15),
        ("1 - 2 - 3", -4),
        ("1 - 2 + 3 - 4 + 5 - 6", -3),
    ],
)
def test_sequences_of_additions_and_subtractions(code: str, result: int):
    assert run_computation(code) == result


@pytest.mark.parametrize(
    ["code", "result"],
    [
        ("-3", -3),
        ("+3", 3),
        ("--3", 3),
        ("---3", -3),
        ("----3", 3),
        ("--++-++-+3", 3),
        ("--3 + --3", 6),
    ],
)
def test_unary_operators(code: str, result: int):
    assert run_computation(code) == result


@pytest.mark.parametrize(
    ["code", "result"],
    [
        ("-(3 + 2)", -5),
        ("1 - (2 - 3)", 2),
        ("(((1))) + (2 + (3))", 6),
        ("(2 - 3) - (5 - 6)", 0),
    ],
)
def test_parenthesised_expressions(code: str, result: int):
    assert run_computation(code) == result


@pytest.mark.parametrize(
    ["code", "correct_precedence"],
    [
        ("2 + 3 * 4 + 5", "2 + (3 * 4) + 5"),
        ("2 - 3 * 4 - 5", "2 - (3 * 4) - 5"),
        ("2 + 3 / 5 + 7", "2 + (3 / 5) + 7"),
        ("20 % 4 * 10", "(20 % 4) * 10"),
        ("-2 ** -3", "- (2 ** -3)"),
        ("2 ** 3 * 4", "(2 ** 3) * 4"),
        ("2 * 3 ** 4", "2 * (3 ** 4)"),
        ("5 + 4 % 9", "5 + (4 % 9)"),
    ],
)
def test_arithmetic_operator_precedence(code: str, correct_precedence: str) -> None:
    assert run_computation(code) == run_computation(correct_precedence)


@pytest.mark.parametrize(
    ["code", "result"],
    [
        ("4 % 5 % 3", 1),
        ("2 * 3 * 4", 24),
        ("-2 ** 10", -1024),
        ("2 / 2 / 1", 1.0),
        ("2 + 3 * 4 ** 5 - 6 % 7 / 8", 3073.25),
    ],
)
def test_all_arithmetic_operators(code: str, result: int | float) -> None:
    assert run_computation(code) == result
