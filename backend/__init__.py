import logging

from flask import Flask

from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room

from backend.helper import WordsLoader, CodenameGenerator, Playground

app = Flask(__name__)
app.config["SECRET_KEY"] = "vnkdjnfjknfl1232#"
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


playground = Playground()


@socketio.on("connect")
def handle_connect():
    join_room("all")
    logger.info("Client connected")
    emit("updatedGameData", playground.codenames, to="all")


@socketio.on("restartGame")
def handle_restart():
    logger.info("Client requested game restart")
    playground.restart_game()
    emit("restartedGame", playground.codenames, to="all")


@socketio.on("endGame")
def handle_endgame():
    emit("gameEnded")


@socketio.on("joinTeam")
def handle_join_team(team):
    join_room(team)
    data = {"color": team, "name": playground.get_nickname()}
    emit("joinedTeam", data, to="all")
    emit("joinedTeamTrigger", data, to=team)


@socketio.on("clickAction")
def handle_word_click(word):
    logger.info("Client clicked word")
    color = playground.trigger_click(word)
    emit("clickedAction", {"word": word, "color": color}, to="all")


@socketio.on("becomeSpymaster")
def become_spymaster(color):
    join_room("spymaster")
    emit("spymaster", {"color": color, "name": playground.get_nickname()})
