import random
import secrets
from collections import defaultdict
from typing import Self

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from backend.helper import WordsLoader

words_loader = WordsLoader()

db = SQLAlchemy()


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    red_initial_score = db.Column(db.Integer, nullable=False, default=0)
    blue_initial_score = db.Column(db.Integer, nullable=False, default=0)
    red_score = db.Column(db.Integer, nullable=False, default=0)
    blue_score = db.Column(db.Integer, nullable=False, default=0)

    users = relationship("User", back_populates="game")
    codenames = relationship("Codename", back_populates="game")

    @classmethod
    def create_game(cls, game_name: str) -> "Game":
        game = cls(name=game_name)
        game.new_game()
        try:
            db.session.add(game)
            db.session.commit()
            return game
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def find_by_name(cls, name) -> Self:
        game = cls.query.filter_by(name=name).first()
        return game

    def new_game(self):
        self.clean_game()

        codenames = random.sample(words_loader.get["codenames"], 25)
        self.assign_teams(codenames)

    def clean_game(self):
        Codename.query.delete()

        self.red_initial_score = 0
        self.blue_initial_score = 0

        db.session.commit()

    def assign_teams(self, codenames: list):
        team_counts = [8, 9]
        random.shuffle(team_counts)
        team_counts = {
            "red": team_counts[0],
            "blue": team_counts[-1],
            "yellow": 7,
            "black": 1,
        }
        random.shuffle(codenames)

        indexes = list(range(1, 26))
        random.shuffle(indexes)
        index_iter = iter(indexes)

        for color, count in team_counts.items():
            team_words = codenames[:count]
            codenames = codenames[count:]
            for word in team_words:
                self.add_codename(word, color, next(index_iter))
        self.red_initial_score = team_counts["red"]
        self.blue_initial_score = team_counts["blue"]
        db.session.commit()

    def add_codename(self, name: str, color: str, index):
        """Add a codename to the game."""
        codename = Codename(id=index, name=name, color=color, game=self)
        db.session.add(codename)

    def get_game_data(self):
        red_score = Codename.query.filter_by(
            game_name=self.name, color="red", state=True
        ).count()
        blue_score = Codename.query.filter_by(
            game_name=self.name, color="blue", state=True
        ).count()

        return {
            "name": self.name,
            "red_initial_score": self.red_initial_score,
            "blue_initial_score": self.blue_initial_score,
            "red_score": red_score,
            "blue_score": blue_score,
            "codenames": [
                {
                    "name": codename.name,
                    "color": codename.color,
                    "state": codename.state,
                }
                for codename in self.codenames
            ],
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(20), nullable=False, default="grey")
    token = db.Column(db.String(255), nullable=False, unique=True)

    game_name = Column(db.String, ForeignKey("game.name"), default="default")
    game = relationship("Game", back_populates="users")

    @classmethod
    def create_user(cls, role: str) -> "User":
        """Create a new user and add it to the database."""
        token = secrets.token_hex(24)
        user = cls(
            username=words_loader.get_nickname(), token=token, role=role, color="grey"
        )
        try:
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def find_by_token(cls, token: str) -> "User":
        """Find a user by their token."""
        return cls.query.filter_by(token=token).first()

    @classmethod
    def get_players_by_color_and_role(cls) -> dict:
        """Get all players grouped by color and role."""
        players = defaultdict(lambda: defaultdict(list))

        for user in cls.query.filter(User.role != "all").all():
            players[user.color][user.role].append(user.username or "")

        return players

    def update_role(self, new_role: str) -> None:
        """Update the role of the user."""
        self.role = new_role
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def update_color(self, new_color: str) -> None:
        """Update the color of the user."""
        self.color = new_color
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def update_username(self, new_name: str) -> None:
        """Update the username of the user."""
        self.username = new_name
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class Codename(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    color = db.Column(db.String(25), nullable=False)  # color can't be unique
    state = db.Column(db.Boolean, nullable=False, default=False)
    game_name = db.Column(db.Integer, db.ForeignKey("game.name"))

    game = relationship("Game", back_populates="codenames")

    @classmethod
    def find_by_name(cls, name: str) -> "Codename":
        """Find a codename by its name."""
        return cls.query.filter_by(name=name).first()

    def update_state(self, new_state: bool) -> None:
        """Update the state of the codename."""
        self.state = new_state
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
