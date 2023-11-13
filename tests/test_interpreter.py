from typing import Any

from python.tokenizer import Tokenizer
from python.parser import Parser
from python.compiler import BytecodeType, Compiler
from python.interpreter import Interpreter

import pytest


def test_all_bytecode_types_can_be_interpreted():
    for bct in BytecodeType:
        name = bct.value
        assert hasattr(Interpreter, f"interpret_{name}")


def _run(code: str) -> Interpreter:
    tokens = list(Tokenizer(code))
    tree = Parser(tokens).parse()
    bytecode = list(Compiler(tree).compile())
    interpreter = Interpreter(bytecode)
    interpreter.interpret()
    return interpreter


def run_expr(code: str) -> Any:
    return _run(code).last_value_popped


def run_get_scope(code: str) -> dict[str, Any]:
    return _run(code).scope


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
    assert run_expr(code) == result


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
    assert run_expr(code) == result


@pytest.mark.parametrize(
    ["code", "result"],
    [
        ("1 + 2 + 3 + 4 + 5", 15),
        ("1 - 2 - 3", -4),
        ("1 - 2 + 3 - 4 + 5 - 6", -3),
    ],
)
def test_sequences_of_additions_and_subtractions(code: str, result: int):
    assert run_expr(code) == result


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
    assert run_expr(code) == result


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
    assert run_expr(code) == result


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
def test_arithmetic_operator_precedence(code: str, correct_precedence: str):
    assert run_expr(code) == run_expr(correct_precedence)


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
def test_all_arithmetic_operators(code: str, result: int | float):
    assert run_expr(code) == result


def test_simple_assignment():
    code = "a = 3"
    scope = run_get_scope(code)
    assert len(scope) == 1
    assert scope["a"] == 3


def test_overriding_assignment():
    code = "a = 3\na = 4\na = 5"
    scope = run_get_scope(code)
    assert len(scope) == 1
    assert scope["a"] == 5


def test_multiple_assignment_statements():
    code = "a = 1\nb = 2\na = 3\nc = 4\na = 5"
    scope = run_get_scope(code)
    assert len(scope) == 3
    assert scope["a"] == 5
    assert scope["b"] == 2
    assert scope["c"] == 4


@pytest.mark.parametrize(
    ["code", "scope"],
    [
        ("a = 1\nb = 1\nc = a + b", {"a": 1, "b": 1, "c": 2}),
        ("a = 1\nb = a\nc = b\na = 3", {"a": 3, "b": 1, "c": 1}),
        ("a = b = c = 3", {"a": 3, "b": 3, "c": 3}),
    ],
)
def test_assignments_and_references(code: str, scope: dict[str, Any]):
    assert scope == run_get_scope(code)


def test_flat_conditionals():
    code = """
if 1:
    a = 1
    b = 1
if 0:
    a = 20
    b = 20

if a:
    c = 11 - 10
"""

    assert run_get_scope(code) == {"a": 1, "b": 1, "c": 1}


def test_nested_conditionals():
    code = """
if 1:
    if 1:
        a = 1

        if 0:
            c = 1

    if a:
        b = 1

    if 5 - 5:
        c = 1
"""

    assert run_get_scope(code) == {"a": 1, "b": 1}


def test_booleans():
    code = """
if True:
    a = 73

if False:
    b = 73
"""

    assert run_get_scope(code) == {"a": 73}


@pytest.mark.parametrize(
    ["code", "result"],
    [
        ("not True", False),
        ("not not True", True),
        ("not not not True", False),
        ("not not not not True", True),
        ("not False", True),
        ("not not False", False),
        ("not not not False", True),
        ("not not not not False", False),
    ],
)
def test_not(code: str, result: bool):
    assert run_expr(code) == result
