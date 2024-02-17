import secrets
from functools import wraps

import flask
from flask import Flask

from flask_cors import CORS


from flask_socketio import SocketIO


from flask_socketio import join_room, emit, leave_room
import logging

from flask_sqlalchemy import SQLAlchemy

from playground import Playground

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///codenames.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

db = SQLAlchemy(app)

playground = Playground()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(20), nullable=False, default="grey")
    token = db.Column(db.String(255), nullable=False, unique=True)

    @classmethod
    def create_user(cls, username, role):
        token = secrets.token_hex(24)
        db_user = cls(username=username, token=token, role=role, color="grey")
        db.session.add(db_user)
        db.session.commit()
        return db_user

    @classmethod
    def find_by_token(cls, token):
        user = cls.query.filter_by(token=token).first()
        return user

    @classmethod
    def players(cls):
        users = cls.query.all()
        members = {
            "red": {"players": [], "spymaster": ["Spymaster"]},
            "blue": {"players": [], "spymaster": ["Spymaster"]},
            "grey": {"players": []},
        }
        for user in users:
            if not user.role == "all":
                members[user.color][user.role].append(user.username)
        return members

    def update_role(self, new_role):
        self.role = new_role
        db.session.commit()

    def update_color(self, new_color):
        self.color = new_color
        db.session.commit()

    def update_username(self, new_name):
        self.username = new_name
        db.session.commit()


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
                user = User.create_user(playground.get_nickname(), "players")
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
                emit("playersUpdate", User.players(), to="spymaster")
                emit("spymasterGameData", playground.codenames, to="spymaster")
            kwargs["user"] = user
            return func(*args, **kwargs)

        return decorated_function

    return decorator


@socketio.on("connect", namespace="/")
@authentication_required(role=None)
def handle_connect(user: User, auth=True):
    join_room("all")
    emit("playersUpdate", User.players(), to="all")
    emit("updateGameData", playground.codenames, to="all")


@socketio.on("disconnect", namespace="/")
@authentication_required(role=None)
def handle_disconnected(user: User):
    pass


@socketio.on("changeUsername", namespace="/")
@authentication_required(role=None)
def handle_change_username(new_username: str, user: User):
    user.update_username(new_username)


@socketio.on("restartGame", namespace="/")
@authentication_required(role=["players", "spymaster"])
def handle_restart(user: User):
    for user in User.query.all():
        user.update_role("all")
        user.update_color("grey")
    logger.info("Client requested game restart")
    playground.restart_game()
    emit("restartedGameData", playground.codenames, to="all")
    emit("playersUpdate", User.players(), to="all")


@socketio.on("restarted", namespace="/")
@authentication_required(role=None)
def restart(user: User):
    leave_room("players")
    leave_room("spymaster")
    join_room("all")


@socketio.on("clickAction", namespace="/")
@authentication_required(role=["players"])
def handle_word_click(word, user: User):
    logger.info("Client clicked word")
    color = playground.trigger_click(word)
    emit("clickedAction", {"word": word, "color": color}, to="all")


@socketio.on("joinPlayers", namespace="/")
@authentication_required(role=["players", "all"])
def become_player(color, user: User):
    join_room("players")
    user.update_role("players")
    user.update_color(color)
    emit("playersUpdate", User.players(), to="all")


@socketio.on("joinSpymaster", namespace="/")
@authentication_required(role=["players"])
def become_spymaster(user: User):
    user.update_role("spymaster")
    leave_room("players")
    join_room("spymaster")
    emit("playersUpdate", User.players(), to="all")
    emit("spymasterGameData", playground.codenames, to="spymaster")


@socketio.on("endGame", namespace="/")
def handle_endgame():
    emit("gameEnded")
