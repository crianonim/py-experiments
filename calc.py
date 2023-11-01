"""
Basic calculator
================

A simple example of a REPL calculator

This example shows how to write a basic calculator with variables.
"""
from lark import Lark, Transformer, v_args
from dataclasses import dataclass


class Value:
    pass


class Expression:
    pass


class LiteralValue(Expression):
    pass


@dataclass
class ExpressionVar(Expression):
    identifier: str


@dataclass
class ValueNumber(LiteralValue):
    value: float


@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression


@dataclass
class UnaryOP(Expression):
    left: Value
    op: str


calc_grammar = """
    ?start: sum

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | NAME             -> var
         | "(" sum ")"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
"""


@v_args(inline=True)    # Affects the signatures of the methods
class CalculateTree(Transformer):

    number = float

    def __init__(self):
        self.vars = {}

    def assign_var(self, name, value):
        self.vars[name] = value
        return value

    def var(self, name):
        try:
            return self.vars[name]
        except KeyError:
            raise Exception("Variable not found: %s" % name)


@v_args(inline=True)    # Affects the signatures of the methods
class CalculateTree2(Transformer):
    # from operator import add, sub, mul, truediv as div, neg

    def __init__(self):
        self.vars = {}

    # def assign_var(self, name, value):
    #     self.vars[name] = value
    #     return value

    def var(self, name):
        return ExpressionVar(name)

    def add(self, a, b):
        return BinaryOp(a, "+", b)

    def sub(self, a, b):
        return BinaryOp(a, "-", b)

    def mul(self, a, b):
        return BinaryOp(a, "*", b)

    def number(self, n):
        return ValueNumber(float(n))

    def neg(self, n):
        return UnaryOP(n, "-")


calc_parser = Lark(calc_grammar, parser='lalr', transformer=CalculateTree())
calc_parser2 = Lark(calc_grammar, parser='lalr', transformer=CalculateTree2())
calc = calc_parser.parse
calc2 = calc_parser2.parse


def main():
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        print(calc2(s))


def evaluateExpression(e: Expression):
    if type(e) == ValueNumber:
        return e.value
    if type(e) == BinaryOp:
        if e.op == "+":
            return evaluateExpression(e.left)+evaluateExpression(e.right)
        if e.op == "-":
            return evaluateExpression(e.left)-evaluateExpression(e.right)
        if e.op == "*":
            return evaluateExpression(e.left)*evaluateExpression(e.right)
    if type(e) == UnaryOP:
        if e.op == "-":
            return -evaluateExpression(e.left)
    if type(e) == ExpressionVar:
        return 1


def test():
    # print(calc2("a = 1+2"))
    expr = "5-1+a*-3"
    parsed = calc2(expr)
    parsed2 = Lark(calc_grammar, parser='lalr').parse(expr)
    print(parsed)
    print(evaluateExpression(parsed))
    print(parsed2.pretty())


if __name__ == '__main__':
    test()
    # main()
