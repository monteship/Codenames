import logging
import os

from flask import Flask

from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

from backend.helper import WordsLoader, CodenameGenerator, Playground

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


playground = Playground()

RESPONSE = {
    "score": {
        "initial_score_blue": 0,
        "score_blue": 0,
        "initial_score_red": 0,
        "score_red": 0,
    },
    "codenames": [],
    "recent_click_action": {"word": "color"},
}


@socketio.on("connect")
def handle_connect():
    join_room("guests")
    logger.info("Client connected")
    emit("usersGameData", playground.codenames)
    emit("usersGameData", playground.codenames)
    emit("spymasterGameData", playground.codenames, to="spymaster")


@socketio.on("restartGame")
def handle_restart():
    logger.info("Client requested game restart")
    playground.restart_game()
    emit("restartedGameData", playground.codenames)


@socketio.on("endGame")
def handle_endgame():
    emit("gameEnded")


@socketio.on("clickAction")
def handle_word_click(word):
    logger.info("Client clicked word")
    color = playground.trigger_click(word)
    emit("usersGameData", playground.codenames)
    emit("clickedAction", {"word": word, "color": color})


@socketio.on("becomePlayer")
def become_player(color):
    member = {"name": playground.get_nickname(), "color": color, "role": "players"}
    logger.info(f"Client become {color}_player")
    leave_room("guest")
    join_room("players")
    playground.add_member(**member)
    emit("memberJoined", member)
    emit("usersGameData", playground.codenames)


@socketio.on("becomeSpymaster")
def become_spymaster(color):
    spymaster = {"name": playground.get_nickname(), "color": color, "role": "spymaster"}
    logger.info(f"Client become {color}_spymaster")
    leave_room("players")
    join_room("spymaster")
    playground.add_member(**spymaster)
    emit("spymasterAppeared", spymaster)
    emit("usersGameData", playground.codenames)
    emit("spymasterGameData", playground.codenames, to="spymaster")
