from backend.app import db


class Game(db.Model):
    __tablename__ = "session"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    initial_score_red = db.Column(db.Integer)
    score_red = db.Column(db.Integer)
    spymaster_red = db.Column(db.Text, nullable=False, default="")
    players_red = db.Column(db.Text, nullable=False, default="[]")

    initial_score_blue = db.Column(db.Integer)
    score_blue = db.Column(db.Integer)
    spymaster_blue = db.Column(db.Text, nullable=False, default="")
    players_blue = db.Column(db.Text, nullable=False, default="[]")

    codenames = db.relationship("Field", backref="session", lazy="dynamic")


class Codenames(db.Model):
    __tablename__ = "codenames"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(
        db.Integer, db.ForeignKey("games.id"), nullable=False, primary_key=True
    )
    name = db.Column(db.String(25), nullable=False)
    color = db.Column(db.String(6), nullable=False)
    clicked = db.Column(db.Boolean, nullable=False, default=False)
