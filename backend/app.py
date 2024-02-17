import secrets

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
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

db = SQLAlchemy(app)

playground = Playground()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)

    def __repr__(self):
        return {"username": self.username, "color": self.color, "role": self.role}

    @classmethod
    def create_user(cls, username, role):
        token = secrets.token_hex(24)
        user = cls(username=username, token=token, role=role, color="neutral")
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def find_by_token(cls, token):
        return cls.query.filter_by(token=token).first()


with app.app_context():
    db.create_all()


def authentication_required(role=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            token = flask.request.headers.get("Authorization").split(" ")[-1]
            user = User.find_by_token(token)
            if not user:
                user = User.create_user(playground.get_nickname(), "guest")
                emit("grantToken", {"token": user.token, "name": user.username})
                logger.info("New user %s connected", user.username)
                join_room("guests")
            logger.info("User %s connected", user.username)

            if role and user.role not in role:
                logger.warning(
                    "User %s does not have the required role to access this functionality",
                    user.username,
                )
                return

            emit("updateGameData", playground.codenames)
            if user.role == "spymaster":
                emit("spymasterGameData", playground.codenames, to="spymaster")
            kwargs["user"] = user
            return func(*args, **kwargs)

        return wrapper

    return decorator


@socketio.on("connect")
@authentication_required
def handle_connect():
    join_room("guests")


@socketio.on("restartGame")
@authentication_required(role=["players", "spymaster"])
def handle_restart():
    logger.info("Client requested game restart")
    playground.restart_game()
    emit("restartedGameData", playground.codenames)


@socketio.on("clickAction")
@authentication_required(role=["players"])
def handle_word_click(word):
    logger.info("Client clicked word")
    color = playground.trigger_click(word)
    emit("clickedAction", {"word": word, "color": color})


@socketio.on("becomePlayer")
@authentication_required(role=["players", "guest"])
def become_player(color, **kwargs):
    user: User = kwargs["user"]
    leave_room("guest")
    join_room("players")
    user.role = "players"
    user.color = color
    db.session.commit()
    emit("newPlayer", kwargs["user"])


@socketio.on("becomeSpymaster")
@authentication_required(role=["players"])
def become_spymaster(**kwargs):
    user: User = kwargs["user"]
    user.role = "spymaster"
    db.session.commit()
    leave_room("players")
    join_room("spymaster")
    emit("newSpymaster", kwargs["user"])


@socketio.on("endGame")
def handle_endgame():
    emit("gameEnded")
