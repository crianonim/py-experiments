"""
Screept
================

Implements Screept "programming language" in python >3.12
"""
from collections.abc import Mapping
from typing import Sequence

from lark import Lark, Transformer, v_args
from dataclasses import dataclass


class Expression:
    pass


class Value(Expression):
    pass


class LiteralValue(Value):
    pass


@dataclass
class Environment:
    vars: Mapping[str, LiteralValue]


@dataclass
class ExpressionVar(Expression):
    identifier: str


@dataclass
class ValueNumber(LiteralValue):
    value: float


@dataclass
class ValueString(LiteralValue):
    value: str


@dataclass
class FuncCall(Expression):
    identifier: str
    values: Sequence[Value]


@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression


@dataclass
class UnaryOP(Expression):
    left: Value
    op: str


@dataclass
class Conditional(Expression):
    cond: Expression
    ifTrue: Expression
    ifFalse: Expression


@dataclass
class ComparisonEqual(Expression):
    left: Expression
    right: Expression


calc_grammar = """
    ?start: conditional

    ?conditional : comparison "?" comparison ":" conditional ->  conditional
        | comparison "?" conditional ":" conditional ->  conditional
        | comparison
    
    ?comparison : sum
        | sum "==" sum -> comp_equal
    
    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | NAME "(" [conditional ("," conditional)*] ")" -> func_call
         | NAME             -> var
         | "(" conditional ")"
         | STRING           -> string

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE
    %import python (STRING)
    %ignore WS_INLINE
"""


@v_args(inline=True)  # Affects the signatures of the methods
class Ast(Transformer):

    @staticmethod
    def string(s):
        # Remove quotation marks
        return ValueString(s[1:-1])

    @staticmethod
    def var(name):
        return ExpressionVar(name)

    @staticmethod
    def func_call(identifier, *values):
        return FuncCall(identifier, values)

    @staticmethod
    def add(a, b):
        return BinaryOp(a, "+", b)

    @staticmethod
    def sub(a, b):
        return BinaryOp(a, "-", b)

    @staticmethod
    def mul(a, b):
        return BinaryOp(a, "*", b)

    @staticmethod
    def div(a, b):
        return BinaryOp(a, "/", b)

    @staticmethod
    def number(n):
        return ValueNumber(float(n))

    @staticmethod
    def neg(n):
        return UnaryOP(n, "-")

    @staticmethod
    def conditional(*args):
        return Conditional(*args)

    @staticmethod
    def comp_equal(left, right):
        return ComparisonEqual(left, right)


calc_parser2 = Lark(calc_grammar, parser='lalr', transformer=Ast())
calc2 = calc_parser2.parse


def main():
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        print(calc2(s))


def getLiteralValue(v: LiteralValue) -> str | float:
    match v:
        case ValueNumber(x):
            return x
        case ValueString(x):
            return x


def evaluate_expression(e: Expression, env: Environment):
    match e:
        case ValueNumber(v):
            return v
        case ValueString(v):
            return v
        case BinaryOp(left, op, right):
            from operator import add, sub, mul, truediv
            match op:
                case "+":
                    binary = add
                case "-":
                    binary = sub
                case "*":
                    binary = mul
                case "/":
                    binary = truediv
                case _:
                    raise Exception
            return binary(evaluate_expression(left, env), evaluate_expression(right, env))
        case ExpressionVar(i):
            return getLiteralValue(env.vars[i])
        case UnaryOP(left, op):
            match op:
                case "-": return -evaluate_expression(left)


def test():
    env: Environment = Environment({'abc': ValueNumber(66)})
    # print(calc2("a = 1+2"))
    # expr = "5-1+a*(-3-3)==3?1?3:2:4"
    expr = "a(12,33)"

    expr2 = 'abc+4'
    parsed3 = calc2(expr2)
    print("S", parsed3)
    print("EV", evaluate_expression(parsed3, env))
    parsed = calc2(expr)
    parsed2 = Lark(calc_grammar, parser='lalr').parse(expr)
    print(parsed)
    print(parsed2.pretty())


if __name__ == '__main__':
    test()
    # main()
