from dataclasses import dataclass

from .tokenizer import Token, TokenType


@dataclass
class TreeNode:
    pass


@dataclass
class Expr(TreeNode):
    pass


@dataclass
class UnaryOp(Expr):
    op: str
    value: Expr


@dataclass
class BinOp(Expr):
    op: str
    left: Expr
    right: Expr


@dataclass
class Int(Expr):
    value: int


@dataclass
class Float(Expr):
    value: float


def print_ast(tree: TreeNode, depth: int = 0) -> None:
    indent = "    " * depth
    node_name = tree.__class__.__name__
    match tree:
        case UnaryOp(op, value):
            print(f"{indent}{node_name}(\n{indent}    {op!r},")
            print_ast(value, depth + 1)
            print(f",\n{indent})", end="")
        case BinOp(op, left, right):
            print(f"{indent}{node_name}(\n{indent}    {op!r},")
            print_ast(left, depth + 1)
            print(",")
            print_ast(right, depth + 1)
            print(f",\n{indent})", end="")
        case Int(value) | Float(value):
            print(f"{indent}{node_name}({value!r})", end="")
        case _:
            raise RuntimeError(f"Can't print a node of type {node_name}")
    if depth == 0:
        print()


class Parser:
    """
    program := computation
    computation := unary ( (PLUS | MINUS) unary )*
    unary := PLUS unary | MINUS unary | number
    number := INT | FLOAT
    """

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.next_token_index: int = 0
        """Points to the next token to be consumed."""

    def eat(self, expected_token_type: TokenType) -> Token:
        """Returns the next token if it is of the expected type.

        If the next token is not of the expected type, this raises an error.
        """
        next_token = self.tokens[self.next_token_index]
        self.next_token_index += 1
        if next_token.type != expected_token_type:
            raise RuntimeError(f"Expected {expected_token_type}, ate {next_token!r}.")
        return next_token

    def peek(self, skip: int = 0) -> TokenType | None:
        """Checks the type of an upcoming token without consuming it."""
        peek_at = self.next_token_index + skip
        return self.tokens[peek_at].type if peek_at < len(self.tokens) else None

    def parse_number(self) -> Int | Float:
        """Parses an integer or a float."""
        if self.peek() == TokenType.INT:
            return Int(self.eat(TokenType.INT).value)
        else:
            return Float(self.eat(TokenType.FLOAT).value)

    def parse_unary(self) -> Expr:
        """Parses an unary operator."""
        if (next_token_type := self.peek()) in {TokenType.PLUS, TokenType.MINUS}:
            op = "+" if next_token_type == TokenType.PLUS else "-"
            self.eat(next_token_type)
            value = self.parse_unary()
            return UnaryOp(op, value)
        else:  # No unary operators in sight.
            return self.parse_number()

    def parse_computation(self) -> Expr:
        """Parses a computation."""
        result: Expr
        result = self.parse_unary()

        while (next_token_type := self.peek()) in {TokenType.PLUS, TokenType.MINUS}:
            op = "+" if next_token_type == TokenType.PLUS else "-"
            self.eat(next_token_type)
            right = self.parse_unary()
            result = BinOp(op, result, right)

        return result

    def parse(self) -> Expr:
        """Parses the program."""
        computation = self.parse_computation()
        self.eat(TokenType.EOF)
        return computation


if __name__ == "__main__":
    from .tokenizer import Tokenizer

    code = "--++3.5 - 2"
    parser = Parser(list(Tokenizer(code)))
    print_ast(parser.parse())
