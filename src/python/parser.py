from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .tokenizer import Token, TokenType


@dataclass
class TreeNode:
    pass


@dataclass
class Program(TreeNode):
    statements: list[Statement]


@dataclass
class Statement(TreeNode):
    pass


@dataclass
class Assignment(Statement):
    targets: list[Variable]
    value: Expr


@dataclass
class ExprStatement(Statement):
    expr: Expr


@dataclass
class Conditional(Statement):
    condition: Expr
    body: Body
    orelse: Body | None = None


@dataclass
class Body(TreeNode):
    statements: list[Statement]


@dataclass
class Expr(TreeNode):
    pass


@dataclass
class BoolOp(Expr):
    op: str
    values: list[Expr]


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
class Variable(Expr):
    name: str


@dataclass
class Constant(Expr):
    value: bool | float | int


def print_ast(
    obj: TreeNode | list[Any] | Any, depth: int = 0, prefix: str = ""
) -> None:
    indent = "    " * depth
    obj_name = obj.__class__.__name__
    if isinstance(obj, TreeNode):
        items = list(vars(obj).items())
        if not items:
            print(f"{indent}{prefix}{obj_name}()", end="")
        elif len(items) == 1 and not isinstance(items[0][1], (TreeNode, list)):
            print(f"{indent}{prefix}{obj_name}({items[0][1]!r})", end="")
        else:
            print(f"{indent}{prefix}{obj_name}(")
            for key, value in items:
                print_ast(value, depth + 1, f"{key}=")
                print(",")
            print(f"{indent})", end="")
    elif isinstance(obj, list) and obj and isinstance(obj[0], TreeNode):
        print(f"{indent}{prefix}[")
        for value in obj:
            print_ast(value, depth + 1)
            print(",")
        print(f"{indent}]", end="")
    else:
        print(f"{indent}{prefix}{obj!r}", end="")

    if not depth:
        print()


class Parser:
    """
    program := statement* EOF

    statement := expr_statement | assignment | conditional

    expr_statement := expr NEWLINE
    assignment := ( NAME ASSIGN )+ expr NEWLINE
    conditional := if_statement ( elif_statement )* else_statement?

    if_statement := IF expr COLON NEWLINE body
    elif_statement := ELIF expr COLON NEWLINE body
    else_statement := ELSE COLON NEWLINE body

    body := INDENT statement+ DEDENT

    expr := alternative
    alternative := conjunction ( OR conjunction )*
    conjunction := negation ( AND negation ) *
    negation := NOT negation | computation
    computation := term ( (PLUS | MINUS) term )*
    term := unary ( (MUL | DIV | MOD) unary )*
    unary := PLUS unary | MINUS unary | exponentiation
    exponentiation := atom EXP unary | atom
    atom := LPAREN expr RPAREN | value
    value := NAME | INT | FLOAT | TRUE | FALSE
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

    def parse_value(self) -> Variable | Constant:
        """Parses an integer or a float."""
        next_token_type = self.peek()
        if next_token_type == TokenType.NAME:
            return Variable(self.eat(TokenType.NAME).value)
        elif next_token_type in {TokenType.INT, TokenType.FLOAT}:
            return Constant(self.eat(next_token_type).value)
        elif next_token_type in {TokenType.TRUE, TokenType.FALSE}:
            self.eat(next_token_type)
            return Constant(next_token_type == TokenType.TRUE)
        else:
            raise RuntimeError(f"Can't parse {next_token_type} as a value.")

    def parse_atom(self) -> Expr:
        """Parses a parenthesised expression or a number."""
        if self.peek() == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            result = self.parse_expr()
            self.eat(TokenType.RPAREN)
        else:
            result = self.parse_value()
        return result

    def parse_exponentiation(self) -> Expr:
        """Parses an exponentiation operator."""
        result = self.parse_atom()
        if self.peek() == TokenType.EXP:
            self.eat(TokenType.EXP)
            result = BinOp("**", result, self.parse_unary())
        return result

    def parse_unary(self) -> Expr:
        """Parses an unary operator."""
        if (next_token_type := self.peek()) in {TokenType.PLUS, TokenType.MINUS}:
            op = "+" if next_token_type == TokenType.PLUS else "-"
            self.eat(next_token_type)
            value = self.parse_unary()
            return UnaryOp(op, value)
        else:  # No unary operators in sight.
            return self.parse_exponentiation()

    def parse_term(self) -> Expr:
        """Parses an expression with multiplications, divisions, and modulo operations."""
        result: Expr
        result = self.parse_unary()

        TYPES_TO_OPS = {
            TokenType.MUL: "*",
            TokenType.DIV: "/",
            TokenType.MOD: "%",
        }
        while (next_token_type := self.peek()) in TYPES_TO_OPS:
            op = TYPES_TO_OPS[next_token_type]
            self.eat(next_token_type)
            right = self.parse_unary()
            result = BinOp(op, result, right)

        return result

    def parse_computation(self) -> Expr:
        """Parses addition and subtraction computations."""
        result: Expr
        result = self.parse_term()

        while (next_token_type := self.peek()) in {TokenType.PLUS, TokenType.MINUS}:
            op = "+" if next_token_type == TokenType.PLUS else "-"
            self.eat(next_token_type)
            right = self.parse_term()
            result = BinOp(op, result, right)

        return result

    def parse_negation(self) -> Expr:
        """Parses a Boolean negation."""
        if self.peek() == TokenType.NOT:
            self.eat(TokenType.NOT)
            return UnaryOp("not", self.parse_negation())
        else:
            return self.parse_computation()

    def parse_conjunction(self) -> Expr:
        """Parses a Boolean conjunction (and)."""
        values: list[Expr] = [self.parse_negation()]

        while self.peek() == TokenType.AND:
            self.eat(TokenType.AND)
            values.append(self.parse_negation())

        return values[0] if len(values) == 1 else BoolOp("and", values)

    def parse_alternative(self) -> Expr:
        """Parses a Boolean alternative (or)."""
        values: list[Expr] = [self.parse_conjunction()]

        while self.peek() == TokenType.OR:
            self.eat(TokenType.OR)
            values.append(self.parse_conjunction())

        return values[0] if len(values) == 1 else BoolOp("or", values)

    def parse_expr(self) -> Expr:
        """Parses a full expression."""
        return self.parse_alternative()

    def parse_expr_statement(self) -> ExprStatement:
        """Parses a standalone expression."""
        expr = ExprStatement(self.parse_expr())
        self.eat(TokenType.NEWLINE)
        return expr

    def parse_assignment(self) -> Assignment:
        """Parses an assignment."""
        first = True
        targets: list[Variable] = []
        while first or self.peek(skip=1) == TokenType.ASSIGN:
            first = False
            name_token = self.eat(TokenType.NAME)
            self.eat(TokenType.ASSIGN)
            targets.append(Variable(name_token.value))

        value = self.parse_expr()
        self.eat(TokenType.NEWLINE)
        return Assignment(targets, value)

    def parse_body(self) -> Body:
        """Parses the body of a compound statement."""
        self.eat(TokenType.INDENT)
        body = Body([])
        while self.peek() != TokenType.DEDENT:
            body.statements.append(self.parse_statement())
        self.eat(TokenType.DEDENT)
        return body

    def parse_else_statement(self) -> Body:
        """Parses an `else` statement and returns its body."""
        self.eat(TokenType.ELSE)
        self.eat(TokenType.COLON)
        self.eat(TokenType.NEWLINE)
        body = self.parse_body()
        return body

    def parse_elif_statement(self) -> Conditional:
        """Parses an `elif` conditional and returns it."""
        self.eat(TokenType.ELIF)
        condition = self.parse_expr()
        self.eat(TokenType.COLON)
        self.eat(TokenType.NEWLINE)
        body = self.parse_body()
        return Conditional(condition, body)

    def parse_if_statement(self) -> Conditional:
        """Parses an `if` conditional and returns it."""
        self.eat(TokenType.IF)
        condition = self.parse_expr()
        self.eat(TokenType.COLON)
        self.eat(TokenType.NEWLINE)
        body = self.parse_body()
        return Conditional(condition, body)

    def parse_conditional(self) -> Conditional:
        """Parses a conditional block."""
        top_conditional = self.parse_if_statement()

        innermost_conditional = top_conditional
        while self.peek() == TokenType.ELIF:
            elif_statement = self.parse_elif_statement()
            innermost_conditional.orelse = Body([elif_statement])
            innermost_conditional = elif_statement
        if self.peek() == TokenType.ELSE:
            else_statement = self.parse_else_statement()
            innermost_conditional.orelse = else_statement

        return top_conditional

    def parse_statement(self) -> Statement:
        """Parses a statement."""
        if self.peek(skip=1) == TokenType.ASSIGN:
            return self.parse_assignment()
        elif self.peek() == TokenType.IF:
            return self.parse_conditional()
        else:
            return self.parse_expr_statement()

    def parse(self) -> Program:
        """Parses the program."""
        program = Program([])
        while self.peek() != TokenType.EOF:
            program.statements.append(self.parse_statement())
        self.eat(TokenType.EOF)
        return program


if __name__ == "__main__":
    import sys
    from .tokenizer import Tokenizer

    code = sys.argv[1]
    parser = Parser(list(Tokenizer(code)))
    tree = parser.parse()
    print_ast(tree)
