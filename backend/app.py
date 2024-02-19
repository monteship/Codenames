import secrets
from functools import wraps

import flask
from flask import Flask

from flask_cors import CORS

from flask_socketio import SocketIO

from flask_socketio import join_room, emit, leave_room
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///codenames.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

from models import *

db.init_app(app)

with app.app_context():
    db.create_all()

    for _user in User.query.all():
        _user.update_role("all")
        _user.update_color("grey")


def authentication_required(role=None, auth=False):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            token = flask.request.headers.get("Authorization").split(" ")[-1]
            user = User.find_by_token(token)
            if not user:
                user = User.create_user("players")
                logger.info("New user %s connected", user.username)
                emit("auth", {"token": user.token, "username": user.username})
            if auth:
                emit("auth", {"token": user.token, "username": user.username})

            if role and user.role not in role:
                logger.warning(
                    "User %s does not have the required role to access this functionality",
                    user.username,
                )
                return
            if user.role == "spymaster":
                emit(
                    "playersUpdate",
                    User.get_players_by_color_and_role(),
                    to="spymaster",
                )
                emit(
                    "spymasterGameData",
                    Game.find_by_name(user.game_name).get_game_data(),
                    to="spymaster",
                )
            kwargs["user"] = user
            return func(*args, **kwargs)

        return decorated_function

    return decorator


@socketio.on("connect")
@authentication_required(role=None)
def handle_connect(user: User, auth=True):
    join_room("all")
    emit("playersUpdate", User.get_players_by_color_and_role(), to="all")
    game = Game.find_by_name(user.game_name)
    if not game:
        game = Game.create_game(user.game_name)
    emit("updateGameData", game.get_game_data(), to="all")


@socketio.on("disconnect")
@authentication_required(role=None)
def handle_disconnected(user: User):
    pass


@socketio.on("changeUsername")
@authentication_required(role=None)
def handle_change_username(new_username: str, user: User):
    user.update_username(new_username)
    emit("playersUpdate", User.get_players_by_color_and_role(), to="all")


@socketio.on("restartGame")
@authentication_required(role=["players", "spymaster"])
def handle_restart(user: User):
    for user in User.query.all():
        user.update_role("all")
        user.update_color("grey")
    logger.info("Client requested game restart")
    game = Game.find_by_name(user.game_name)
    game.new_game()
    emit("restartedGameData", game.get_game_data(), to="all")
    emit("playersUpdate", User.get_players_by_color_and_role(), to="all")


@socketio.on("restarted")
@authentication_required(role=None)
def restart(user: User):
    leave_room("players")
    leave_room("spymaster")
    join_room("all")


@socketio.on("clickAction")
@authentication_required(role=["players"])
def handle_word_click(word, user: User):
    logger.info("Client clicked word")
    codename = Codename.find_by_name(word)
    codename.update_state(True)
    game = Game.find_by_name(user.game_name)
    emit("updateGameData", game.get_game_data(), to="all")


@socketio.on("joinPlayers")
@authentication_required(role=["players", "all"])
def become_player(color, user: User):
    join_room("players")
    user.update_role("players")
    user.update_color(color)
    emit("playersUpdate", User.get_players_by_color_and_role(), to="all")


@socketio.on("joinSpymaster")
@authentication_required(role=["players"])
def become_spymaster(user: User):
    user.update_role("spymaster")
    leave_room("players")
    join_room("spymaster")
    emit("playersUpdate", User.get_players_by_color_and_role(), to="all")
    emit(
        "spymasterGameData",
        Game.find_by_name(user.game_name).get_game_data(),
        to="spymaster",
    )


@socketio.on("endGame")
def handle_endgame():
    emit("gameEnded")
