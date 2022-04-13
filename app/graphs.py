from app.config import log
from app import models
from flask_sqlalchemy import inspect

graph_types = ("lines","bars","gauge","pie chart")

def exists_graph(name):
    res=models.db_graph.query.filter(models.db_graph.name==name).first()
    return res==None

# help function to build the data_xy string from the db_data_stream_head
# object and the field name
# if field name is None, this will either build the data_xy to describe
# the date_time field if date_t is True, otherwise it will build the data_xy
# to describe the first non-date field

def build_data_xy(data_str_head,field=None,date_t=False):
    if field is not None:
        return data_str_head.name+"['"+field+"']"
    else:
        if date_t:
            # use the date_time field
            return data_str_head.name+"[date_time]"
        else:
            # find first non-date field
            if data_str_head.stream_format == "VALUE":
                # just one value field
                return data_str_head.name+"[VALUE]"
            elif "CSV" in data_str_head.stream_format:
                # CSV formatted data stream
                # get rid of the date format
                l1=data_str_head.fields.split('"')
                if len(l1[0])>0:
                    res = l1[0][:l1[0].find(',')]
                else:
                    pos = l1[2][1:].find(',')
                    if pos==-1:
                        pos = len(l1[2])
                    res=l1[2][:pos]
                print("name['"+res+"']")
                return "name['"+res+"']"
    
def add_new_graph(name,graph_type,
                  data_xy,options="",rect=""):
    graph = models.db_graph()
    graph.name = name
    graph.graph_type = graph_types[graph_type]
    graph.rect=rect
    graph.data_xy = data_xy
    graph.options = options
    models.db.session.add(graph)
    models.db.session.commit()
    log("added graph "+name)
