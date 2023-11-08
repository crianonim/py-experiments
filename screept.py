"""
Screept
================

Implements Screept "programming language" in python >3.12
"""
import random
from collections.abc import MutableMapping, Callable
from copy import deepcopy
from math import floor
from pprint import pprint
from typing import Sequence, override, Optional
from abc import ABC, abstractmethod
from lark import Lark, Transformer, v_args, Token, tree
from dataclasses import dataclass


class Expression:
    pass


class ExprLiteralValue(Expression):
    pass


class Value(ExprLiteralValue, ABC):
    @abstractmethod
    def get_string(self) -> str:
        pass

    @abstractmethod
    def get_number(self) -> float:
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
class ValueNumber(Value):
    value: float

    @override
    def get_string(self) -> str:
        return str(self.value)

    @override
    def get_number(self) -> float:
        return self.value


@dataclass
class ValueString(Value):
    value: str

    @override
    def get_string(self) -> str:
        return self.value

    @override
    def get_number(self) -> float:
        return 1


@dataclass
class ValueFunction(Value):
    value: Expression

    @override
    def get_string(self) -> str:
        return "<FUNC>"

    @override
    def get_number(self) -> float:
        return 1


@dataclass
class ExprFuncCall(Expression):
    identifier: Identifier
    args: Sequence[ExprLiteralValue]


@dataclass
class ExprBinaryOp(Expression):
    left: Expression
    op: str
    right: Expression


@dataclass
class ExprUnaryOP(Expression):
    left: ExprLiteralValue
    op: str


@dataclass
class ExprConditional(Expression):
    cond: Expression
    if_true: Expression
    if_false: Expression


@dataclass
class ExprComparisonEqual(Expression):
    left: Expression
    right: Expression


@dataclass
class ExprComparisonLess(Expression):
    left: Expression
    right: Expression


@dataclass
class ExprComparisonMore(Expression):
    left: Expression
    right: Expression


grammar = """
    ?statement: "PRINT" expression                      -> stmt_print
        | "{" [statement (";" statement)*] ";"? "}"     -> stmt_block
        | identifier "=" expression                     -> stmt_bind
        | "PROC" identifier statement                   -> stmt_proc_def
        | "RUN" identifier  "(" [expression ("," expression)*] ")"    -> stmt_proc_run
        | "RND" identifier expression expression        -> stmt_rnd
        | "IF" expression "THEN" statement "ELSE" statement -> stmt_if
        | "EMIT" expression                             -> stmt_emit
    
    # expressions
    
    ?expression: conditional
    
    ?conditional : comparison "?" comparison ":" conditional ->  conditional
        | comparison "?" conditional ":" conditional ->  conditional
        | comparison
    
    ?comparison : sum
        | sum "==" sum      -> comp_equal
        | sum "<" sum       -> comp_less
        | sum ">" sum       -> comp_more
    
    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div
        | product "//" atom  -> floordiv

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | "FUNC" conditional -> func
         | identifier "(" (conditional ("," conditional)*)* ")" -> func_call
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
    vars: MutableMapping[str, Value]
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


@dataclass
class StmtIf(Statement):
    condition: Identifier
    if_true: Statement
    if_false: Optional[Statement] = None


@dataclass
class StmtEmit(Statement):
    expression: Expression


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
        return ExprFuncCall(identifier, values)

    @staticmethod
    def add(a, b):
        return ExprBinaryOp(a, "+", b)

    @staticmethod
    def sub(a, b):
        return ExprBinaryOp(a, "-", b)

    @staticmethod
    def NAME(a: Token) -> Identifier:
        return IdentifierLiteral(a.value)

    @staticmethod
    def id_computed(expr: Expression) -> Identifier:
        return IdentifierComputed(expr)

    @staticmethod
    def mul(a, b):
        return ExprBinaryOp(a, "*", b)

    @staticmethod
    def div(a, b):
        return ExprBinaryOp(a, "/", b)

    @staticmethod
    def neg(n):
        return ExprUnaryOP(n, "-")

    @staticmethod
    def conditional(*args):
        return ExprConditional(*args)

    @staticmethod
    def comp_equal(left, right):
        return ExprComparisonEqual(left, right)

    @staticmethod
    def comp_less(left, right):
        return ExprComparisonLess(left, right)

    @staticmethod
    def comp_more(left, right):
        return ExprComparisonMore(left, right)

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

    @staticmethod
    def stmt_if(cond, if_true, if_false):
        return StmtIf(cond, if_true, if_false)

    @staticmethod
    def stmt_emit(expr):
        return StmtEmit(expr)


stmt_parser = Lark(grammar, parser='lalr', start='statement', transformer=Ast())
expr_parser = Lark(grammar, parser='lalr', start='expression', transformer=Ast())
stmt_parser_tree = Lark(grammar, parser='lalr', start='statement')
expr_parser_tree = Lark(grammar, parser='lalr', start='expression')


#


def get_literal_value(v: Value) -> str | float:
    match v:
        case ValueNumber(x):
            return x
        case ValueString(x):
            return x
        case _:
            raise Exception("wrong param")


def get_identifier_value(i: Identifier, env: Environment) -> str:
    match i:
        case IdentifierLiteral(x):
            return x
        case IdentifierComputed(x):
            print("ID "+repr(i),(evaluate_expression(x, env)).get_string())
            return (evaluate_expression(x, env)).get_string()
        case _:
            raise Exception("Wrong identifier"+repr(i))


def get_numerical_value(v: Value) -> float:
    match v:
        case ValueNumber(n):
            return n
        case _:
            return 0


def evaluate_expression(e: Expression, env: Environment) -> Value:
    match e:
        case ValueNumber(v):
            return ValueNumber(v)
        case ValueString(v):
            return ValueString(v)
        case ValueFunction(v):
            return ValueFunction(v)
        case ExprBinaryOp(left, op, right):
            from operator import sub, mul, truediv, floordiv
            ev_left = evaluate_expression(left, env)
            ev_right = evaluate_expression(right, env)
            match op:
                case "+":

                    match (ev_left, ev_right):
                        case (ValueNumber(ll), ValueNumber(rr)):
                            return ValueNumber(ll + rr)
                        case _:
                            return ValueString(ev_left.get_string() + ev_right.get_string())

                case "-":
                    binary = sub
                case "*":
                    binary = mul
                case "/":
                    binary = truediv
                case "//":
                    binary = floordiv
                case _:
                    raise Exception("Unknown binary: " + op)

            return ValueNumber(binary(ev_left.get_number(), ev_right.get_number()))
        case ExpressionVar(i):

            return env.vars[get_identifier_value(i, env)]
        case ExprUnaryOP(left, op):
            match op:
                case "-":
                    return ValueNumber(-evaluate_expression(left, env).get_number())
                case "!":
                    if evaluate_expression(left, env).get_number():
                        return ValueNumber(0)
                    else:
                        return ValueNumber(1)
                case _:
                    raise Exception("Unknown Unary" + op)
        case ExprFuncCall(i, args):
            func = env.vars[get_identifier_value(i, env)]
            if isinstance(func, ValueFunction):
                new_env = environment_with_args(env, args)

                return evaluate_expression(func.value, new_env)

            raise Exception
        case ExprComparisonEqual(left, right):
            if evaluate_expression(left, env) == evaluate_expression(right, env):
                return ValueNumber(1)
            else:
                return ValueNumber(0)
        case ExprComparisonLess(left, right):
            if evaluate_expression(left, env).get_number() < evaluate_expression(right, env).get_number():
                return ValueNumber(1)
            else:
                return ValueNumber(0)
        case ExprComparisonMore(left, right):
            if evaluate_expression(left, env).get_number() > evaluate_expression(right, env).get_number():
                return ValueNumber(1)
            else:
                return ValueNumber(0)

        case ExprConditional(cond, if_true, if_false):
            ec = evaluate_expression(cond, env)
            if ec == ValueNumber(0):
                return evaluate_expression(if_false, env)
            else:
                return evaluate_expression(if_true, env)
        case _:
            raise Exception("Can't handle EXPR ", e)


def environment_with_args(env: Environment, args: Sequence[ExprLiteralValue]) -> Environment:
    new_env = deepcopy(env)
    for i, arg in enumerate(args):
        new_env.vars['_' + str(i)] = evaluate_expression(arg, env)
    return new_env


def run_statement(s: Statement, env: Environment, emit_handler: Callable[[str], None] = lambda x: None) -> None:
    match s:
        case StmtPrint(e):
            res = evaluate_expression(e, env)
            env.output.append(res.get_string())
            print("PRINT ", evaluate_expression(e, env))
        case StmtBind(i, e):
            v = evaluate_expression(e, env)
            env.vars[get_identifier_value(i, env)] = v
        case StmtBlock(ss):
            for st in ss:
                run_statement(st, env, emit_handler)
        case StmtProcDef(i, stmt):
            env.procedures[get_identifier_value(i, env)] = stmt
        case StmtProcRun(i, args):
            stmt = env.procedures[get_identifier_value(i, env)]
            for i, arg in enumerate(args):
                env.vars['_' + str(i)] = evaluate_expression(arg, env)

            run_statement(stmt, env, emit_handler)
        case StmtRnd(i, minVal, maxVal):
            min_v = get_numerical_value(evaluate_expression(minVal, env))
            max_v = get_numerical_value(evaluate_expression(maxVal, env))

            env.vars[get_identifier_value(i, env)] = ValueNumber(random.randint(floor(min_v), floor(max_v)))
        case StmtIf(cond, if_true, if_false):
            if evaluate_expression(cond, env).get_number():
                run_statement(if_true, env, emit_handler)
            else:
                if if_false is None:
                    pass
                else:
                    run_statement(if_false, env, emit_handler)
        case StmtEmit(expression):
            emit_handler(evaluate_expression(expression, env).get_string())
        case _:
            raise Exception("unknown statement", s)


def test_emit_handler(s: str) -> None:
    print("EMITTED", s)


def test():
    env: Environment = Environment({'abc': ValueNumber(66)
                                       , 'fun1': ValueFunction(
            ExprBinaryOp(ExpressionVar(IdentifierLiteral('_0')), '+',
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
    print(parsed)
    s1 = """{ g=FUNC _0 + _1;
    PROC janowa { PRINT _0 ; a66=5 };
    RUN janowa("X");
     PRINT g(5,a66); PRINT g(5,-6)==10 ? "Jan" : "Test" ;
     a66=a66+2;
     PRINT a66;
     RND xx 2 10;
     PRINT xx;
     PRINT g;
     IF xx<8 THEN PRINT "XX"+xx ELSE PRINT "YYY"+xx;
     EMIT xx
     }"""
    sp1 = stmt_parser.parse(s1)
    print(sp1)
    run_statement(sp1, env, test_emit_handler)
    pprint(env)
    # print(parsed2.pretty())
    # s1 = stmt_parser.parse()


def main():
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        print(expr_parser.parse(s))


if __name__ == '__main__':
    test()
    # main()
