import os.path
from datetime import datetime,timezone

basedir = os.path.abspath(os.path.dirname(__file__))

def log(message):
    s = datetime.now(timezone.utc).strftime("%x %X")+":"+message
    log_file = Config.get_config("LOG_FILE")
    if log_file == "":
        print(s)
    else:
        with open(log_file,"a") as f:
            f.write(s+"\n")

class Config(object):
    #minimal set of config options
    default_config = {"DB_FILE":"sqlite:///test.db",
                      "LOG_FILE":"" }
    loaded_config = None
    
    SECRET_KEY = 'secret!'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:////opt/opt/prog/sources/mqtt_to_data_stream/mqtt_to_data_stream.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def load_config(cls,filename):
        if not os.path.isfile(filename):
            log('Config file, '+filename+' not found, using default config')
            return
        
        with open(filename) as file:
            line=file.readline()
            lst = line.split('=')
            if len(lst)!=2:
                log('Error reading config file, '+line+' is not of the form KEY = value')
            else:
                if cls.loaded_config is None:
                    cls.loaded_config = {}
                cls.loaded_config[lst[0]]=lst[1]
                #make sure we set the SqlAlchemy config var according to the config
                if lst[0]=='DB_FILE':
                    cls.SQLALCHEMY_DATABASE_URI='sqlite:///'+lst[1]

    @classmethod
    def get_config(cls,name):
        if cls.loaded_config is None or not name in cls.loaded_config:
            return cls.default_config[name]
        return cls.load_config[name]
