from app import *
from datetime import datetime,timezone
from app import message
from app import config
from app.config import log
import sys

from flask_socketio import SocketIO

socketio = SocketIO(app)

if __name__ == '__main__':
    socketio.run(app)
