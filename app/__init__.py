from app import config
from app.config import log

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from app import config
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap 

import sys

#first load config file (only argument possible on the command line)
if len(sys.argv)==2:
    #load config
    log("trying to load config file: "+sys.argv[1])
    config.Config.load_config(sys.argv[1])
else:
    #no argument or too many, try default config file
    config.Config.load_config("config.txt")

# Application object
app = Flask(__name__)
boot = Bootstrap(app)

#load app config
app.config.from_object(config.Config)
log("App config="+str(app.config))

#Start DB engine
db = SQLAlchemy(app,session_options={"expire_on_commit": False})
print("tables=",db.metadata)

#start socketio
socketio = SocketIO(app,async_mode="eventlet")

from app import models,routes
