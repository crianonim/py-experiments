import dataclasses
import json
import random
from dataclasses import dataclass
from pprint import pprint

surnames = [
    "Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davies", "Robinson", "Wright", "Thomson",
    "Evans"
]

boy_names = [
    "Noah", "Oliver", "George", "Arthur", "Muhammad", "Leo", "Harry", "Oscar", "Archie", "Henry"
]

girl_names = ["Olivia", "Amelia", "Isla", "Ava", "Ivy", "Freya", "Lily", "Florence", "Mia", "Willow"]

polite_messages = [
    "Great to hear from you!",
    "Thanks for the update!",
    "I appreciate your quick response.",
    "Thanks for getting back to me.",
    "Thanks for getting in touch!",
    "Thank you for your help.",
    "Thanks for the fast response.",
    "I hope this email finds you well",
]

first_names = boy_names + girl_names


def generate_number():
    a = 0
    while True:
        a = a + 1
        yield a


def get_polite_message():
    return random.choice(polite_messages)


def generate_name():
    return random.choice(first_names) + " " + random.choice(surnames)
@dataclass
class Message:
    sender: str
    to: str
    content: str

if __name__ == '__main__':
    for x in range(10):
        m=Message(generate_name(),generate_name(),get_polite_message())
        j=json.dumps(dataclasses.asdict(m))
        pprint(j)

