"""
Screept
================

Implements Screept "programming language" in python >3.12
"""
from collections.abc import Mapping
from copy import deepcopy
from typing import Sequence

from lark import Lark, Transformer, v_args, Token
from dataclasses import dataclass


class Expression:
    pass


class Value(Expression):
    pass


class LiteralValue(Value):
    pass


class Identifier:
    pass


@dataclass
class IdentifierLiteral(Identifier):
    value: str


@dataclass
class IdentifierComputed(Identifier):
    value: Expression


@dataclass
class Environment:
    vars: Mapping[str, LiteralValue]


@dataclass
class ExpressionVar(Expression):
    identifier: Identifier


@dataclass
class ValueNumber(LiteralValue):
    value: float


@dataclass
class ValueString(LiteralValue):
    value: str


@dataclass
class ValueFunction(Expression):
    value: Expression


@dataclass
class FuncCall(Expression):
    identifier: str
    args: Sequence[Value]


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
    if_true: Expression
    if_false: Expression


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
        | sum "==" sum      -> comp_equal
    
    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | "FUNC" conditional -> func
         | identifier "(" [conditional ("," conditional)*] ")" -> func_call
         | identifier             -> var
         | "(" conditional ")"
         | STRING           -> string

    ?identifier : NAME 
         | "$[" conditional "]" -> id_computed 
    
    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE
    %import python (STRING)
    %ignore WS_INLINE
"""


@v_args(inline=True)  # Affects the signatures of the methods
class Ast(Transformer):
    @staticmethod
    def number(n):
        return ValueNumber(float(n))

    @staticmethod
    def string(s):
        # Remove quotation marks
        return ValueString(s[1:-1])

    @staticmethod
    def func(n):
        return ValueFunction(n)

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
    def NAME(a: Token) -> Identifier:
        return IdentifierLiteral(a.value)

    @staticmethod
    def id_computed(expr: Expression) -> Identifier:
        return IdentifierComputed(expr)

    @staticmethod
    def mul(a, b):
        return BinaryOp(a, "*", b)

    @staticmethod
    def div(a, b):
        return BinaryOp(a, "/", b)

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


def get_literal_value(v: LiteralValue) -> str | float:
    match v:
        case ValueNumber(x):
            return x
        case ValueString(x):
            return x


def get_identifier_value(i: Identifier, env: Environment) -> str:
    match i:
        case IdentifierLiteral(x):
            return x
        case IdentifierComputed(x):
            return str(evaluate_expression(x, env))


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
            return get_literal_value(env.vars[get_identifier_value(i, env)])
        case UnaryOP(left, op):
            match op:
                case "-": return -evaluate_expression(left)
        case FuncCall(i, args):
            func = env.vars[get_identifier_value(i, env)]
            if isinstance(func, ValueFunction):
                new_env = environment_with_args(env, args)

                return evaluate_expression(func.value, new_env)

            raise Exception
        case ComparisonEqual(left, right):
            if evaluate_expression(left, env) == evaluate_expression(right, env):
                return 1
            else:
                return 0
        case Conditional(cond, if_true, if_false):
            if cond == 0:
                return evaluate_expression(if_false, env)
            else:
                return evaluate_expression(if_true, env)
        case _:
            print("DIDN'T handle", e)


def environment_with_args(env: Environment, args: Sequence[Value]) -> Environment:
    new_env = deepcopy(env)
    for i, arg in enumerate(args):
        new_env.vars['_' + str(i)] = arg
    return new_env


def test():
    env: Environment = Environment({'abc': ValueNumber(66)
                                       , 'fun1': ValueFunction(
            value=BinaryOp(left=ExpressionVar(IdentifierLiteral(value='_0')), op='+',
                           right=ExpressionVar(identifier=IdentifierLiteral(value='_1'))))
                                    })
    # print(calc2("a = 1+2"))
    # expr = "5-1+a*(-3-3)==3?1?3:2:4"
    # expr = """ $[ "a"+"b"+"c"] """
    expr = """fun1(2,3)==5?1:0"""
    print(expr)
    # expr2 = 'abc+4'
    # expr2 = """ $[ "a"+"b"+"c"] + 5 """
    expr2 = """fun1(2,3)==5?1:0"""
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
