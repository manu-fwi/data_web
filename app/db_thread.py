from app.config import log
from app import models,socketio
from datetime import datetime,timezone
from collections import deque
from sqlalchemy import and_
import json

#dictionnary of sids <-> pair: (communication queue, list of data_stream_header name that are of interest for the client)
updates = {}
#last_update is a naive datetime because every datetime coming from the DB is in UTC
#FIXME: global last_update does not seem right
last_update = datetime.fromtimestamp(0)
log("original update="+str(last_update))

# Iterate through all updates and return those corresponding to sid
# that is those with an header present in updates[sid][1]
# the return value is a list of list: each element is a list of updates all corresponding to the same header id

def update_of_interest(sid,update_lst_orig):
    result = []
    #make a copy as we will modify it
    update_lst = update_lst_orig[:]
    log("update_of_interest:"+str(updates[sid]))
    for stream_id in updates[sid][1]:
        empty = True
        to_delete = deque()
        for i in range(len(update_lst)):
            #retrieve the stream_id from the data_stream
            data_str = models.db_data_streams.query\
                                             .filter(models.db_data_streams.id==update_lst[i].id)\
                                             .first()
            if data_str.header.id == stream_id:
                #add the index of the element to be deleted at the end
                to_delete.appendleft(i)
                if empty:
                    result.append([])
                    empty = False
                result[-1].append(update_lst[i])
        #prune update_lst of all the records already added to result
        for i in to_delete:
            update_lst.pop(i)
        if not empty:
            result[-1].reverse()
    for r in result:
        log("update of interest : "+str(r))
    return result
    
# Background thread checking if the DB has been updated

def get_new_updates():
    #query db_updates table for all updates after last_update in descending order
    new_up = models.db_updates.query.join(models.db_data_streams)\
                                    .filter(and_(models.db_updates.stream_id == models.db_data_streams.id,
                                                 models.db_data_streams.date_time>last_update))\
                                    .order_by(models.db_data_streams.date_time.desc()).all()
    log("get_new_update = "+str(new_up))
    return new_up

def db_thread(socketio):
    global last_update
    while True:
        new_updates = get_new_updates()
        if len(new_updates)>0:
            last_date = new_updates[0].data_stream.date_time
            for sid in updates:
                #build a list of all interesting updates for this sid
                up = update_of_interest(sid,new_updates)
                if len(up)>0:
                    #we have some interesting updates, send them to the queue
                    log("queuing for update "+str(up))
                    updates[sid][0].put(("update",up))
            #get last update time
            if last_date>last_update:
                last_update = last_date
            log("new last_update="+str(last_update))
        socketio.sleep(5)

def process_init(streams_lst,sid):
    global last_update
    log("Processing init message "+str(streams_lst))
    for str_name,stream_id,limit in streams_lst:
        #get last values (number is given by limit)
        #in case the request wants no data, we need to set the limit to 1
        #so we can still query to get the header_id
        query_limit=max(limit,1)
        values = models.db_data_streams.query.filter(models.db_data_streams.header_id==stream_id)\
                                             .order_by(models.db_data_streams.date_time.desc())\
                                             .limit(limit).all()

        #update last_update using the timestamp of the values
        if values[0].date_time>last_update:
            last_update = values[0].date_time

        if limit==0:
            #empty the values if limit was set to 0
            values=[]
        else:
            #We had to get the values in reverse order, re-order them
            values.reverse()

        log("emitting init "+str([v.value.split(',')[0] for v in values]))
        #FIXME: make sure we convert from the CSV/JSON format to the correct format for the Plotly plot
        socketio.emit("init",
                      {"data":{"name":str_name,
                               "values":[int(v.value.split(',')[0]) for v in values],
                               "dates_times":[v.value.split(',')[1] for v in values]}},
                      to=sid)

#process updates, lst is a list of list of updates see updates_of_interest
def process_updates(lst,sid):
    for up_lst in lst:
        #build list of values and corresponding dates from up_lst
        values = []
        dates = []
        for up in up_lst:
            data_str = models.db_data_streams.query\
                                             .filter(models.db_data_streams.id==up.stream_id)\
                                             .first()
            values.append(data_str.value)
            #FIXME str(date_time)!
            dates.append(str(data_str.date_time))
        #get stream name
        str_name=models.db_data_streams_head.query\
                                            .filter(models.db_data_streams_head.id==data_str.header_id)\
                                            .first().name
        for v in values:
            log("v="+v)
        log("emitting update : "+json.dumps({"data":{"name":str_name,
                                                     "values":[int(v.split(',')[0]) for v in values],
                                                     "dates_times":dates}}))
        socketio.emit("update",{"data":{"name":str_name,
                                        "values":[int(v.split(',')[0]) for v in values],
                                        "dates_times":dates}}, to=sid)

# Socketio thread
def background_thread(sid):

    while True:
        # wait on the queue to get the next update/init
        msg = updates[sid][0].get()
        if msg[0]=="update":
            log("Got update from queue, list="+str(msg[1]))
            process_updates(msg[1],sid)
        elif msg[0]=="init":
            log("Got init from queue, list="+str(msg[1]))
            process_init(msg[1],sid)
