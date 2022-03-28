from app.config import log
from app import models
from flask_sqlalchemy import inspect


def exists_graph(name):
    res=models.db_graph.query.filter(models.db_graph.name==name).first()
    return res==None
    
def add_new_graph(name,graph_type,
                  data_xy,options="",rect=""):
    graph_types=["lines","bars","gauge","pie chart"]
    graph = models.db_graph()
    graph.name = name
    graph.graph_type = graph_types[graph_type]
    graph.rect=rect
    graph.data_xy = data_xy
    graph.options = options
    models.db.session.add(graph)
    models.db.session.commit()
    log("added graph "+name)
