import logging
from typing import Optional, List

from flask import Flask
import random

from flask_cors import CORS
from flask_socketio import SocketIO

from config import UKRAINIAN_WORDS

app = Flask(__name__)
app.config["SECRET_KEY"] = "vnkdjnfjknfl1232#"
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def initialize_game_data(restart: bool = False):
    global codenames
    if codenames is None or restart:
        codenames = generate_game()
    return codenames


def generate_game():
    name_generator = RandomCodeNameGenerator(word_list)
    team_words_quantity = [8, 9]
    random.shuffle(team_words_quantity)

    new_codenames = []
    for color, quantity in zip(["blue", "red"], team_words_quantity):
        new_codenames.extend(
            [
                dict(word=name_generator.generate(), color=color, clicked=False)
                for _ in range(0, quantity)
            ]
        )

    new_codenames.extend(
        [
            dict(word=name_generator.generate(), color="yellow", clicked=False)
            for _ in range(7)
        ]
    )

    new_codenames.append(
        dict(word=name_generator.generate(), color="black", clicked=False)
    )

    random.shuffle(new_codenames)

    return new_codenames


@socketio.on("update")
def handle_connect():
    logger.info("Data update")
    initialize_game_data()
    socketio.emit("updated", codenames)


@socketio.on("restart")
def handle_restart():
    logger.info("Client requested game restart")
    initialize_game_data(restart=True)
    socketio.emit("restarted", codenames)


@socketio.on("click")
def handle_word_click(name):
    color = "white"
    for word in codenames:
        if word["word"] == name:
            word["clicked"] = True
            color = word["color"]
            break
    socketio.emit(
        "clicked",
        {
            "data": {
                "word": name,
                "color": color,
            }
        },
    )


