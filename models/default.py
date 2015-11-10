import json
import threading


def jsonify(status='success', **kwargs):
    d = dict()
    d['status'] = status
    for i in kwargs:
        d[i] = kwargs[i]
    return json.dumps(d)


def seconds_to_localtime(seconds):
    import time
    t = time.localtime(seconds)
    return "%i:%i:%i %i/%i/%i"%(t.tm_hour, t.tm_min, t.tm_sec, t.tm_mday, t.tm_mon, t.tm_year)


def network_name_from_id(netid):
    netlist = conn.networks()
    for i in netlist:
        if netid == i.id:
            return i.label
        pass
    pass


def convert_timezone(utctimestring, fmt="%Y-%m-%dT%H:%M:%SZ", timezone='Asia/Kolkata'):
    from datetime import datetime
    import pytz
    utc_time = datetime.strptime(utctimestring, fmt)
    utc_time_withtz = utc_time.replace(tzinfo=pytz.utc)
    localtime = utc_time_withtz.astimezone(pytz.timezone(timezone))
    return localtime.strftime(fmt)

    
class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
 
    def run(self):
        self._target(*self._args)

