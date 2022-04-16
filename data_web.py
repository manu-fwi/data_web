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
        db_thread.updates[request.sid]=[comm_queue,{updates_ids:[],graphs_desc:[]}]

    th = socketio.start_background_task(db_thread.background_thread,request.sid)
    emit("connected");

#event received to indicate which streams the page will make graphs from and the max number of data points used
#data_request event json data format (careful its a stringified json):
# { "graph_name":"name","streams":[{"data":"stream_name[field] (see data_xy format)","nb_data_init":10]]}

@socketio.event
def data_request(js_arg):
    log("Data request for data_streams: "+str(js_arg))

    #first get all streams names from the json
    #and build a list of triples (stream name, stream id, limit number of data points)

    streams_names = []
    names_limits_lst=[]
    for l in js_arg["streams"]:
        str_name = l["data"][:l["data"].find("[")]
        streams_names.append(str_name)
        names_limits_lst.append({"name":str_name,"id":0,"nb_data_init":int(l["nb_data_init"])})

    #fill in the ids in names_limits_lst
    lst = models.db_data_streams_head.query.filter(models.db_data_streams_head.name.in_(streams_names)).all()
    for l in lst:
        for nl in names_limits_lst:
            if nl["name"]==l.name:
                nl["id"]=l.id
    #FIXME: add detection of streams that have not been found
    
    #Now send first batch of data corresponding to all data streams using the "init" message to the queue
    db_thread.updates[request.sid][0].put(("init",names_limits_lst))
    #Set the list of data_streams_head ids a
    with threads_lock:
        # add streams_ids that are not yet present in the list of interesting updates
        for l in lst:
            if l.id not in db_thread.updates[request.sid][1]["updates_ids"]:
                db_thread.updates[request.sid][1]["updates_ids"].append(l.id)
            #add the graph description
            db_thread.updates[request.sid][1]["graphs_desc"].append(js_arg)

    log("data request lst="+str([l.id for l in lst]))

if __name__ == '__main__':
    #Start DB thread
    socketio.start_background_task(db_thread.db_thread,socketio)
    #Start application
    socketio.run(app,host="192.168.8.200")
