"""
Screept
================

Implements Screept "programming language" in python >3.12
"""
import random
from collections.abc import Mapping,MutableMapping
from copy import deepcopy
from math import floor
from pprint import pprint
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
class ExpressionVar(Expression):
    identifier: Identifier


@dataclass
class ValueNumber(LiteralValue):
    value: float


@dataclass
class ValueString(LiteralValue):
    value: str


@dataclass
class ValueFunction(LiteralValue):
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


grammar = """
    ?statement: "PRINT" expression                      -> stmt_print
        | "{" [statement (";" statement)*] ";"? "}"     -> stmt_block
        | identifier "=" expression                     -> stmt_bind
        | "PROC" identifier statement                   -> stmt_proc_def
        | "RUN" identifier  "(" [expression ("," expression)*] ")"    -> stmt_proc_run
        | "RND" identifier expression expression        -> stmt_rnd
    
    # expressions
    
    ?expression: conditional
    
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
    %import common.WS
    %import python (STRING)
    %ignore WS
"""


class Statement:
    pass


@dataclass
class Environment:
    vars: MutableMapping[str, LiteralValue]
    procedures: MutableMapping[str, Statement]
    output: list[str]


@dataclass
class StmtPrint(Statement):
    expression: Expression


@dataclass
class StmtBlock(Statement):
    statements: Sequence[Statement]


@dataclass
class StmtBind(Statement):
    identifier: Identifier
    expression: Expression


@dataclass
class StmtProcDef(Statement):
    identifier: Identifier
    statement: Statement


@dataclass
class StmtProcRun(Statement):
    identifier: Identifier
    args: Sequence[Expression]


@dataclass
class StmtRnd(Statement):
    identifier: Identifier
    minVal: Expression
    maxVal: Expression


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

    @staticmethod
    def stmt_print(e):
        return StmtPrint(e)

    @staticmethod
    def stmt_block(*l):
        return StmtBlock(l)

    @staticmethod
    def stmt_bind(i, expr):
        return StmtBind(i, expr)

    @staticmethod
    def stmt_proc_def(i, stmt):
        return StmtProcDef(i, stmt)

    @staticmethod
    def stmt_proc_run(i, *args):
        if args == (None,):
            return StmtProcRun(i, tuple())
        return StmtProcRun(i, args)

    @staticmethod
    def stmt_rnd(i, minVal, maxVal):
        return StmtRnd(i, minVal, maxVal)


stmt_parser = Lark(grammar, parser='lalr', start='statement', transformer=Ast())
expr_parser = Lark(grammar, parser='lalr', start='expression', transformer=Ast())


#

def main():
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        print(expr_parser.parse(s))


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


def get_string_value(v: LiteralValue) -> str:
    match v:
        case ValueNumber(n):
            return str(n)
        case ValueString(t):
            return t
        case ValueFunction(f):
            # TODO
            return "FUNC"

def get_numerical_value(v: LiteralValue)-> float:
    match v:
        case ValueNumber(n):
            return n
        case _ : return 0
def evaluate_expression(e: Expression, env: Environment) -> LiteralValue:
    match e:
        case ValueNumber(v):
            return ValueNumber(v)
        case ValueString(v):
            return ValueString(v)
        case ValueFunction(v):
            return ValueFunction(v)
        case BinaryOp(left, op, right):
            from operator import sub, mul, truediv
            match op:
                case "+":
                    l = evaluate_expression(left, env)
                    r = evaluate_expression(right, env)
                    match (l, r):
                        case (ValueNumber(ll), ValueNumber(rr)):
                            return ValueNumber(ll + rr)
                        case _:
                            return ValueString(get_string_value(l) + get_string_value(r))

                case "-":
                    binary = sub
                case "*":
                    binary = mul
                case "/":
                    binary = truediv
                case _:
                    raise Exception

            return ValueNumber(binary(evaluate_expression(left, env), evaluate_expression(right, env)))
        case ExpressionVar(i):

            return env.vars[get_identifier_value(i, env)]
        case UnaryOP(left, op):
            match op:
                case "-": return ValueNumber(-evaluate_expression(left).value)
        case FuncCall(i, args):
            func = env.vars[get_identifier_value(i, env)]
            if isinstance(func, ValueFunction):
                new_env = environment_with_args(env, args)

                return evaluate_expression(func.value, new_env)

            raise Exception
        case ComparisonEqual(left, right):
            if evaluate_expression(left, env) == evaluate_expression(right, env):
                return ValueNumber(1)
            else:
                return ValueNumber(0)
        case Conditional(cond, if_true, if_false):
            ec = evaluate_expression(cond, env)
            if ec == ValueNumber(0):
                return evaluate_expression(if_false, env)
            else:
                return evaluate_expression(if_true, env)
        case _:
            print("DIDN'T handle", e)


def environment_with_args(env: Environment, args: Sequence[Value]) -> Environment:
    new_env = deepcopy(env)
    for i, arg in enumerate(args):
        new_env.vars['_' + str(i)] = evaluate_expression(arg, env)
    return new_env


def run_statement(s: Statement, env: Environment) -> None:
    match s:
        case StmtPrint(e):
            res = evaluate_expression(e, env)
            env.output.append(get_string_value(res))
            print("PRINT ", evaluate_expression(e, env))
        case StmtBind(i, e):
            v = evaluate_expression(e, env)
            env.vars[get_identifier_value(i, env)] = v
            print("NE", env)
        case StmtBlock(ss):
            for st in ss:
                run_statement(st, env)
        case StmtProcDef(i, stmt):
            env.procedures[get_identifier_value(i, env)] = stmt
        case StmtProcRun(i, args):
            stmt = env.procedures[get_identifier_value(i, env)]
            for i, arg in enumerate(args):
                env.vars['_' + str(i)] = evaluate_expression(arg, env)

            run_statement(stmt, env)
        case StmtRnd(i,minVal,maxVal):
            min_v=get_numerical_value(evaluate_expression(minVal,env))
            max_v=get_numerical_value(evaluate_expression(maxVal,env))

            env.vars[get_identifier_value(i, env)] = ValueNumber(random.randint(floor(min_v),floor(max_v)))
        case _:
            raise Exception("unknown statement")



def test():
    env: Environment = Environment({'abc': ValueNumber(66)
                                    , 'fun1': ValueFunction(
            BinaryOp(ExpressionVar(IdentifierLiteral('_0')), '+',
                           ExpressionVar(IdentifierLiteral('_1'))))
                                    },
                                   {},
                                   [])
    # print(calc2("a = 1+2"))
    # expr = "5-1+a*(-3-3)==3?1?3:2:4"
    # expr = """ $[ "a"+"b"+"c"] """
    expr = """fun1(2,3)==5?1:0"""
    print(expr)
    # expr2 = 'abc+4'
    # expr2 = """ $[ "a"+"b"+"c"] + 5 """
    expr2 = """fun1(2,3)==6?1:0"""
    # parsed3 = calc2(expr2)
    parsed3 = expr_parser.parse(expr2)

    print("S", parsed3)
    print("EV", evaluate_expression(parsed3, env))
    parsed = expr_parser.parse(expr)
    # parsed2 = Lark('  ?start: conditional\n'+expression_grammar, parser='lalr').parse(expr)
    print(parsed)
    s1 = """{ g=FUNC _0 + _1;
    PROC janowa { PRINT _0 ; a66=5 };
    RUN janowa("X");
     PRINT g(5,a66); PRINT g(5,6)==10 ? "Jan" : "Test" ;
     a66=a66+2;
     PRINT a66;
     RND xx 2 10;
     PRINT xx
     }"""
    sp1 = stmt_parser.parse(s1)
    print(sp1)
    run_statement(sp1, env)
    pprint(env)
    # print(parsed2.pretty())
    # s1 = stmt_parser.parse()


if __name__ == '__main__':
    test()
    # main()
