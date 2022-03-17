from app import db

# table that stores each data stream characteristics:
# name (string)
# format: VALUE to indicate just one value, JSON, or CSV for comma separated values
# the suffix -RECVTIME may be added to the formats JSON and CSV to indicate
# that we must add the time of reception (up to ms); this is implicitly done for the
# VALUE format
# fields: comma separated list of fields name
# for JSON and CSV format one field MUST BE "emission_datetime!format!timezone" indicating the time of emission (note the double quotes)
# only the emission_date and time field is enclosed in double quotes (")
#for CSV format: no comma can be present in the format fields and in the payload (that would mess up the parsing
#of the payload
# format being codified as for strptime function (no timezone must be included in the format)
# if no timezone is provided, UTC is assumed
# all times/dates will be stored in UTC

class db_data_streams_head(db.Model):
    __tablename__= "data_streams_head"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200),index=True)
    stream_format = db.Column(db.String(30))
    fields = db.Column(db.String(200))
    stream_values = db.relationship("db_data_streams", back_populates="header")

# Actual data streams
# header_id points to the header describing the data stream
# value is the string describing the value(s) depending on the corresponding header format
# the date_time field is taken from the date field of value if it exists
# otherwise it must be added on reception

class db_data_streams(db.Model):
    __tablename__= "data_streams"
    id = db.Column(db.Integer, primary_key=True)
    header_id = db.Column(db.Integer,db.ForeignKey('data_streams_head.id'))
    value = db.Column(db.String(300))
    date_time = db.Column(db.DateTime(),index=True,nullable=True)
    header = db.relationship('db_data_streams_head',foreign_keys=header_id,
                             back_populates = 'stream_values')

# Table holding updates (additions only) of the data streams
# Each record points to the data stream record that has been added
class db_updates(db.Model):
    __tablename__ = "updated_streams"
    id = db.Column(db.Integer, primary_key=True)
    stream_id = db.Column(db.Integer,db.ForeignKey('data_streams.id'))
    data_stream = db.relationship('db_data_streams',foreign_keys=stream_id)

# Dashboard related models

#association table to build a full dashboard
#a full dashboard has a name and is made from graphs

full_dashboards = db.Table('full_dashboards',
    db.Column('dashboard_id', db.Integer, db.ForeignKey('dashboards.id')),
    db.Column('graph_id', db.Integer, db.ForeignKey('graphs.id'))
)

#Dashboard
class db_dashboard(db.Model):
    __tablename__ = "dashboards"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200),index=True)
    graphs = db.relationship("db_graph",secondary=full_dashboards,lazy='subquery',
                             backref=db.backref('dashboards',lazy=True))

# describes a graph (what data feeds, type,...)
class db_graph(db.Model):
    __tablename__ = "graphs"
    id = db.Column(db.Integer, primary_key=True)
    #name: used to find the html object to put it into
    name = db.Column(db.String(50),index=True)
    #dashboard it belongs to
    dashboard_id = db.Column(db.Integer,db.ForeignKey('dashboards.id'))
    #Position and size in a string in x,y,w,h format
    #can be Null
    rect = db.Column(db.String(20))
    #data to describe the graph
    # graph_type: string, can be: lines FIXME
    graph_type = db.Column(db.String(50))
    # data_xy: json as a string {"x":data stream name,"y":[data stream names]}
    # data stream name is: "name[field]", if field is not present the first field which is not a date is taken
    data_xy = db.Column(db.String(200))
    # options: json as a string FIXME (axes, hover style,...)
    options = db.Column(db.String(300))

    #dashboards = db.relationship("dashboards",secondary=full_dashboards,lazy='subquery',
    #                             backref=db.backref('graphs',lazy=True))
