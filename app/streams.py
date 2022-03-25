from app import models

#class used to pass around the values of a stream
class stream_values:
    def __init__(self,name,stream_id,limit,last_update = None):
        #self.data will be passed as JSON to the javascript of the web page
        self.data = {"name":name,"values":None,"dates_times":None}
        self.stream_id = stream_id
        self.last_update = last_update
        self.limit = limit

    #get last values (in date order) from the db for this stream
    #since_last_update=True to only take new values
    #only a maximum of nb_values will be loaded
    #It return the date_time of the last retrieved data
    
    def get_last_values_from_db(self,nb_values=0,since_last_update=True):
        if nb_values<0:
            nb_values = self.limit
        if self.last_update is None:
            since_last_update = True
        if since_last_update:
            datas = models.db_data_streams.query.filter(and_(models.db_data_streams.date_time>last_update,
                                                             models.db_data_streams.header_id==self.stream_id))\
                                                .order_by(models.db_data_streams.date_time.desc())\
                                                .limit(nb_values).all()
        else:
            datas = models.db_data_streams.query.filter(models.db_data_streams.stream_id==self.stream_id)\
                                                .order_by(models.db_data_streams.date_time.desc())\
                                                .limit(nb_values).all()
        if len(datas)==0:
            return None

        values = []
        dates = []
        #get values and date_times from the db objects
        for d in datas:
            values.append(d.value)
            #FIXME str for date_time
            dates.append(str(d.date_time))

        #put values and dates back in good order
        values.reverse()
        dates.reverse()
        self.data["values"] = values
        self.data["dates_times"]=dates
        
        return datas[0].date_time

