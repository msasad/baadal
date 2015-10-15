import json
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
