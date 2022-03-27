from app.config import log
from app import models
from flask_sqlalchemy import inspect


def exists_graph(name):
    inspector = inspect(models.db.engine)
    if inspector.has_table("graphs"):
        res=models.db_graph.query.filter(models.db_graph.name==name).first()
        return res==None
    return False

def add_new_graph(name,graph_type,data_streams):
    pass
