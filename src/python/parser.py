from dataclasses import dataclass

from .tokenizer import Token, TokenType


@dataclass
class TreeNode:
    pass


@dataclass
class BinOp(TreeNode):
    op: str
    left: "Int | Float"
    right: "Int | Float"


@dataclass
class Int(TreeNode):
    value: int


@dataclass
class Float(TreeNode):
    value: float


def print_ast(tree: TreeNode, depth: int = 0) -> None:
    indent = "    " * depth
    match tree:
        case BinOp(op, left, right):
            print(indent + op)
            print_ast(left, depth + 1)
            print_ast(right, depth + 1)
        case Int(value) | Float(value):
            print(indent + str(value))
        case _:
            raise RuntimeError(f"Can't print a node of type {tree.__class__.__name__}")


class Parser:
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

    def parse_computation(self) -> BinOp:
        """Parses a computation."""
        left = self.parse_number()

        if self.peek() == TokenType.PLUS:
            op = "+"
            self.eat(TokenType.PLUS)
        else:
            op = "-"
            self.eat(TokenType.MINUS)

        right = self.parse_number()

        return BinOp(op, left, right)

    def parse(self) -> BinOp:
        """Parses the program."""
        computation = self.parse_computation()
        self.eat(TokenType.EOF)
        return computation


if __name__ == "__main__":
    from .tokenizer import Tokenizer

    code = "3 + 5"
    parser = Parser(list(Tokenizer(code)))
    print_ast(parser.parse())
