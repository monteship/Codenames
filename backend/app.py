from typing import Optional, List

from flask import Flask, jsonify
import random
from flask_cors import CORS
from flask_socketio import SocketIO

from config import UKRAINIAN_WORDS

app = Flask(__name__)
app.config["SECRET_KEY"] = "vnkdjnfjknfl1232#"
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

word_list = UKRAINIAN_WORDS

codenames: Optional[List[dict]] = []


class RandomCodeNameGenerator:
    def __init__(self, codenames_list):
        self.codenames = set(codenames_list)

    def generate(self):
        if not self.codenames:
            raise ValueError("No more unique words available.")

        word = random.choice(list(self.codenames))
        self.codenames.remove(word)
        return word


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    if not codenames:
        restart_game()
    socketio.emit("codenames", {"data": codenames})


@socketio.on("getGameData")
def handle_get_game_data():
    print("Client request data")
    socketio.emit("gameData", codenames)


@socketio.on("clicked")
def handle_word_click(name):
    global codenames
    color = "white"
    for word in codenames:
        if word["word"] == name:
            word["clicked"] = True
            color = word["color"]
            break
    socketio.emit("updateRender", {"data": {"word": name, "color": color}})


@socketio.on("restart")
def handle_restart():
    print("Client requested game restart")
    restart_game()
    socketio.emit("gameData", codenames)


@app.route("/", methods=["GET"])
def get_codenames():
    global codenames
    if codenames is None:
        restart_game()
    # return jsonify(codenames)
    socketio.emit("gameData", codenames)


def restart_game():
    global codenames
    codenames = []

    name_generator = RandomCodeNameGenerator(word_list)
    team_words_quantity = [8, 9]
    random.shuffle(team_words_quantity)

    for color, quantity in zip(["blue", "red"], team_words_quantity):
        codenames.extend(
            [
                dict(word=name_generator.generate(), color=color, clicked=False)
                for _ in range(0, quantity)
            ]
        )

    codenames.extend(
        [
            dict(word=name_generator.generate(), color="yellow", clicked=False)
            for _ in range(7)
        ]
    )

    codenames.append(dict(word=name_generator.generate(), color="black", clicked=False))

    random.shuffle(codenames)

    socketio.emit("gameData", codenames)
    return jsonify(codenames)


if __name__ == "__main__":
    socketio.run(app)
