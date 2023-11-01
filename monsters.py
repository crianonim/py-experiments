import json
from dataclasses import dataclass


@dataclass
class Monster:
    """Monster data Class"""
    index: str
    name: str
    type: str
    alignment: str

    def __str__(self) -> str:
        return self.name+" type: "+self.type+" alignment: "+self.alignment

# class Monster():
#     name: str
#     type: str
#     alignment: str

#     def __init__(self, dict):

#         self.name = dict["name"]
#         self.type = dict["type"]
#         self.alignment = dict["alignment"]

#     def __str__(self) -> str:
#         return self.name+" type: "+self.type+" alignment: "+self.alignment


def decode(dict):
    if "name" in dict and "type" in dict:
        # return Monster(dict)
        return Monster(dict["index"], dict["name"], dict["type"], dict["alignment"])


monsterFile = 'data/monsters.json'


def getMonsters() -> list[Monster]:

    with open(monsterFile, 'r') as f:
        return json.load(f, object_hook=decode)


def getNames(monsters: list[Monster]) -> list[str]:
    return list(map(lambda m: m.name, monsters))


monsters = getMonsters()
names = getNames(monsters)


def main():
    while True:
        command = input("Your command? ")
        try:
            n = int(command)
            print(monsters[n])
        except:
            if command == "q":
                break
            elif command == "l":
                for (i, name) in enumerate(names):
                    print(i, name)

            else:
                print(command, "not found", monsters)


if __name__ == "__main__":
    main()
