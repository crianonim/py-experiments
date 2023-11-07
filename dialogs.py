import json
from collections.abc import Sequence
from dataclasses import dataclass
from pprint import pprint
import screept


def parse_expression_json(d) -> screept.Expression | dict:
    match (d):
        case {"type": "number", "value": x}:
            return screept.ValueNumber(x)
        case {"type": "text", "value": x}:
            return screept.ValueString(x)

        case _:
            return d


def json_helper(d):
    if "type" in d:
        return parse_expression_json(d)
    else:
        return d


def load_game(title: str):
    with open("data/" + title + ".json", "r") as f:
        # data=json.load(f)
        data = json.load(f, object_hook=json_helper)

        # dialogs_data=data["dialogs"]
        # pprint(dialogs_data)
        pprint(data)
        return data


if __name__ == "__main__":
    # load_game("fable")
    load_game("customGame")
