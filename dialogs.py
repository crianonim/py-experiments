import json
from collections.abc import Sequence, Mapping
from dataclasses import dataclass
from functools import partial
from pprint import pprint
import screept
from typing import Optional


def parse_value(d) -> screept.Value:
    match d:

        case {"type": "number", "value": x}:
            return screept.ValueNumber(x)
        case {"type": "text", "value": x}:
            return screept.ValueString(x)
        case {"type": "func", "value": x}:
            return screept.ValueFunction(parse_expression(x))
        case _:
            raise Exception("Parse Error Value: " + repr(d))


def parse_identifier(d) -> screept.Identifier:
    match d:
        case {"type": 'literal', 'value': v}:
            return screept.IdentifierLiteral(v)
        case {'type': 'computed', 'value': v}:
            return screept.IdentifierComputed(parse_expression(v))
        case _:
            raise Exception("Parse Error Identifier: " + repr(d))


def parse_expression(d):
    match d:
        case {'type': 'binary_op', 'op': op, 'x': left, 'y': right}:
            match op:
                case "==":
                    return screept.ExprComparisonEqual(parse_expression(left), parse_expression(right))
                case "<":
                    return screept.ExprComparisonLess(parse_expression(left), parse_expression(right))
                case ">":
                    return screept.ExprComparisonMore(parse_expression(left), parse_expression(right))
                case _:
                    return screept.ExprBinaryOp(parse_expression(left), op, parse_expression(right))
        case {'type': 'condition', 'condition': expr, 'onFalse': on_false, 'onTrue': on_true}:
            return screept.ExprConditional(parse_expression(expr), parse_expression(on_true),
                                           parse_expression(on_false))
        case {'type': 'var', 'identifier': identifier}:
            return screept.ExpressionVar(parse_identifier(identifier))
        case {'type': 'literal', 'value': value}:
            return parse_value(value)
        case {'type': 'fun_call', 'identifier': identifier, 'args': args}:
            return screept.ExprFuncCall(parse_identifier(identifier), list(map(parse_expression, args)))
        case {'type': 'parens', 'expression': expr}:
            return parse_expression(expr)
        case {'type': 'unary_op', 'op': op, 'x': x}:
            return screept.ExprUnaryOP(parse_expression(x), op)
        # case
        case _:
            raise Exception("Parse Error Expression: " + repr(d))


def parse_statement(x):
    match (x):
        case {'type': 'block', 'statements': stmts}:
            return screept.StmtBlock(list(map(parse_statement, stmts)))
        case {'type': 'bind', 'identifier': identifier, 'value': value}:
            return screept.StmtBind(parse_identifier(identifier), parse_expression(value))
        case {'type': 'proc_run', 'identifier': identifier, 'args': args}:
            return screept.StmtProcRun(parse_identifier(identifier), list(map(parse_expression, args)))
        case {'type': 'print', 'value': value}:
            return screept.StmtPrint(parse_expression(value))
        case {'type': 'random', 'identifier': identifier, 'from': from_value, 'to': to_value}:
            return screept.StmtRnd(parse_identifier(identifier), parse_expression(from_value),
                                   parse_expression(to_value))
        case {'type': 'if', 'condition': condition, 'thenStatement': thenStatement}:
            if 'elseStatement' in x:
                return screept.StmtIf(parse_expression(condition), parse_statement(thenStatement),
                                      parse_statement(x['elseStatement']))
            else:
                return screept.StmtIf(parse_expression(condition), parse_statement(thenStatement))
        case _:
            raise Exception("Parse Error Statement: " + repr(x))


def process_var(v):
    name, value = v
    return name, parse_value(value)


def process_procedure(v):
    name, value = v
    return name, parse_statement(value)


@dataclass
class GameState:
    environment: screept.Environment
    dialog_stack: list[str]


class DialogAction:
    pass


@dataclass
class DAGoBack(DialogAction):
    pass


@dataclass
class DAGoDialog(DialogAction):
    dialog_id: str


@dataclass
class DAScreept(DialogAction):
    value: screept.Statement


@dataclass
class DAConditional(DialogAction):
    condition: screept.Expression
    then_actions: Sequence[DialogAction]
    else_actions: Sequence[DialogAction]


@dataclass
class DAMessage(DialogAction):
    value: screept.Expression


@dataclass
class DABlock(DialogAction):
    actions: Sequence[DialogAction]


@dataclass
class Option:
    id: str
    text: screept.Expression
    actions: Sequence[DialogAction]
    condition: Optional[screept.Expression] = None


@dataclass
class Dialog:
    id: str
    text: screept.Expression
    options: Sequence[Option]


@dataclass
class GameDefinition:
    game_state: GameState
    dialogs: Mapping[str, Dialog]


def parse_action(x) -> DialogAction:
    match x:
        case {'type': 'go back'}:
            return DAGoBack()
        case {'type': 'go_dialog', 'destination': destination}:
            return DAGoDialog(destination)
        case {'type': 'screept', 'value': value}:
            return DAScreept(parse_statement(value))
        case {'type': 'conditional', 'if': condition, 'then': then_actions, 'else': else_actions}:
            return DAConditional(parse_expression(condition), list(map(parse_action, then_actions)),
                                 list(map(parse_action, else_actions)))
        case {'type': 'msg', 'value': value}:
            return DAMessage(parse_expression(value))
        case {'type': 'block', 'actions': actions}:
            return DABlock(list(map(parse_action, actions)))
        case _:
            pprint(x)
            raise Exception("CANT" + x)


def parse_option(x) -> Option:
    if 'condition' in x:
        condition = (parse_expression(x['condition']))
    else:
        condition = None
    text = parse_expression(x['text'])
    actions = list(map(parse_action, x['actions']))
    return Option(x['id'], text, actions, condition)


def parse_dialog(x) -> Dialog:
    return Dialog(x['id'], parse_expression(x['text']), list(map(parse_option, x['options'])))


def load_game(title: str) -> GameDefinition:
    with open("data/" + title + ".json", "r") as f:
        data = json.load(f)
        game_state = data['gameState']
        # print(data.keys())
        env = game_state['screeptEnv']
        dialog_stack: list[str] = game_state['dialogStack']
        # print(data['dialogs'])
        dialogs = [(x[0], parse_dialog(x[1])) for x in data['dialogs'].items()]
        # pprint(dialogs)
        variables = (dict(map(process_var, env['vars'].items())))
        procedures = (dict(map(process_procedure, env['procedures'].items())))
        # pprint(procedures)
        environment: screept.Environment = screept.Environment(variables, procedures, [])
        # pprint(environment)

        return GameDefinition(GameState(environment, dialog_stack), dict(dialogs))


def get_split_string_on_nl(expr: screept.Expression, env: screept.Environment) -> list[str]:
    return screept.evaluate_expression(expr, env).get_string().split('<nl>')


def get_status_line(env: screept.Environment):
    if '__statusLine' in env.vars:
        parsed = screept.expr_parser.parse('__statusLine()')
        return screept.evaluate_expression(parsed, env).get_string()
    else:
        return ""


def is_option_visible(env: screept.Environment, option: Option) -> bool:
    match option.condition:
        case None:
            return True
        case ex:
            return screept.evaluate_expression(ex, env).get_number() != 0


def get_visible_options(options: Sequence[Option], env: screept.Environment) -> Sequence[Option]:
    return list(filter(partial(is_option_visible, env), options))


def show_option(option: Option, env: screept.Environment):
    text = screept.evaluate_expression(option.text, env).get_string()
    return text


def show_dialog(dialogs: Mapping[str, Dialog], dialog_id: str, env: screept.Environment):
    dialog = dialogs[dialog_id]
    # pprint(dialog)
    status_line = get_status_line(env)
    if status_line:
        print(status_line)
    print("\n".join(get_split_string_on_nl(dialog.text, env)))
    visible_options = get_visible_options(dialog.options, env)
    for i, opt in enumerate(visible_options):
        print(i + 1, show_option(opt, env))

    # pprint(env.vars)


def execute_action(game: GameDefinition, action: DialogAction):
    env = game.game_state.environment
    match action:
        case DAGoDialog(dialog_id):
            game.game_state.dialog_stack.insert(0, dialog_id)
        case DAGoBack():
            game.game_state.dialog_stack.pop(0)
        case DAScreept(value):
            screept.run_statement(value, env)
        case DAMessage(value):
            print("MESSAGE:")
            print(screept.evaluate_expression(value, env).get_string())
        case DAConditional(condition, then_actions, else_actions):
            if screept.evaluate_expression(condition, env).get_number():
                for a in then_actions:
                    execute_action(game, a)
            else:
                for a in else_actions:
                    execute_action(game, a)
        case _:
            pprint(action)
            raise Exception("NO handler for ACTION" + repr(action))


def loop(gd):
    dialog = gd.dialogs[gd.game_state.dialog_stack[0]]
    show_dialog(gd.dialogs, gd.game_state.dialog_stack[0],
                gd.game_state.environment)
    selected = input("Choose option")
    try:
        opt_no = int(selected)
        option = get_visible_options(dialog.options, gd.game_state.environment)[opt_no - 1]


    except:
        loop(gd)
    else:
        pprint(option)
        for action in option.actions:
            try:
                execute_action(gd, action)
            except Exception as e:
                print("Action Error: "+str(e))
                pprint(gd.game_state.environment)
        loop(gd)


if __name__ == "__main__":
    # game_definition = load_game("fable")
    game_definition = load_game("customGame")
    loop(game_definition)
    # show_dialog(game_definition.dialogs, game_definition.game_state.dialog_stack[0],
    #             game_definition.game_state.environment)
