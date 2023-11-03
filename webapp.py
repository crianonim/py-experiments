# TO RUN: python -m flask --app webapp run

from flask import Flask, request
import monsters
app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/monsters/<index>")
def monster_route(index):
    print(request.headers)
    m = list(filter(lambda m: m.index == index, monsters.monsters))[0]
    return f'''<div>{str(m)}<div>
    <div>{str(request.headers)}<div>
    '''


@app.route("/monsters")
def monsters_route():
    return "<ul>"+("".join(map(lambda m: f'<li><a href="monsters/{m.index}">{m.value}</li>', monsters.monsters)))+ "</ul>"
