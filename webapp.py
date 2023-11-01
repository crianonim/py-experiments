# TO RUN: python -m flask --app webapp run

from flask import Flask
import monsters
app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/monsters/<index>")
def monster_route(index):
    m = list(filter(lambda m: m.index == index, monsters.monsters))[0]
    return str(m)


@app.route("/monsters")
def monsters_route():
    return "<ul>"+("".join(map(lambda m: f'<li><a href="monsters/{m.index}">{m.name}</li>', monsters.monsters)))+"</ul>"
