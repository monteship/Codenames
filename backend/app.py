from flask import Flask

from flask_cors import CORS

from flask_socketio import SocketIO

import os

from flask_socketio import join_room, emit, leave_room
import logging

from flask_sqlalchemy import SQLAlchemy

from playground import Playground

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///codenames.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


with app.app_context():
    db.create_all()

playground = Playground()


def transmit_game():
    emit("guestGameData", playground.codenames)
    emit("playerGameData", playground.codenames, to="players")
    emit("spymasterGameData", playground.codenames, to="spymaster")


@socketio.on("connect")
def handle_connect():
    join_room("guests")
    logger.info("Client connected")
    transmit_game()


@socketio.on("restartGame")
def handle_restart():
    logger.info("Client requested game restart")
    playground.restart_game()
    emit("restartedGameData", playground.codenames)


@socketio.on("clickAction")
def handle_word_click(word):
    logger.info("Client clicked word")
    color = playground.trigger_click(word)
    emit("clickedAction", {"word": word, "color": color})
    transmit_game()


@socketio.on("becomePlayer")
def become_player(color):
    member = {"name": playground.get_nickname(), "color": color, "role": "players"}
    logger.info(f"Client become {color}_player")
    leave_room("guest")
    join_room("players")
    playground.add_member(**member)
    emit("memberJoined", member)
    transmit_game()


@socketio.on("becomeSpymaster")
def become_spymaster(color):
    spymaster = {"name": playground.get_nickname(), "color": color, "role": "spymaster"}
    logger.info(f"Client become {color}_spymaster")
    leave_room("players")
    join_room("spymaster")
    playground.add_member(**spymaster)
    emit("spymasterAppeared", spymaster)
    transmit_game()


@socketio.on("endGame")
def handle_endgame():
    emit("gameEnded")
