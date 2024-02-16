import logging

from flask import Flask

from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

import os


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", "postgresql:///codenames"
)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)


with app.app_context():
    db.create_all()
