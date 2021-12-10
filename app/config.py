import os.path
from datetime import datetime,timezone

def log(message):
    s = datetime.now(timezone.utc).strftime("%x %X")+":"+message
    log_file = config.get_config("LOG_FILE")
    if log_file == "":
        print(s)
    else:
        with open(log_file,"a") as f:
            f.write(s+"\n")

class config:
    #minimal set of config options
    default_config = {}
    loaded_config = None
    
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

    @classmethod
    def get_config(cls,name):
        if cls.loaded_config is None or not name in cls.loaded_config:
            return cls.default_config[name]
        return cls.load_config[name]
