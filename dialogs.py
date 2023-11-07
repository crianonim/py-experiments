import json
from collections.abc import Sequence
from dataclasses import dataclass
from pprint import pprint
import screept

def parse_value(d)->screept.Value:
    match (d):

        case {"type": "number", "value": x}:
            return screept.ValueNumber(x)
        case {"type": "text", "value": x}:
            return screept.ValueString(x)
        case {"type": "func", "value": x}:
            return screept.ValueFunction(parse_expression(x))
        case _ :
            raise Exception("Can't parse Value",d)

def parse_identifier(d)->screept.Identifier:
    match (d):
        case {"type": 'literal', 'value': v}:
            return screept.IdentifierLiteral(v)


def parse_expression(d):
    match (d):
        case {'type':'binary_op','op':op,'x':left,'y':right}:
            return screept.ExprBinaryOp(parse_expression(left),op,parse_expression(right))
        case {'type': 'conditon', 'condition': expr, 'onFalse': on_false, 'onTrue':on_true}:
            return screept.ExprConditional(parse_expression(expr),parse_expression(on_true),parse_expression(on_false))
        case {'type':'var', 'identifier': identifier}:
            return screept.ExpressionVar(parse_identifier(identifier))
        case {'type':'literal','value':value}:
            return parse_value(value)
        case {'type':'fun_call','identifier':identifier,'args':args}:
            return screept.ExprFuncCall(parse_identifier(identifier),list(map(parse_expression,args)))
        case {'type':'parens', 'expression':expr}:
            return  parse_expression(expr)
        # case
        case _:
            pprint(d)
            raise Exception("EXPR",d)



def process_var(v):
    name,value = v
    return (name,parse_value(value))

def load_game(title: str):
    with open("data/" + title + ".json", "r") as f:
        data = json.load(f)
        game_state=data['gameState']
        env=game_state['screeptEnv']
        vars=(dict(map(process_var,env['vars'].items())))
        pprint(vars)
        return data


if __name__ == "__main__":
    # load_game("fable")
    load_game("customGame")
