from datetime import datetime,timezone
import eventlet

from app import models,config,app,socketio,db_thread
from app.config import log
import sys
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO,emit

# Threading

threads_lock = Lock()

# Events handlers

# Connection event => Create a server thread to send updates to the connected client when needed
@socketio.event
def connect():
    log("Got a connection, sid="+str(request.sid))
    log("Starting socketio thread")

    #queue to communicate with the background thread checking for DB updates
    comm_queue = eventlet.Queue()

    #update dictionnary
    with threads_lock:
        db_thread.updates[request.sid]=[comm_queue,[]]

    th = socketio.start_background_task(db_thread.background_thread,request.sid)
    emit("connected");

#event received to indicate which streams the page will make graphs from and the max number of data points used
@socketio.event
def data_request(js_arg):
    log("Data request for data_streams: "+str(js_arg))
    streams_names = [l["name"] for l in js_arg["streams"]]
    lst = models.db_data_streams_head.query.filter(models.db_data_streams_head.name.in_(streams_names)).all()
    #build a list of couples (stream id, limit number of data points)
    names_limits_lst=[]
    for l in lst:
        for s in js_arg["streams"]:
            if s["name"]==l.name:
                names_limits_lst.append((l.name,l.id,s["limit"]))
    #FIXME: add detection of streams that have not been found
    
    #Now send first batch of data corresponding to all data streams using the "init" message to the queue
    db_thread.updates[request.sid][0].put(("init",names_limits_lst))
    #Set the list of data_streams_head ids
    with threads_lock:
        db_thread.updates[request.sid][1]=[l.id for l in lst]

    log("data request lst="+str([l.id for l in lst]))

if __name__ == '__main__':
    #Start DB thread
    socketio.start_background_task(db_thread.db_thread,socketio)
    #Start application
    socketio.run(app,host="192.168.8.200")
