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

ukrainian_words = UKRAINIAN_WORDS
codenames: Optional[List[dict]] = []


class CodenameGenerator:
    def __init__(self, codenames_list):
        self.codenames = random.sample(codenames_list, 25)

    def gen(self):
        codename = random.choice(self.codenames)
        self.codenames.remove(codename)
        return codename

    def get_codenames(self, color: str, count: int):
        return [
            dict(word=self.gen(), color=color, clicked=False) for _ in range(0, count)
        ]


def initialize_game_data(restart: bool = False):
    global codenames
    if not codenames or restart:
        codenames = generate_game(ukrainian_words)
    return codenames


def generate_game(word_list):
    generator = CodenameGenerator(word_list)
    team_words_counts = [8, 9]
    random.shuffle(team_words_counts)

    new_codenames = []
    for color, count in zip(["blue", "red"], team_words_counts):
        new_codenames.extend(generator.get_codenames(color, count))

    new_codenames.extend(generator.get_codenames(color="yellow", count=6))
    new_codenames.extend(generator.get_codenames(color="balck", count=1))

    random.shuffle(new_codenames)

    return new_codenames


@socketio.on("connect")
def handle_connect():
    logger.info("Client connected")
    initialize_game_data()
    socketio.emit("updated", codenames)


@socketio.on("username")
def handle_username():
    logger.info("User connected")
    initialize_game_data()
    socketio.emit("updated", codenames)


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


@socketio.on("endGame")
def handle_endgame():
    socketio.emit("gameEnded")


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
